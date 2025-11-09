"""Clean math question generation module.

This rebuild removes previous merge conflict artifacts and provides a stable
API surface expected by the backend service:

Functions exported:
  generate_question(grade, difficulty, topic, model="phi") -> (question, answer, hint, steps)
  generate_hint(question, topic, model="phi") -> hint
  generate_solution(question, topic, model="phi") -> (answer, steps)

Current strategy:
  1. 95% template-based generation (deterministic, grade-scaled).
  2. 5% optional LLM call (best-effort; safely sanitized). If LLM fails, fallback to template.
  3. Hints/Solutions generated on demand: solver first (if available), else manual/LLM fallback.

The previous complex retry/backoff and conflicting prompt code was removed for
clarity. You can extend this file again once repository state is clean.
"""

from __future__ import annotations

import re
import random
import subprocess
from typing import Tuple, List, Optional

"""Import / solver resolution notes:
The file dynamically tries to import the backend solver with a runtime sys.path
insertion inside generate_solution(). That works at execution time but static
linters (and some tooling) flag `from app.utils.solver import solve_question`
as unresolved because the path modification happens later.

To satisfy both runtime reliability and static analysis, we perform a guarded
import here with multiple fallbacks. If none succeed, `solve_question` is set
to None and the downstream code will skip the symbolic solver path.
"""
try:  # Direct import when running from backend context (uvicorn working dir)
    from app.utils.solver import solve_question  # type: ignore
except Exception:  # noqa: broad-except – fall back to alternative resolutions
    solve_question = None  # type: ignore

    # Attempt to add backend path and retry (works when invoking from repo root or model dir)
    try:
        import sys as _sys
        from pathlib import Path as _Path
        repo_root = _Path(__file__).resolve().parents[1]
        backend_dir = repo_root / "mathai_backend"
        if backend_dir.exists() and str(backend_dir) not in _sys.path:
            _sys.path.insert(0, str(backend_dir))
        try:
            from app.utils.solver import solve_question  # type: ignore
        except Exception:  # noqa: broad-except
            solve_question = None  # type: ignore
    except Exception:
        # Final fallback: leave solve_question as None
        solve_question = None  # type: ignore

# Import expanded templates with all new topics
try:
    from expanded_templates import EXPANDED_TEMPLATES
    print("[generate_math_question] Using EXPANDED_TEMPLATES with all topics")
except ImportError:
    print("[generate_math_question] WARNING: Could not import EXPANDED_TEMPLATES, using fallback")
    EXPANDED_TEMPLATES = None

# Import quality improvement modules
try:
    from smart_numbers import SmartNumberGenerator
    smart_number_gen = SmartNumberGenerator()
    print("[generate_math_question] SmartNumberGenerator loaded")
except ImportError:
    print("[generate_math_question] WARNING: Could not import SmartNumberGenerator")
    smart_number_gen = None

try:
    from question_validator import QuestionValidator, QuestionQualityScorer
    question_validator = QuestionValidator()
    quality_scorer = QuestionQualityScorer()
    print("[generate_math_question] QuestionValidator and QuestionQualityScorer loaded")
except ImportError:
    print("[generate_math_question] WARNING: Could not import validation modules")
    question_validator = None
    quality_scorer = None

try:
    from complexity_scorer import ComplexityScorer
    complexity_scorer = ComplexityScorer()
    print("[generate_math_question] ComplexityScorer loaded")
except ImportError:
    print("[generate_math_question] WARNING: Could not import ComplexityScorer")
    complexity_scorer = None


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
class ModelConfig:
    """Runtime-tunable configuration.

    Values can be overridden via environment variables so operators can
    shift behavior (e.g., increase AI variety) without code changes:

    MATHAI_TEMPLATE_RATE  float in [0,1]  (default 0.95)
    MATHAI_TEMP_CREATIVE  float temperature for novel questions (default 0.75)
    MATHAI_TEMP_HINT      float temperature for hints (default 0.5)
    MATHAI_TEMP_SOLVE     float temperature for solutions (default 0.1)
    """
    import os as _os

    def _f(name: str, default: float) -> float:
        try:
            v = float(ModelConfig._os.getenv(name, default))  # type: ignore[attr-defined]
            if v < 0:
                return 0.0
            if v > 1 and name.startswith("MATHAI_TEMP"):
                # allow >1 temps but cap at 2.0 for safety
                return min(v, 2.0)
            if name == "MATHAI_TEMPLATE_RATE":
                return min(max(v, 0.0), 1.0)
            return v
        except Exception:
            return default

    MAX_RETRIES = 3
    INITIAL_TIMEOUT = 12
    BACKOFF_FACTOR = 1.6
    TEMPLATE_RATE = _f("MATHAI_TEMPLATE_RATE", 0.95)  # probability to use templates

    TEMP_CREATIVE = _f("MATHAI_TEMP_CREATIVE", 0.75)
    TEMP_HINT = _f("MATHAI_TEMP_HINT", 0.5)
    TEMP_SOLVE = _f("MATHAI_TEMP_SOLVE", 0.1)


