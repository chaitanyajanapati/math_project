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

class MathAIService:
    def __init__(self):
        # Initialize any AI model configurations here
        pass
    
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

    def generate_hint_for_question(self, question_text: str, topic: str, model: str = "phi") -> str:
        """Generate a hint for an existing question (on-demand)."""
        try:
            return generate_hint(question_text, topic, model)
        except Exception as e:
            print(f"Error generating hint: {e}")
            return "Think about the key concepts and formulas you know for this type of problem."

    def generate_solution_for_question(self, question_text: str, topic: str, model: str = "phi") -> Tuple[str, List[str]]:
        """Generate solution (answer, steps) for an existing question (on-demand)."""
        try:
            return generate_solution(question_text, topic, model)
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
    
    def calculate_points(self, is_correct: bool, attempt_number: int, time_taken: float) -> int:
        """Calculate points based on correctness, attempts, and time taken"""
        if not is_correct:
            return 0
            
        # Base points for correct answer
        base_points = 100
        
        # Deduct points for multiple attempts
        attempt_penalty = (attempt_number - 1) * 10
        
        # Time bonus/penalty (adjust thresholds as needed)
        time_points = 0
        if time_taken < 60:  # Fast solution
            time_points = 20
        elif time_taken > 300:  # Took too long
            time_points = -20
            
        final_points = base_points - attempt_penalty + time_points
        return max(final_points, 10)  # Ensure minimum points for correct answer