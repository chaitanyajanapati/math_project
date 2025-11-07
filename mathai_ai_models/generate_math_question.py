"""
generate_math_question.py
-------------------------
This module connects to a local Ollama model (like phi3 or mistral)
to generate random math questions based on grade, difficulty, and topic.

This file was refactored to only generate questions by default. Hints and
solutions are generated on demand via generate_hint(...) and generate_solution(...).
"""

import subprocess
import re
from typing import Tuple, List, Optional


def get_generic_hint(topic: str, question: str) -> str:
    """Generate a generic hint based on the topic and question."""
    topic_hints = {
        "algebra": "Try to isolate the variable on one side of the equation.",
        "geometry": "Remember the formulas for area and perimeter.",
        "arithmetic": "Break down the problem into smaller steps.",
        "percentages": "Convert the percentage to a decimal by dividing by 100.",
        "trigonometry": "Draw a diagram and label the sides.",
        "statistics": "Organize the data first before calculating.",
        "calculus": "Consider using differentiation or integration rules."
    }
    return topic_hints.get(topic, "Read the question carefully and identify what is being asked.")


def generate_manual_solution(question: str, topic: str) -> Tuple[Optional[str], Optional[str]]:
    """Generate a solution for simple patterns (fallback). Returns (answer, explanation)."""
    # Capture fractions like 3/4 as well as decimals/integers
    numbers = re.findall(r"[-+]?\d+/\d+|[-+]?[0-9]*\.?[0-9]+", question)

    # Basic arithmetic patterns
    if topic in ("basic_arithmetic", "arithmetic"):
        qlow = question.lower()
        # Proportion pattern: "If 5 apples cost $12, how much would 10 apples cost?"
        if qlow.startswith("if") and "how much" in qlow and len(numbers) >= 3:
            try:
                # numbers likely like [5, 12, 10]
                x = float(numbers[0])
                cost_x = float(numbers[1])
                target = float(numbers[2])
                result = (cost_x / x) * target
                explanation = f"Cost per item = {cost_x}/{x} = {cost_x/x}; cost for {target} items = {result}"
                return str(result), explanation
            except Exception:
                pass

        # 'of' pattern and fractions multiplication: e.g., "What is 3/4 of 1/2?"
        if " of " in qlow and len(numbers) >= 2:
            try:
                # helper to parse a number or fraction
                def parse_num(s):
                    s = s.strip()
                    if '/' in s:
                        a, b = s.split('/')
                        return float(a) / float(b)
                    return float(s)

                vals = [parse_num(n) for n in numbers[:2]]
                result = vals[0] * vals[1]
                explanation = f"Multiply {numbers[0]} by {numbers[1]} = {result}"
                return str(result), explanation
            except Exception:
                pass

        if "+" in question or "add" in qlow or "sum" in qlow:
            try:
                result = sum(float(n) for n in numbers)
                explanation = f"Add the numbers: {' + '.join(numbers)} = {result}"
                return str(result), explanation
            except Exception:
                pass
        if "-" in question or "subtract" in qlow or "difference" in qlow:
            try:
                if len(numbers) >= 2:
                    result = float(numbers[0]) - float(numbers[1])
                    explanation = f"Subtract the numbers: {numbers[0]} - {numbers[1]} = {result}"
                    return str(result), explanation
            except Exception:
                pass
        if "*" in question or "multiply" in qlow or "product" in qlow:
            try:
                result = 1
                for n in numbers:
                    result *= float(n)
                explanation = f"Multiply the numbers: {' × '.join(numbers)} = {result}"
                return str(result), explanation
            except Exception:
                pass
        if "/" in question or "divide" in qlow:
            try:
                if len(numbers) >= 2:
                    n1, n2 = float(numbers[0]), float(numbers[1])
                    if n2 != 0:
                        result = n1 / n2
                        explanation = f"Divide the numbers: {n1} ÷ {n2} = {result}"
                        return str(result), explanation
            except Exception:
                pass

    # Percentages
    if topic == "percentages":
        if "%" in question and len(numbers) >= 2:
            try:
                n1, n2 = float(numbers[0]), float(numbers[1])
                if "what is" in question.lower() and "of" in question:
                    result = (n1 * n2) / 100
                    explanation = f"Calculate {n1}% of {n2}: ({n1} × {n2}) ÷ 100 = {result}"
                    return str(result), explanation
            except Exception:
                pass

    # Geometry - simple area
    if topic == "geometry" and "area" in question.lower():
        ql = question.lower()
        try:
            if "square" in ql and len(numbers) >= 1:
                side = float(numbers[0])
                result = side * side
                explanation = f"Calculate area of square: side × side = {side} × {side} = {result}"
                return str(result), explanation
            if "rectangle" in ql and len(numbers) >= 2:
                l, w = float(numbers[0]), float(numbers[1])
                result = l * w
                explanation = f"Calculate area of rectangle: length × width = {l} × {w} = {result}"
                return str(result), explanation
        except Exception:
            pass

    return None, None