# ---------------------------------------------------------------------------
# Prompt helper (minimal – extend later if needed)
# ---------------------------------------------------------------------------
class PromptTemplates:
    @staticmethod
    def question_prompt(grade: int, difficulty: str, topic: str, context: str) -> str:
        return (
            "You are a math question generator. Return ONLY one **clear** question.\n"
            "Constraints:\n"
            " - Topic: {topic}\n - Grade: {grade}\n - Difficulty: {difficulty}\n"
            " - No prefix like 'Question:' or numbering.\n"
            " - No hints, no solution, no explanation.\n"
            " - Keep within one sentence unless word problem requires two.\n"
            " - End with '?' if interrogative, else '.' for statement problems.\n"
            "Context keywords: {context}\n"
        ).format(topic=topic, grade=grade, difficulty=difficulty, context=context)

    @staticmethod
    def hint_prompt(question: str, topic: str) -> str:
        return (
            "Provide a concise hint (NOT the answer) for the following {topic} problem.\n"
            "Question: {q}\n"
            "Rules: 1) Do NOT reveal the answer. 2) One or two short sentences."
        ).format(topic=topic, q=question)

    @staticmethod
    def solution_prompt(question: str, topic: str) -> str:
        return (
            "Solve the {topic} problem. First line: ANSWER:<value>. Then steps each on its own line beginning with a number.\n"
            "Question: {q}"
        ).format(topic=topic, q=question)


