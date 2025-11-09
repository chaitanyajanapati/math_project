import time
import re
from typing import Tuple, List
import sys
import os
from pathlib import Path

# Add repository-relative AI models path to system path so imports work when
# running the backend from inside the `mathai_backend` folder.
# math_service.py is at: <repo>/mathai_backend/app/utils/math_service.py
# repo root is parents[3]
PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "mathai_ai_models"
if MODEL_PATH.exists():
    # Insert at front so it takes precedence
    sys.path.insert(0, str(MODEL_PATH))
else:
    # Fallback to a home-directory-based path for backwards compatibility
    fallback = Path.home() / "mathai_ai_models"
    if str(fallback) not in sys.path:
        sys.path.insert(0, str(fallback))

from generate_math_question import generate_question, generate_hint, generate_solution
from app.utils.solver import solve_question as deterministic_solve

try:
    from progressive_hints import generate_progressive_hints
    PROGRESSIVE_HINTS_AVAILABLE = True
except ImportError:
    PROGRESSIVE_HINTS_AVAILABLE = False
    print("[MathAIService] Progressive hints module not available")

try:
    from solution_explainer import enhance_solution_steps
    SOLUTION_EXPLAINER_AVAILABLE = True
except ImportError:
    SOLUTION_EXPLAINER_AVAILABLE = False
    print("[MathAIService] Solution explainer module not available")