def generate_question(grade: int, difficulty: str, topic: str, model: str = "qwen2.5:7b") -> Tuple[str, str, str, List[str]]:
    """Generate only the question text. Return (question, answer, hint, solution_steps).
    By default answer/hint/steps are empty — they are generated on demand.
    """
    sample_questions = {
        "algebra": {
            "easy": {
                "question": "Solve for x: 2x + 3 = 11",
                "answer": "4",
                "explanation": "Subtract 3 from both sides: 2x = 8, then divide by 2: x = 4"
            },
            "medium": {
                "question": "Solve the equation: 3x² - 12 = 0",
                "answer": "2, -2",
                "explanation": "Factor out 3: 3(x² - 4) = 0, then solve: x = ±2"
            },
            "hard": {
                "question": "Solve the system of equations: 2x + y = 8, 3x - 2y = 1",
                "answer": "x = 2, y = 4",
                "explanation": "Use substitution method: from first equation y = 8 - 2x, substitute into second equation"
            }
        },
        "geometry": {
            "easy": {
                "question": "Find the area of a rectangle with length 6 cm and width 4 cm",
                "answer": "24",
                "explanation": "Area of rectangle = length × width = 6 × 4 = 24 square cm"
            },
            "medium": {
                "question": "Calculate the area of a triangle with base 8 cm and height 5 cm",
                "answer": "20",
                "explanation": "Area of triangle = (1/2) × base × height = (1/2) × 8 × 5 = 20 square cm"
            },
            "hard": {
                "question": "Find the volume of a cylinder with radius 3 cm and height 10 cm",
                "answer": "282.7",
                "explanation": "Volume = πr²h = π × 3² × 10 ≈ 282.7 cubic cm"
            }
        }
    }

    topic_contexts = {
        "algebra": "equations, variables, expressions",
        "geometry": "shapes, areas, angles, volumes",
        "arithmetic": "basic operations, fractions, decimals",
        "mensuration": "measurement of geometric shapes",
        "trigonometry": "sine, cosine, tangent, angles",
        "statistics": "mean, median, mode, probability",
        "calculus": "derivatives, integrals, limits"
    }

    context = topic_contexts.get(topic, topic)

    question_prompt = (
        f"Generate a {difficulty}-level math question for grade {grade} students.\n"
        f"Topic: {topic} ({context})\n\n"
        "Rules:\n"
        "1. Output only the question\n"
        "2. No hints or solutions\n"
        "3. No explanations\n"
        "4. Just one equation\n"
        "5. Only measurements for geometry\n\n"
        "Examples:\n"
        "- Solve for x: 3x + 5 = 14\n"
        "- Find the area of a rectangle with length 6 cm and width 4 cm\n"
        "- What is 25% of 80?\n\n"
        "Question:"
    )

    print(f"Generating question with model {model}...")
    generated_question = None
    for timeout in [20, 30, 40]:
        try:
            print(f"Attempting question generation with {timeout}s timeout...")
            result = subprocess.run([
                "ollama", "run", model, question_prompt
            ], capture_output=True, text=True, check=True, timeout=timeout)

            generated_question = result.stdout.strip()

            # Basic cleanups
            if "?" in generated_question:
                generated_question = generated_question.split("?", 1)[0] + "?"

            # Remove common solution markers
            solution_markers = ["solution:", "answer:", "hint:", "steps:", "output:", "therefore:", "(hint", "=>", "->", "\n", "solving:", "step "]
            for marker in solution_markers:
                if marker in generated_question.lower():
                    generated_question = generated_question.split(marker, 1)[0].strip()

            generated_question = re.sub(r"\([^)]*hint[^)]*\)", "", generated_question, flags=re.IGNORECASE).strip()

            # Keep only first equation if multiple
            if "=" in generated_question:
                parts = [p.strip() for p in generated_question.split("=")]
                if len(parts) > 2:
                    generated_question = f"{parts[0]} = {parts[1]}"

            print(f"Generated question: {generated_question}")
            if generated_question and len(generated_question) > 10:
                break
        except Exception as e:
            print(f"Question generation attempt failed with timeout {timeout}s: {str(e)}")
            continue

    if not generated_question:
        # fallback to sample
        fallback_topic = topic if topic in sample_questions else "algebra"
        fallback = sample_questions[fallback_topic][difficulty]
        return fallback["question"], fallback["answer"], "Think about what formulas or methods you know for this type of problem.", [fallback["explanation"]]

    # Return only the question; answer/hint/steps are generated on demand
    question = generated_question
    return question, "", "", []