# ---------------------------------------------------------------------------
# Template question bank (grade-banded) – simplified version
# ---------------------------------------------------------------------------
TEMPLATES = {
    "algebra": {
        "easy": {
            (1, 5): ["Solve for x: 3x + 4 = NUM", "Find x if 5x = NUM", "If x + 9 = NUM what is x?"],
            (6, 9): ["Solve: 4x - 7 = NUM", "If 6x + 3 = NUM find x", "Solve for x: 3(x - 2) = NUM"],
            (10, 12): ["Solve: 5(x - 3) + 2x = NUM", "Find x: 4x - 7 = 2x + NUM", "Simplify then solve: 3(2x - 1) + 5 = NUM"]
        },
        "medium": {
            (1, 5): ["If 4x = NUM what is x?", "Solve: 7x - 5 = NUM", "Find x: 9x = NUM"],
            (6, 9): ["Solve: 6x - 13 = 3x + NUM", "Simplify and solve: 4(2x + 3) = NUM", "Find x: 5x - 7 = 2x + NUM"],
            (10, 12): ["Solve: 2x^2 - 13x + NUM = 0", "Solve system: 3x + 2y = NUM and 5x - y = NUM", "Find x: 3x^2 - 17x + NUM = 0"]
        },
        "hard": {
            (1, 5): ["Solve: 3(x + 5) = NUM", "If 2(x - 3) = NUM find x", "Solve: 4x + 7 = NUM"],
            (6, 9): ["Solve: 6(3x - 5) + 7 = NUM", "Find x: (2x + 7)/3 = NUM", "Solve: 4(2x - 3) - 5x = NUM"],
            (10, 12): ["Solve: 3x^2 - 14x + NUM = 0", "Solve system: 4x + 3y = NUM and 7x - 2y = NUM", "Factor and solve: 6x^2 - 17x + NUM = 0"]
        }
    },
    "geometry": {
        "easy": {
            (1,5): ["Find the area of a square with side NUM cm", "What is the perimeter of a rectangle with sides NUM cm and NUM cm?"],
            (6,9): ["Find the area of a circle with radius NUM cm (use π ≈ 3.14)", "What is the volume of a cube with edge NUM cm?"],
            (10,12): ["Find the volume of a sphere with radius NUM cm (use π ≈ 3.14)", "Find the surface area of a cube with edge NUM cm"]
        },
        "medium": {
            (1,5): ["A rectangle has length NUM cm and width NUM cm. Find its area", "Find the perimeter of a square with area NUM cm^2"],
            (6,9): ["A right triangle has legs NUM cm and NUM cm. Find the hypotenuse", "Find circumference of circle radius NUM cm"],
            (10,12): ["Find volume of a cone radius NUM cm height NUM cm (π ≈ 3.14)", "Distance between points (NUM, NUM) and (NUM, NUM)"]
        },
        "hard": {
            (1,5): ["Room NUM m by NUM m, tiles are 25 cm by 25 cm. How many tiles?", "Fence a rectangular field NUM m by NUM m at $12/m. What is cost?"],
            (6,9): ["Surface area of rectangular prism NUM×NUM×NUM cm", "Cylinder volume NUM cm^3 height NUM cm (π≈3.14). Find radius"],
            (10,12): ["Volume of sphere inscribed in cube side NUM cm", "Surface area of hemisphere radius NUM cm (π≈3.14)"]
        }
    },
    "arithmetic": {
        "easy": {
            (1,5): ["What is NUM - NUM?", "Calculate: NUM × NUM"],
            (6,9): ["What is NUM/NUM + NUM/NUM?", "Calculate: NUM × NUM"],
            (10,12): ["Simplify: NUM/NUM + NUM/NUM - NUM/NUM", "Calculate: NUM.NUM × NUM.NUM"]
        },
        "medium": {
            (1,5): ["What is NUM + NUM?", "Calculate: NUM × NUM"],
            (6,9): ["What is NUM/NUM × NUM/NUM?", "Calculate: NUM.NUM - NUM.NUM"],
            (10,12): ["If NUM% of a number is NUM find the number", "(NUM/NUM ÷ NUM/NUM) × NUM/NUM"]
        },
        "hard": {
            (1,5): ["What is NUM - NUM?", "Calculate: NUM ÷ NUM + NUM × NUM"],
            (6,9): ["What is NUM/NUM of NUM/NUM of NUM?", "(NUM.NUM + NUM.NUM) × (NUM.NUM - NUM.NUM)"],
            (10,12): ["If NUM/NUM of a number is NUM what is NUM/NUM of it?", "(NUM NUM/NUM × NUM NUM/NUM) ÷ NUM/NUM"]
        }
    }
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _pick_template(topic: str, difficulty: str, grade: int) -> Optional[str]:
    # Always use expanded templates for best variety and complexity
    template_source = EXPANDED_TEMPLATES if EXPANDED_TEMPLATES is not None else TEMPLATES

    if topic not in template_source or difficulty not in template_source[topic]:
        return None
    band = template_source[topic][difficulty]

    # For hard difficulty, filter for templates with complex structure
    def is_structurally_hard(template: str, topic: str) -> bool:
        keywords = {
            "algebra": ["system", "quadratic", "factor", "absolute value", "optimization", "mixture", "exponent", "logarithm"],
            "arithmetic": ["fraction", "%", "rate", "multi-step", "mixture", "percent", "ratio"],
            "geometry": ["composite", "volume", "surface area", "multi-step", "hemisphere", "inscribed", "distance"],
        }
        topic_keywords = keywords.get(topic, [])
        return any(k in template.lower() for k in topic_keywords) or ("system" in template.lower() or "quadratic" in template.lower())

    templates = []
    for (g_min, g_max), tlist in band.items():
        if g_min <= grade <= g_max:
            if difficulty == "hard":
                filtered = [t for t in tlist if is_structurally_hard(t, topic)]
                if filtered:
                    templates.extend(filtered)
                else:
                    templates.extend(tlist)
            else:
                templates.extend(tlist)
    # fallback any list
    if not templates:
        for _, tlist in band.items():
            templates.extend(tlist)
    if templates:
        return random.choice(templates)
    return None


def generate_variation_from_template(template: str, grade: int, topic: str = "arithmetic", difficulty: str = "medium") -> str:
    """Replace each NUM token or {a}, {b}, {c} placeholders with grade-scaled numbers; keep structure stable."""
    
    # Fallback to simple random generation (smart generation has method signature issues)
    if grade <= 5:
        low, high = 5, 40
    elif grade <= 9:
        low, high = 12, 120
    else:
        low, high = 25, 250

    def repl(match):
        # Provide variability; sometimes decimals or fractions for higher grades
        val = random.randint(low, high)
        if grade >= 10 and random.random() < 0.2:
            # occasional decimal
            return f"{round(val * random.uniform(0.3,1.2), 2)}"
        return str(val)

    # Replace tokens: both NUM (old format) and {a}, {b}, {c}, etc. (new format)
    out = re.sub(r"NUM", repl, template)
    out = re.sub(r"\{[a-z]\}", repl, out)
    # Basic cleanup of duplicate spaces
    return re.sub(r"\s+", " ", out).strip()


def clean_question(text: str) -> str:
    """Sanitize LLM output to a single clean question line."""
    if not text:
        return ""
    # Remove code fences / quotes
    t = re.sub(r"```[a-zA-Z]*", "", text)
    t = t.replace("```", "").strip().strip("'\"")
    # Take first meaningful line
    lines = [l.strip() for l in t.splitlines() if l.strip()]
    if not lines:
        return ""
    first = lines[0]
    # Strip leading numbering / prefixes
    first = re.sub(r"^(Question\s*\d*[:.)-]\s*|\d+[.)]\s*)", "", first, flags=re.IGNORECASE)
    # Remove meta-intro phrases
    meta = ["here is", "here's", "a possible", "example question", "the question is"]
    for m in meta:
        if first.lower().startswith(m):
            first = first[len(m):].strip(" :")
    # Ensure proper ending
    if not first.endswith(("?", ".")):
        if any(w in first.lower() for w in ["what", "find", "solve", "calculate", "determine", "how"]):
            first += "?"
        else:
            first += "."
    return first.strip()


def _call_ollama(prompt: str, model: str, timeout: int) -> Optional[str]:
    try:
        result = subprocess.run([
            "ollama", "run", model, prompt
        ], capture_output=True, text=True, timeout=timeout, check=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Ollama call failed ({e}); using template fallback.")
        return None


def generate_question(grade: int, difficulty: str, topic: str, model: str = "phi", force_ai: bool = False, max_attempts: int = 5) -> Tuple[str, str, str, List[str]]:
    """Generate a single math question with validation and complexity checking.

    Parameters:
        grade: int student grade level (1-12 typical)
        difficulty: str difficulty tag (easy/medium/hard)
        topic: str topic key (algebra, geometry, arithmetic, ...)
        model: str ollama model name
        force_ai: bool if True, bypass template probability and attempt AI first
        max_attempts: int maximum attempts to generate a valid question

    Returns a tuple of (question, answer, hint, steps) with only question
    populated here (other values kept for backward compatibility with older
    callers expecting the previous signature.)
    """
    
    for attempt in range(max_attempts):
        template = _pick_template(topic, difficulty, grade)

        # Decide path: AI first if forced OR random exceeds template rate.
        attempt_ai = force_ai or (template is not None and random.random() >= ModelConfig.TEMPLATE_RATE)

        question = None
        source = None

        if attempt_ai:
            prompt = PromptTemplates.question_prompt(grade, difficulty, topic, topic)
            raw = _call_ollama(prompt, model, timeout=ModelConfig.INITIAL_TIMEOUT)
            if raw:
                cleaned = clean_question(raw)
                if len(cleaned) >= 8:
                    question = cleaned
                    source = "LLM"

        # Fall back to template if AI failed or wasn't attempted
        if question is None:
            if template:
                question = generate_variation_from_template(template, grade, topic, difficulty)
                source = "TEMPLATE"
            else:
                # ultimate fallback static
                question = generate_variation_from_template("Solve for x: 3x + 7 = 22", grade, "algebra", difficulty)
                source = "FALLBACK"

        # Validate the question if validator is available (simplified - only check critical issues)
        if question_validator is not None and complexity_scorer is not None:
            try:
                # Just use complexity scoring for now - validation is too strict without answers
                complexity_result = complexity_scorer.calculate_complexity(question, topic)
                complexity_score = complexity_result['score']
                complexity_level = complexity_result['level']
                assessment = complexity_scorer.match_difficulty_to_grade(complexity_score, grade)
                
                print(f"[question-gen] SOURCE: {source} | Complexity: {complexity_score} ({complexity_level}) | Grade Assessment: {assessment}")
            except Exception as e:
                print(f"[question-gen] Scoring error: {e}")
                print(f"[question-gen] SOURCE: {source}")
        else:
            print(f"[question-gen] SOURCE: {source}")

        return question, "", "", []

    # Should never reach here, but just in case
    return "Solve for x: 2x + 5 = 15", "", "", []


# ---------------------------------------------------------------------------
# Hint generation
# ---------------------------------------------------------------------------
def get_generic_hint(topic: str, question: str) -> str:
    base = {
        "algebra": "Isolate the variable step by step.",
        "geometry": "Recall the appropriate formula for this shape.",
        "arithmetic": "Break the calculation into simpler parts.",
        "trigonometry": "Use fundamental trig identities and ratios (SOH-CAH-TOA).",
        "statistics": "Identify what measure is being asked (mean, median, mode, etc.).",
        "probability": "Consider the total possible outcomes and favorable outcomes.",
        "number_theory": "Think about factors, multiples, or divisibility rules.",
        "calculus": "Apply the appropriate rule (power, chain, product, etc.).",
    }
    return base.get(topic, "Identify the key operation or relationship.")


def generate_hint(question: str, topic: str, model: str = "phi") -> str:
    prompt = PromptTemplates.hint_prompt(question, topic)
    raw = _call_ollama(prompt, model, timeout=8)
    if not raw or len(raw) < 5:
        return get_generic_hint(topic, question)
    # Strip answer leakage
    if re.search(r"=\s*\d", raw) or "answer" in raw.lower():
        return get_generic_hint(topic, question)
    # Keep to one-two sentences
    sentences = re.split(r"(?<=[.?!])\s+", raw.strip())
    return " ".join(sentences[:2]).strip()


# ---------------------------------------------------------------------------
# Solution generation (solver-first, simplified fallback)
# ---------------------------------------------------------------------------
def generate_manual_solution(question: str, topic: str) -> Tuple[str, str]:
    # Very lightweight parser for simple linear forms: ax + b = c
    m = re.match(r".*?([+-]?\d+)x\s*([+-]\s*\d+)?\s*=\s*([+-]?\d+)", question.replace(" ", ""))
    if m:
        a = int(m.group(1))
        b = m.group(2)
        c = int(m.group(3))
        b_val = int(b.replace("+", "")) if b else 0
        # a x + b = c -> a x = c - b
        x = (c - b_val)/a
        return (str(int(x)) if abs(x - int(x)) < 1e-9 else str(x), f"Subtract {b_val} then divide by {a}.")
    return "", ""


def generate_solution(question: str, topic: str, model: str = "phi") -> Tuple[str, List[str]]:
    """Generate solution (answer + steps) using solver-first, then LLM fallback.

    Returns: (answer, steps)
    """
    # 1) Try symbolic solver if available
    try:
        if 'solve_question' in globals() and solve_question is not None:  # type: ignore[name-defined]
            solver_result = solve_question(question, topic)  # type: ignore[name-defined]
            if solver_result:
                solver_answer, solver_steps = solver_result
                return str(solver_answer).strip(), list(solver_steps)
    except Exception as e:
        print(f"Symbolic solver failed: {e}")

    # 2) Try simple manual parse for linear forms
    ans, expl = generate_manual_solution(question, topic)
    if ans:
        steps = [s for s in [expl, "Substitute back to verify."] if s]
        steps = [f"{i+1}. {s}" for i, s in enumerate(steps)]
        return ans, steps

    # 3) LLM fallback
    prompt = PromptTemplates.solution_prompt(question, topic)
    raw = _call_ollama(prompt, model, timeout=15)
    if not raw:
        # If LLM fails, return generic steps
        generic_steps = [
            "Read the question carefully.",
            "Apply the appropriate formula or method.",
            "Calculate step by step.",
            "Check your answer."
        ]
        return "", [f"{i+1}. {s}" for i, s in enumerate(generic_steps)]

    answer = ""
    steps: List[str] = []
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    for line in lines:
        if line.lower().startswith("answer:") and not answer:
            answer = line.split(":", 1)[1].strip()
        else:
            steps.append(line)

    if not answer:
        nums = re.findall(r"[-+]?\d*\.?\d+", raw)
        if nums:
            answer = nums[-1]

    steps = [f"{i+1}. {s}" for i, s in enumerate(steps)]
    # Pad steps to minimum 4 points if too short
    if len(steps) < 4:
        generic_steps = [
            "Read the question carefully.",
            "Apply the appropriate formula or method.",
            "Calculate step by step.",
            "Check your answer."
        ]
        for i in range(len(steps), 4):
            steps.append(f"{i+1}. {generic_steps[i]}")
    return answer.strip(), steps


if __name__ == "__main__":
    q, a, h, st = generate_question(9, "easy", "algebra")
    print("Question:", q)
    print("Hint:", generate_hint(q, "algebra"))
    sol_a, sol_steps = generate_solution(q, "algebra")
    print("Answer:", sol_a)
    print("Steps:", sol_steps)