class MathAIService:
    def __init__(self):
        # Initialize any AI model configurations here
        # Simple in-memory cache for progressive hints (deterministic, safe to cache)
        self._hint_cache = {}
        self._cache_hits = 0
        self._cache_misses = 0

    # ------------------ Multiple Choice Support Helpers ------------------
    def generate_distractors(self, correct: str, topic: str, max_count: int = 3):
        """Generate smart distractor answers based on common mistakes and topic.
        Creates plausible wrong answers that reflect typical student errors.
        """
        if not correct:
            return []
        distractors = []
        base = correct.strip().replace(',', '')  # Remove commas for numeric comparison
        
        import random
        import math
        
        try:
            # Handle fractions
            if "/" in base and all(p.strip().replace('-','').isdigit() for p in base.split("/", 1)):
                parts = base.split("/", 1)
                num, den = parts[0].strip(), parts[1].strip()
                num_i, den_i = int(num), int(den)
                
                # Generate plausible fraction distractors (common mistakes)
                variations = [
                    f"{den_i}/{num_i}",  # Inverted fraction
                    f"{num_i + den_i}/{den_i}",  # Added numerator to numerator
                    f"{num_i}/{den_i + num_i}",  # Added numerator to denominator
                    f"{num_i * 2}/{den_i}",  # Doubled numerator
                    f"{num_i}/{den_i * 2}",  # Doubled denominator
                    f"{abs(num_i - den_i)}/{den_i}",  # Subtraction error
                ]
                
                # Also add decimal equivalents of wrong fractions
                for frac in variations[:3]:
                    try:
                        fn, fd = map(int, frac.split('/'))
                        if fd != 0:
                            decimal_val = fn / fd
                            variations.append(f"{decimal_val:.4f}".rstrip('0').rstrip('.'))
                    except:
                        pass
                
                distractors.extend(variations)
            else:
                # Try numeric float/integer
                val = float(base)
                is_integer = abs(val - round(val)) < 0.0001
                
                # Topic-specific distractor strategies
                if topic == "algebra":
                    # Common algebra mistakes: sign errors, wrong operations
                    variations = [
                        -val,  # Sign error
                        val * 2,  # Forgot to divide
                        val / 2 if val != 0 else 1,  # Divided instead of multiplied
                        val + 1,  # Off-by-one error
                        val - 1,
                    ]
                elif topic == "geometry":
                    # Common geometry mistakes: wrong formula, forgot π, radius vs diameter
                    variations = [
                        val * 2,  # Radius vs diameter confusion
                        val / 2 if val != 0 else 1,
                        val * 3.14 if abs(val) < 100 else val * 0.5,  # Forgot/added π
                        val ** 2 if abs(val) < 20 else val * 1.5,  # Area vs perimeter
                        math.sqrt(abs(val)) if val > 1 else val * 2,
                    ]
                elif topic == "arithmetic":
                    # Common arithmetic mistakes: operation errors, order of operations
                    variations = [
                        val + 10 if abs(val) > 10 else val + 1,
                        val - 10 if abs(val) > 10 else val - 1,
                        val * 10 if abs(val) < 10 else val * 1.5,
                        val / 10 if abs(val) > 10 else val / 2,
                        -val,
                    ]
                elif topic == "trigonometry":
                    # Common trig mistakes: degrees vs radians, reciprocal functions
                    variations = [
                        1 / val if val != 0 else 1,  # Reciprocal
                        -val,  # Sign error
                        90 - val if abs(val) <= 90 else val * 0.9,  # Complementary angle
                        val * 180 / 3.14159 if abs(val) < 10 else val / 57.3,  # Deg/rad
                    ]
                elif topic == "probability" or topic == "statistics":
                    # Common probability mistakes: complement, wrong denominators
                    if 0 <= val <= 1:
                        variations = [
                            1 - val,  # Complement
                            val * 100,  # Forgot percentage conversion
                            val / 100 if val > 1 else val * 2,
                            min(val * 2, 1),  # Doubled probability
                        ]
                    else:
                        variations = [
                            val * 2,
                            val / 2,
                            val + 1,
                            val - 1,
                        ]
                else:
                    # Default: proportional errors
                    magnitude = abs(val) if val != 0 else 1
                    variations = [
                        val + magnitude * 0.1,
                        val - magnitude * 0.1,
                        val * 1.5,
                        val * 0.5,
                        -val,
                    ]
                
                # Format and add variations
                for new_val in variations:
                    if new_val == val:  # Skip if same as correct answer
                        continue
                    
                    # Format based on original answer format
                    if is_integer and abs(new_val - round(new_val)) < 0.01:
                        formatted = str(int(round(new_val)))
                    elif is_integer:
                        formatted = str(int(round(new_val)))
                    else:
                        # Match decimal places of original answer
                        if '.' in base:
                            decimals = len(base.split('.')[1]) if '.' in base else 2
                            decimals = min(decimals, 4)  # Cap at 4 decimal places
                        else:
                            decimals = 2
                        formatted = f"{new_val:.{decimals}f}".rstrip('0').rstrip('.')
                    
                    distractors.append(formatted)
                    
        except Exception as e:
            print(f"Error generating distractors: {e}")
            # Fallback: simple variations
            try:
                val = float(base)
                distractors.extend([
                    str(int(val + 1)),
                    str(int(val - 1)),
                    str(int(val * 2)),
                ])
            except:
                distractors.extend([
                    base + " units",
                    f"Not {base}",
                    "Cannot be determined",
                ])
        
        # Deduplicate and remove the correct answer
        out = []
        seen = set([base.lower(), correct.strip().lower()])
        for d in distractors:
            d_clean = str(d).strip().replace(',', '').lower()
            d_display = str(d).strip()
            if d_clean and d_clean not in seen and len(d_display) < 50:
                seen.add(d_clean)
                out.append(d_display)
            if len(out) >= max_count:
                break
        
        # Ensure we have exactly max_count distractors with final fallback
        while len(out) < max_count:
            try:
                val = float(base)
                # Generate a somewhat random but reasonable value
                if abs(val) > 100:
                    offset = random.choice([50, -50, 100, -100, 25, -25])
                elif abs(val) > 10:
                    offset = random.choice([5, -5, 10, -10, 3, -3])
                else:
                    offset = random.choice([1, -1, 2, -2, 0.5, -0.5])
                
                new_val = val + offset
                if new_val == val or new_val == 0:
                    new_val = val * 1.5 if val > 0 else val * 0.5
                    
                is_int = abs(float(base) - round(float(base))) < 0.01
                candidate = str(int(round(new_val))) if is_int else f"{new_val:.2f}".rstrip('0').rstrip('.')
                candidate_norm = candidate.replace(',', '').lower()
                
                if candidate_norm not in seen:
                    seen.add(candidate_norm)
                    out.append(candidate)
            except:
                # Last resort
                placeholder = f"Option {len(out) + 1}"
                if placeholder not in out:
                    out.append(placeholder)
                else:
                    out.append(f"Answer {len(out) + 1}")
        
        return out[:max_count]

    def mix_choices(self, correct: str, distractors):
        import random
        if not correct:
            return []
        choices = [correct] + list(distractors)
        random.shuffle(choices)
        return choices
    
    def generate_question_with_solution(self, grade: int, difficulty: str, topic: str) -> Tuple[str, str, List[str], List[str]]:
        """Generate a question along with its solution and hints (using solver when possible)"""
        try:
            print(f"Generating question for grade {grade}, {difficulty} difficulty, topic: {topic}")
            # generate_question now returns only the question (answer/hint/steps are generated on-demand)
            question, _, _, _ = generate_question(grade, difficulty, topic)
            print(f"Generated question: {question}")
            
            # Generate solution using the enhanced pipeline (solver + LLM)
            answer, solution_steps = generate_solution(question, topic)
            print(f"Answer: {answer}")
            
            # Generate hint on-demand
            hint = generate_hint(question, topic) if answer else "Think about the key concepts and formulas you know for this type of problem."
            
            # Ensure solution_steps is a list
            if isinstance(solution_steps, str):
                solution_steps = solution_steps.split("\n")
            elif not isinstance(solution_steps, list):
                solution_steps = [str(solution_steps)]
            
            # Clean up and format solution steps
            formatted_steps = []
            for i, step in enumerate(solution_steps, 1):
                step = step.strip()
                if step:
                    if step.startswith(f"{i}.") or step.startswith("-") or step.startswith("*") or re.match(r"^\d+\.", step):
                        formatted_steps.append(step)
                    else:
                        formatted_steps.append(f"{i}. {step}")
            
            if not formatted_steps:
                formatted_steps = [
                    "1. Read the question carefully", 
                    "2. Apply the appropriate formula or method",
                    "3. Calculate step by step",
                    "4. Check your answer"
                ]
            
            return question, answer, [hint], formatted_steps
            
        except Exception as e:
            print(f"Error in generate_question_with_solution: {str(e)}")
            # Return a fallback question if something goes wrong
            return (
                f"Sample {difficulty} {topic} question for grade {grade}: What is 2 + 2?",
                "4",
                ["Think about basic addition", "Count if needed"],
                ["1. Add 2 and 2 together", "2. Verify your answer"]
            )

    def generate_question_only(self, grade: int, difficulty: str, topic: str) -> str:
        """Generate only the question text (no hints/solutions)."""
        try:
            question, answer, hint_from_model, solution_steps = generate_question(grade, difficulty, topic)
            return question
        except Exception as e:
            print(f"Error in generate_question_only: {e}")
            return f"Sample {difficulty} {topic} question for grade {grade}: What is 2 + 2?"

    def generate_hint_for_question(self, question_text: str, topic: str, model: str = "phi", hint_level: int = 1) -> str:
        """Generate a hint for an existing question (on-demand).
        
        Args:
            question_text: The question to generate hint for
            topic: The topic (algebra, geometry, etc.)
            model: LLM model to use (fallback if progressive hints fail)
            hint_level: 1 (conceptual), 2 (strategic), or 3 (procedural)
        
        Returns:
            Hint string appropriate for the requested level
        """
        # Try progressive hints first (deterministic, faster, better quality)
        if PROGRESSIVE_HINTS_AVAILABLE:
            try:
                # Cache key for progressive hints (deterministic)
                cache_key = f"{question_text}:{topic}:{hint_level}"
                
                if cache_key in self._hint_cache:
                    self._cache_hits += 1
                    return self._hint_cache[cache_key]
                
                self._cache_misses += 1
                tier1, tier2, tier3 = generate_progressive_hints(question_text, topic)
                hints_map = {1: tier1, 2: tier2, 3: tier3}
                
                # Cache all three tiers
                for level, hint in hints_map.items():
                    self._hint_cache[f"{question_text}:{topic}:{level}"] = hint
                
                return hints_map.get(hint_level, tier1)
            except Exception as e:
                print(f"Progressive hints failed: {e}, falling back to LLM")
        
        # Fallback to LLM-based hint generation (not cached due to variability)
        try:
            return generate_hint(question_text, topic, model)
        except Exception as e:
            print(f"Error generating hint: {e}")
            return "Think about the key concepts and formulas you know for this type of problem."

    def generate_solution_for_question(self, question_text: str, topic: str, model: str = "phi", enhanced: bool = False) -> Tuple[str, List]:
        """Generate solution (answer, steps) for an existing question (on-demand).
        
        Args:
            question_text: The question to solve
            topic: Math topic
            model: LLM model for fallback
            enhanced: If True, return enhanced steps with explanations
        
        Returns:
            (answer, steps) where steps is List[str] or List[Dict] if enhanced=True
        """
        try:
            # 1) Try deterministic solver first for common patterns
            try:
                det = deterministic_solve(question_text, topic)
            except Exception as _:
                det = None
            if det and isinstance(det, tuple) and len(det) == 2:
                answer, steps = det
            else:
                # 2) Fallback to model-based solution
                answer, steps = generate_solution(question_text, topic, model)
            
            if enhanced and SOLUTION_EXPLAINER_AVAILABLE and steps:
                # Return enhanced solution with explanations
                enhanced_steps = enhance_solution_steps(steps, question_text, topic)
                return answer, enhanced_steps
            
            return answer, steps
        except Exception as e:
            print(f"Error generating solution: {e}")
            return "", []

    def normalize_answer(self, ans: str) -> List[str]:
        """Public wrapper to normalize an answer into comparable forms (fractions and decimals)."""
        a = str(ans).strip().lower()
        normalized: List[str] = []

        # 1) Extract fraction matches first and add both fraction and decimal forms
        frac_matches = re.findall(r"[-+]?\d+/\d+", a)
        for v in frac_matches:
            v_str = v.strip()
            try:
                num, denom = map(float, v_str.split('/'))
                if denom != 0:
                    # Keep fraction first (familiar to students), then decimal
                    normalized.append(v_str)
                    normalized.append(str(num/denom))
                else:
                    normalized.append(v_str)
            except Exception:
                normalized.append(v_str)

        # Remove fractions from the string so we don't double-capture numbers inside them
        a_no_frac = re.sub(r"[-+]?\d+/\d+", " ", a)

        # 2) Extract standalone numeric matches (decimals/integers)
        num_matches = re.findall(r"[-+]?\d*\.?\d+", a_no_frac)
        for v in num_matches:
            v = v.strip()
            if not v:
                continue
            try:
                normalized.append(str(float(v)))
            except Exception:
                normalized.append(v)

        # 3) If nothing was found, fall back to original cleaned string
        if not normalized:
            normalized = [a]

        # Deduplicate while preserving order
        seen = set()
        out: List[str] = []
        for x in normalized:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out
    
    @staticmethod
    def numeric_equal(val1: str, val2: str, tolerance: float = 0.01) -> bool:
        """Compare two strings as numbers if possible."""
        try:
            return abs(float(val1) - float(val2)) < tolerance
        except (ValueError, TypeError):
            return False

    def validate_answer(self, correct_answer: str, student_answer: str, attempt_number: int, correct_normalized: List[str] = None) -> Tuple[bool, float, str, str]:
        """Validate student's answer and provide feedback"""
        start_time = time.time()
        
        # Normalize answers for comparison - support various formats
        def normalize_answer(ans: str) -> List[str]:
            # Convert to lowercase, remove spaces/whitespace
            ans = str(ans).strip().lower()
            # Prioritize extracting fraction patterns first
            normalized: List[str] = []

            # 1) Fractions
            frac_matches = re.findall(r"[-+]?\d+/\d+", ans)
            for v in frac_matches:
                v_str = v.strip()
                try:
                    num, denom = map(float, v_str.split('/'))
                    if denom != 0:
                        normalized.append(v_str)
                        normalized.append(str(num/denom))
                    else:
                        normalized.append(v_str)
                except Exception:
                    normalized.append(v_str)

            # Remove fractions to avoid capturing numerator/denominator separately
            ans_no_frac = re.sub(r"[-+]?\d+/\d+", " ", ans)

            # 2) Standalone numbers (decimals/integers)
            num_matches = re.findall(r"[-+]?\d*\.?\d+", ans_no_frac)
            for v in num_matches:
                v = v.strip()
                if not v:
                    continue
                try:
                    normalized.append(str(float(v)))
                except Exception:
                    normalized.append(v)

            if not normalized:
                normalized = [ans]

            # Deduplicate while preserving order
            seen = set()
            out = []
            for x in normalized:
                if x not in seen:
                    seen.add(x)
                    out.append(x)
            return out

        # Get normalized versions of both answers. If caller provided pre-normalized variants (preferred), use them.
        if correct_normalized and isinstance(correct_normalized, list) and len(correct_normalized) > 0:
            correct_values = correct_normalized
        else:
            correct_values = normalize_answer(correct_answer)
        student_values = normalize_answer(student_answer)

        print(f"Debug - Original values: correct='{correct_answer}', student='{student_answer}'")
        print(f"Debug - Normalized values: correct={correct_values}, student={student_values}")
        
        # Various ways the answer could be correct
        is_exact_match = any(s == c for s in student_values for c in correct_values)
        is_numeric_match = any(self.numeric_equal(s, c) for s in student_values for c in correct_values)

        print(f"Debug - Checking matches: exact={is_exact_match}, numeric={is_numeric_match}")
        if not is_exact_match and not is_numeric_match:
            print("Debug - Detailed numeric comparisons:")
            for s in student_values:
                for c in correct_values:
                    try:
                        print(f"  {s} vs {c}: diff={abs(float(s) - float(c))}")
                    except (ValueError, TypeError) as e:
                        print(f"  {s} vs {c}: error={str(e)}")

        # For sets of values (like multiple solutions), check if sets match
        if len(student_values) > 1 and len(student_values) == len(correct_values):
            # Try both exact and numeric matching for sets
            student_set = set(student_values)
            correct_set = set(correct_values)
            is_set_match = student_set == correct_set
            if not is_set_match:
                # Try numeric comparison for sets
                is_set_match = all(
                    any(self.numeric_equal(s, c) for c in correct_values)
                    for s in student_values
                ) and len(student_values) == len(correct_values)
        else:
            is_set_match = False

        is_correct = is_exact_match or is_numeric_match or is_set_match
        confidence = 1.0 if is_exact_match else 0.95 if is_numeric_match or is_set_match else 0.0
        
        # Generate appropriate feedback
        if is_correct:
            if is_exact_match:
                feedback = "Perfect! Your answer is exactly correct!"
            else:
                feedback = "Correct! Your answer is numerically equivalent to the solution."
        else:
            if attempt_number == 1:
                feedback = "Not quite right. Try reviewing the problem carefully."
            elif attempt_number == 2:
                feedback = "Still not correct. Consider breaking down the problem into steps."
            else:
                feedback = "Keep trying! Consider using the available hints to guide you."
        
        # Generate next hint if answer is incorrect
        if not is_correct:
            hints = [
                "Review the basic concepts needed for this problem.",
                "Break the problem down into smaller parts.",
                "Check your calculations carefully.",
                "Consider using a different approach."
            ]
            next_hint = hints[min(attempt_number - 1, len(hints) - 1)]
        else:
            next_hint = None
        
        time_taken = time.time() - start_time
        
        return is_correct, confidence, feedback, next_hint
    
    def calculate_points(self, is_correct: bool, attempt_number: int, time_taken: float, difficulty: str = "medium") -> int:
        """Calculate points based on correctness, attempts, time taken, and difficulty
        
        Points breakdown:
        - Base: 100 (easy), 150 (medium), 200 (hard)
        - Attempt penalty: -15 points per extra attempt
        - Speed bonus: Up to +50 for very fast (under 30s), +30 for fast (30-60s)
        - Speed penalty: -20 for slow (over 5 min), -30 for very slow (over 10 min)
        """
        if not is_correct:
            return 0
            
        # Difficulty-based base points
        difficulty_points = {
            "easy": 100,
            "medium": 150,
            "hard": 200,
        }
        base_points = difficulty_points.get(difficulty, 150)
        
        # Deduct points for multiple attempts
        attempt_penalty = 15 * max(0, attempt_number - 1)
        time_points = 0
        if time_taken < 30:
            time_points = 50
        elif time_taken < 60:
            time_points = 30
        elif time_taken < 120:
            time_points = 10
        elif time_taken > 600:
            time_points = -30
        elif time_taken > 300:
            time_points = -20
        final_points = base_points - attempt_penalty + time_points
        return max(final_points, 10)  # Ensure minimum points for correct answer