def generate_hint(question: str, topic: str, model: str = "qwen2.5:7b") -> str:
    """Generate a short hint for a question using the model. Falls back to generic hint."""
    hint = None
    for timeout in [5, 10, 15]:
        try:
            hint_prompt = (
                f"Give a helpful hint for solving this {topic} question: {question}\n"
                "Hint rules: No answers, just key concepts, be brief\n"
                "Format: HINT: [your hint]"
            )
            print(f"Generating hint with {timeout}s timeout...")
            result = subprocess.run([
                "ollama", "run", model, hint_prompt
            ], capture_output=True, text=True, check=True, timeout=timeout)
            hint = result.stdout.strip()
            if "HINT:" in hint:
                hint = hint.split("HINT:", 1)[1].strip()
            break
        except Exception as e:
            print(f"Hint generation failed with timeout {timeout}s: {str(e)}")
            continue

    if not hint or len(hint) < 5:
        hint = get_generic_hint(topic, question)
    return hint


def generate_solution(question: str, topic: str, model: str = "qwen2.5:7b") -> Tuple[str, List[str]]:
    """Generate solution (answer + steps) for a question using the model.
    Returns (answer, solution_steps).
    
    Strategy:
    1. Try symbolic solver first (deterministic, always correct)
    2. If solver succeeds, optionally use LLM to enrich explanation steps
    3. If solver fails, use LLM with structured prompt and verification
    """
    # STEP 1: Try symbolic solver
    try:
        # Import solver (assuming it's in mathai_backend/app/utils/solver.py)
        # For now, we'll import from the parent if available
        import sys
        from pathlib import Path
        backend_path = Path(__file__).resolve().parents[1] / "mathai_backend"
        if backend_path.exists() and str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        try:
            from app.utils.solver import solve_question
            solver_result = solve_question(question, topic)
            
            if solver_result:
                solver_answer, solver_steps = solver_result
                print(f"✓ Symbolic solver found answer: {solver_answer}")
                # Return solver result directly (deterministic and correct)
                return solver_answer, solver_steps
        except ImportError as e:
            print(f"Solver not available: {e}")
    except Exception as e:
        print(f"Error trying symbolic solver: {e}")
    
    # STEP 2: Solver failed or unavailable, use LLM
    # Create prompt asking for ANSWER and SOLUTION
    answer = ""
    solution_steps: List[str] = []

    answer_prompt = (
        f"Solve this {topic} question: {question}\n\n"
        "Format:\n"
        "ANSWER: (write final answer with unit if applicable)\n"
        "SOLUTION:\n"
        "1. Write first step with units\n"
        "2. Show calculation details\n"
        "3. Conclude with final answer"
    )

    result = None
    for timeout in [10, 15, 20]:
        try:
            print(f"Generating solution with {timeout}s timeout...")
            result = subprocess.run([
                "ollama", "run", model, answer_prompt
            ], capture_output=True, text=True, check=True, timeout=timeout)
            break
        except subprocess.TimeoutExpired:
            print(f"Timeout after {timeout}s, retrying with longer timeout...")
            continue
        except Exception as e:
            print(f"Error during generation: {str(e)}")
            break

    if not result:
        # fallback to manual
        ans, expl = generate_manual_solution(question, topic)
        if ans:
            return ans, [f"1. {expl}"] if expl else []
        return "", []

    solution_text = result.stdout.strip()

    # Try strict format first
    if "ANSWER:" in solution_text and "SOLUTION:" in solution_text:
        parts = solution_text.split("SOLUTION:", 1)
        answer_part = parts[0].replace("ANSWER:", "", 1).strip()
        answer = answer_part
        steps_raw = parts[1].strip().splitlines()
        solution_steps = [s.strip().lstrip("123456789. ") for s in steps_raw if s.strip()]
        print(f"DEBUG: answer_part={answer_part}, solution_steps={solution_steps}")
    else:
        # More flexible parsing
        lines = [l.strip() for l in solution_text.splitlines() if l.strip()]
        for line in lines:
            low = line.lower()
            if low.startswith("answer:"):
                answer = line.split(":", 1)[1].strip()
                continue
            if "=" in line and re.search(r"[a-zA-Z]\s*=\s*[-+]?\d", line):
                # x = 3 style assignment
                rhs = line.split("=", 1)[1].strip()
                solution_steps.append(line)
                if not answer:
                    answer = rhs
                continue
            solution_steps.append(line)

    # Regex fallbacks if answer still empty
    if not answer:
        m = re.search(r"(?i)answer\s*[:\-]\s*(.+)", solution_text)
        if m:
            candidate = m.group(1).splitlines()[0].strip()
            answer = candidate
    if not answer:
        assigns = re.findall(r"[a-zA-Z]\s*=\s*([-+]?[0-9]*\.?[0-9]+)", solution_text)
        if assigns:
            answer = ", ".join(assigns)
    if not answer:
        m = re.search(r"(?i)the answer (?:is|=)\s*([-+]?[0-9]*\.?[0-9]+)", solution_text)
        if m:
            answer = m.group(1).strip()
    if not answer:
        nums = re.findall(r"[-+]?[0-9]*\.?[0-9]+", solution_text)
        if nums:
            answer = nums[-1]

    answer = answer.strip()

    # Validate LLM-produced answer against a deterministic/manual solver for simple patterns.
    try:
        manual_ans, manual_expl = generate_manual_solution(question, topic)
        if manual_ans:
            # helper to convert numeric-like string (including fractions) to float
            def to_float(x: str):
                s = str(x).strip()
                s = s.replace('$', '').replace(',', '')
                # fraction
                if '/' in s:
                    parts = s.split('/')
                    if len(parts) == 2:
                        try:
                            return float(parts[0]) / float(parts[1])
                        except Exception:
                            return None
                # percentage
                if s.endswith('%'):
                    try:
                        return float(s[:-1]) / 100.0
                    except Exception:
                        return None
                # generic float
                try:
                    return float(re.findall(r"[-+]?[0-9]*\.?[0-9]+", s)[0])
                except Exception:
                    return None

            parsed_val = to_float(answer)
            manual_val = to_float(manual_ans)
            # If manual solver gives a value and LLM answer is numeric but differs significantly,
            # prefer the manual answer (it's deterministic and less likely to hallucinate simple math).
            if manual_val is not None and parsed_val is not None:
                if abs(manual_val - parsed_val) > 1e-6:
                    print(f"WARNING: LLM answer '{answer}' disagrees with manual answer '{manual_ans}'. Using manual.")
                    answer = manual_ans
            elif manual_val is not None and parsed_val is None:
                # LLM produced non-numeric answer; prefer manual numeric answer
                print(f"INFO: LLM answer '{answer}' is non-numeric; using manual answer '{manual_ans}'.")
                answer = manual_ans
    except Exception as e:
        print(f"Error during manual answer validation: {e}")
    # ensure steps are nicely numbered
    if solution_steps:
        cleaned = []
        for i, s in enumerate(solution_steps):
            s_clean = s.strip()
            if not s_clean:
                continue
            if re.match(r"^\d+\.", s_clean):
                cleaned.append(s_clean)
            else:
                cleaned.append(f"{i+1}. {s_clean}")
        solution_steps = cleaned

    return answer, solution_steps



if __name__ == "__main__":
    # Quick manual test
    q, a, h, s = generate_question(9, "easy", "algebra")
    print("Question:", q)
    # Generate hint/solution on demand
    print("Hint:", generate_hint(q, "algebra"))
    ans, steps = generate_solution(q, "algebra")
    print("Answer:", ans)
    print("Steps:", steps)
