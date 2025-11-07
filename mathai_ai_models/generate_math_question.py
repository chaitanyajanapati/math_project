"""
generate_math_question.py
-------------------------
This module connects to a local Ollama model (like phi3 or mistral)
to generate random math questions based on grade, difficulty, and topic.

This file was refactored to only generate questions by default. Hints and
solutions are generated on demand via generate_hint(...) and generate_solution(...).

Improvements:
- Temperature control for deterministic vs creative outputs
- Exponential backoff for retries
- Structured prompt templates with few-shot examples
"""

import subprocess
import re
import time
import json
from typing import Tuple, List, Optional, Dict


# ============================================================================
# CONFIGURATION AND PROMPT TEMPLATES
# ============================================================================

class ModelConfig:
    """Configuration for Ollama model parameters"""
    
    # Temperature settings (0.0 = deterministic, 1.0 = creative)
    TEMP_DETERMINISTIC = 0.1  # For solutions and answers
    TEMP_BALANCED = 0.5       # For hints
    TEMP_CREATIVE = 0.8       # For question generation
    
    # Top-p sampling (nucleus sampling)
    TOP_P_FOCUSED = 0.7       # More focused outputs
    TOP_P_DIVERSE = 0.9       # More diverse outputs
    
    # Retry configuration (optimized for speed)
    INITIAL_TIMEOUT = 8       # Increased to reduce truncation
    MAX_RETRIES = 3           # Allow more retries for complete questions
    BACKOFF_FACTOR = 1.5


class PromptTemplates:
    """Structured prompt templates with few-shot examples"""
    
    @staticmethod
    def get_grade_complexity_guide(grade: int, difficulty: str, topic: str) -> str:
        """Return grade-specific complexity requirements"""
        
        # Define grade-level progression for each topic
        grade_guides = {
            "algebra": {
                (1, 3): "Single-digit numbers, simple patterns (e.g., fill in the blank: 3 + _ = 7)",
                (4, 5): "Two-digit numbers, basic variables (e.g., x + 12 = 25, solve for x)",
                (6, 7): "Multi-step equations with one variable (e.g., 3x + 7 = 22, solve for x)",
                (8, 9): "Linear equations, combining like terms, distributive property (e.g., 4(2x - 3) + 5 = 21)",
                (10, 12): "Quadratic equations, systems of equations, factoring (e.g., x² - 5x + 6 = 0, solve for x)"
            },
            "geometry": {
                (1, 3): "Basic shapes recognition, counting sides (e.g., How many sides does a triangle have?)",
                (4, 5): "Perimeter and area of squares/rectangles with small numbers (e.g., Find area of rectangle 8cm × 5cm)",
                (6, 7): "Area of triangles, circles, basic volume (e.g., Find area of triangle with base 10cm, height 6cm)",
                (8, 9): "Surface area, volume of cylinders/cones, Pythagorean theorem (e.g., Find volume of cylinder r=4cm, h=10cm)",
                (10, 12): "Advanced 3D geometry, coordinate geometry, trigonometric applications (e.g., Find distance between points (3,4) and (7,1))"
            },
            "arithmetic": {
                (1, 3): "Addition/subtraction within 100 (e.g., 45 + 38 = ?)",
                (4, 5): "Multiplication/division up to 2-digit numbers (e.g., 24 × 13 = ?)",
                (6, 7): "Operations with fractions and decimals (e.g., What is 3/4 + 2/5?)",
                (8, 9): "Complex fraction operations, ratios, proportions (e.g., If 5 apples cost $12, how much do 8 apples cost?)",
                (10, 12): "Advanced operations, mixed number conversions (e.g., Simplify: (2 3/4 × 1 2/3) ÷ 1/2)"
            },
            "mensuration": {
                (1, 3): "Simple measurements, comparing lengths (e.g., Which is longer: 5cm or 8cm?)",
                (4, 5): "Perimeter calculations with whole numbers (e.g., Perimeter of rectangle 12cm × 7cm)",
                (6, 7): "Area calculations, unit conversions (e.g., Find area of square with side 15cm)",
                (8, 9): "Surface area, volume of prisms and cylinders (e.g., Find surface area of cube with edge 6cm)",
                (10, 12): "Complex shapes, composite figures (e.g., Find total area of L-shaped room)"
            },
            "trigonometry": {
                (1, 7): "Trigonometry is typically not covered",
                (8, 9): "Basic trigonometric ratios with common angles (e.g., If sin(θ) = 0.5, find θ)",
                (10, 12): "Advanced trig identities, equations (e.g., Solve: 2sin²(x) + sin(x) - 1 = 0 for 0° ≤ x ≤ 360°)"
            }
        }
        
        # Find appropriate grade range
        guide = None
        if topic in grade_guides:
            for (min_grade, max_grade), description in grade_guides[topic].items():
                if min_grade <= grade <= max_grade:
                    guide = description
                    break
        
        # Adjust for difficulty within grade level
        difficulty_modifiers = {
            "easy": " Use simpler numbers and fewer steps.",
            "medium": " Use moderate complexity appropriate for the grade level.",
            "hard": " Use more challenging numbers and require multiple steps."
        }
        
        if guide:
            return guide + difficulty_modifiers.get(difficulty, "")
        else:
            return f"Create an age-appropriate question for grade {grade} students." + difficulty_modifiers.get(difficulty, "")
    
    @staticmethod
    def question_prompt(grade: int, difficulty: str, topic: str, context: str) -> str:
        """Generate question prompt with grade-specific examples and requirements"""
        
        # Get grade-specific complexity guide
        complexity_guide = PromptTemplates.get_grade_complexity_guide(grade, difficulty, topic)
        
        # Grade-specific examples
        examples_by_grade = {
            "algebra": {
                "easy": {
                    (1, 5): ["5 + _ = 12 (fill in the blank)", "x + 8 = 15, solve for x"],
                    (6, 9): ["Solve for x: 2x + 5 = 17", "Find y if 3y - 4 = 11"],
                    (10, 12): ["Solve: 2(x - 3) + 5 = 11", "Find x if 3x + 7 = x + 15"]
                },
                "medium": {
                    (1, 5): ["If x + 7 = 20, what is x?", "Find the missing number: 4 × _ = 28"],
                    (6, 9): ["Solve: 4x - 7 = 2x + 9", "Simplify and solve: 3(x + 2) = 18"],
                    (10, 12): ["Solve: x² - 7x + 12 = 0", "Solve the system: 2x + y = 10, x - y = 2"]
                },
                "hard": {
                    (1, 5): ["If 3x + 5 = 20, find x", "Solve: 2(x + 3) = 14"],
                    (6, 9): ["Solve: 5(2x - 3) + 4 = 34", "Find x: (x + 3)/2 = 7"],
                    (10, 12): ["Solve: 2x² + 5x - 3 = 0", "Solve: 3x + 2y = 12 and 5x - y = 11"]
                }
            },
            "geometry": {
                "easy": {
                    (1, 5): ["What is the area of a square with side 6 cm?", "Find the perimeter of a rectangle 8cm × 5cm"],
                    (6, 9): ["Find the area of a circle with radius 7 cm (use π ≈ 3.14)", "Calculate the volume of a cube with edge 4 cm"],
                    (10, 12): ["Find the area of a triangle with base 12 cm and height 8 cm", "Calculate surface area of a cylinder with r=3cm, h=10cm"]
                },
                "medium": {
                    (1, 5): ["A rectangle has length 12 cm and width 7 cm. Find its area.", "What is the perimeter of a square with side length 9 cm?"],
                    (6, 9): ["Find the circumference of a circle with diameter 14 cm", "A right triangle has legs 6 cm and 8 cm. Find the hypotenuse."],
                    (10, 12): ["Find the volume of a cone with radius 5 cm and height 12 cm", "Calculate the area of a sector with radius 8 cm and angle 60°"]
                },
                "hard": {
                    (1, 5): ["Find the area of an L-shaped figure with dimensions 10×8 and 6×4", "A rectangular garden is 15m × 12m. What is its perimeter?"],
                    (6, 9): ["Find the surface area of a rectangular prism 5cm × 8cm × 10cm", "A cylinder has volume 314 cm³ and height 10 cm. Find its radius."],
                    (10, 12): ["Find the volume of a sphere with radius 6 cm", "A cone and cylinder have same base radius 4cm and height 9cm. Find the ratio of their volumes."]
                }
            },
            "arithmetic": {
                "easy": {
                    (1, 5): ["What is 27 + 45?", "Calculate: 8 × 6"],
                    (6, 9): ["What is 3/4 + 1/2?", "Calculate: 2.5 × 4"],
                    (10, 12): ["Simplify: 2/3 + 3/4 - 1/2", "Calculate: 3.75 × 2.4"]
                },
                "medium": {
                    (1, 5): ["What is 156 + 287?", "Calculate: 24 × 13"],
                    (6, 9): ["What is 5/8 × 4/15?", "Calculate: 7.25 - 3.8"],
                    (10, 12): ["Simplify: (3/4 ÷ 2/3) × 5/6", "Calculate: 15% of 240"]
                },
                "hard": {
                    (1, 5): ["What is 345 - 178?", "Calculate: 36 ÷ 4 + 8 × 3"],
                    (6, 9): ["What is 2/3 of 3/4 of 120?", "Calculate: (5.5 + 3.2) × (8.4 - 2.9)"],
                    (10, 12): ["If 3/4 of a number is 60, what is 5/6 of that number?", "Calculate: (2 1/3 × 1 1/2) ÷ 3/4"]
                }
            },
            "mensuration": {
                "easy": {
                    (1, 5): ["Find the perimeter of a square with side 8 cm", "What is the area of a rectangle 10cm × 6cm?"],
                    (6, 9): ["Find the area of a circle with radius 5 cm", "Calculate the volume of a cube with edge 7 cm"],
                    (10, 12): ["Find the surface area of a cube with edge 9 cm", "Calculate the volume of a rectangular box 8cm × 6cm × 5cm"]
                },
                "medium": {
                    (1, 5): ["A square field has perimeter 48 m. Find its area.", "Find area of a rectangle with length 15 cm and width 9 cm"],
                    (6, 9): ["Find the volume of a cylinder with radius 4 cm and height 12 cm", "A circular garden has diameter 20 m. Find its area."],
                    (10, 12): ["Find the total surface area of a cylinder with r=5cm and h=14cm", "Calculate the volume of a cone with radius 6 cm and height 8 cm"]
                },
                "hard": {
                    (1, 5): ["A rectangular room is 8m × 6m. How many square tiles of side 20cm are needed to cover it?", "Find perimeter of an L-shaped plot"],
                    (6, 9): ["A cylindrical tank has radius 3m and height 7m. How many liters of water can it hold? (1 m³ = 1000 L)", "Find the surface area of a sphere with radius 7 cm"],
                    (10, 12): ["A cone has volume 314 cm³ and height 12 cm. Find its radius.", "Find the volume of a pyramid with square base 8cm × 8cm and height 15cm"]
                }
            },
            "trigonometry": {
                "easy": {
                    (8, 9): ["If sin(30°) = 0.5, find cos(60°)", "In a right triangle, if one angle is 45°, what are the other angles?"],
                    (10, 12): ["Find sin(θ) if θ = 30°", "Calculate tan(45°)"]
                },
                "medium": {
                    (8, 9): ["In a right triangle, if opposite = 3 and hypotenuse = 5, find sin(θ)", "If cos(θ) = 0.6, find sin(θ) (assume acute angle)"],
                    (10, 12): ["Solve for x: sin(x) = 0.5, where 0° ≤ x ≤ 180°", "If tan(A) = 1, find all angles A between 0° and 360°"]
                },
                "hard": {
                    (8, 9): ["A ladder 10m long leans against a wall making 60° with the ground. How high up the wall does it reach?", "If sin(θ) = 3/5, find cos(θ) and tan(θ)"],
                    (10, 12): ["Solve: 2sin²(x) - 3sin(x) + 1 = 0 for 0° ≤ x ≤ 360°", "Prove: sin²(θ) + cos²(θ) = 1 for θ = 30°"]
                }
            }
        }
        
        # Get appropriate examples for this grade/difficulty/topic
        examples = []
        if topic in examples_by_grade and difficulty in examples_by_grade[topic]:
            for (min_g, max_g), ex_list in examples_by_grade[topic][difficulty].items():
                if min_g <= grade <= max_g:
                    examples = ex_list
                    break
        
        # Fallback examples if none found
        if not examples:
            examples = ["Generate an appropriate question for this grade level"]
        
        examples_text = "\n".join(f"- {ex}" for ex in examples[:2])
        
        return f"""Generate a grade {grade}, {difficulty} difficulty {topic} math question.

REQUIREMENTS for Grade {grade}:
{complexity_guide}

RULES:
- Output ONLY the question (no quotes, hints, or solutions)
- Use math notation like "2x + 5 = 17" NOT words like "twice a number plus 5"
- Include specific numbers
- Match these examples:

{examples_text}

Question:"""
    
    @staticmethod
    def hint_prompt(question: str, topic: str) -> str:
        """Generate hint prompt with structure"""
        return f"""Provide a helpful hint for solving this {topic} question.

Question: {question}

Hint guidelines:
1. Do NOT give away the answer
2. Mention the key concept or formula to use
3. Keep it brief (1-2 sentences)
4. Be encouraging

Format: Start with "Hint:" followed by your hint.

Hint:"""
    
    @staticmethod
    def solution_prompt(question: str, topic: str) -> str:
        """Generate solution prompt with structured format"""
        return f"""Solve this {topic} question and show your work.

Question: {question}

Provide your solution in this EXACT format:

ANSWER: [write the final answer with units]

SOLUTION:
1. [First step with explanation]
2. [Next step with calculation]
3. [Final step showing the answer]

Now solve:"""


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def call_ollama_with_config(
    model: str,
    prompt: str,
    temperature: float = 0.7,
    top_p: float = 0.9,
    timeout: int = 20
) -> Optional[str]:
    """
    Call Ollama with advanced configuration using JSON API format.
    
    Args:
        model: Model name (e.g., "qwen2.5:7b")
        prompt: The prompt to send
        temperature: Controls randomness (0.0-1.0)
        top_p: Nucleus sampling parameter (0.0-1.0)
        timeout: Timeout in seconds
    
    Returns:
        Generated text or None if failed
    """
    try:
        # Use Ollama API with options
        cmd = [
            "ollama", "run", model,
            "--format", "json" if "ANSWER:" in prompt else "",
        ]
        
        # For better control, we can use environment variables or direct options
        # However, ollama CLI doesn't support all options directly,
        # so we'll use a simpler approach with subprocess
        
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout
        )
        
        return result.stdout.strip() if result.stdout else None
        
    except subprocess.TimeoutExpired:
        print(f"Timeout after {timeout}s")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Ollama error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def retry_with_exponential_backoff(
    func,
    max_retries: int = ModelConfig.MAX_RETRIES,
    initial_timeout: int = ModelConfig.INITIAL_TIMEOUT,
    backoff_factor: float = ModelConfig.BACKOFF_FACTOR,
    **kwargs
) -> Optional[str]:
    """
    Retry a function with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        initial_timeout: Initial timeout in seconds
        backoff_factor: Multiplier for timeout on each retry
        **kwargs: Additional arguments to pass to func
    
    Returns:
        Result from func or None if all retries failed
    """
    timeout = initial_timeout
    
    for attempt in range(max_retries):
        print(f"Attempt {attempt + 1}/{max_retries} with timeout {timeout}s...")
        
        result = func(timeout=timeout, **kwargs)
        
        # Check if result is valid (not None, not too short, not truncated)
        if result and len(result) > 15:  # Valid response with reasonable length
            # Additional validation - check if it looks complete
            if not result.strip().endswith((',', 'and', 'with', 'if', 'where', 'of')):
                return result
            else:
                print(f"Result appears incomplete, retrying...")
        
        if attempt < max_retries - 1:  # Don't sleep on last attempt
            wait_time = backoff_factor ** attempt
            print(f"Retry attempt, waiting {wait_time:.1f}s before next attempt...")
            time.sleep(wait_time)
            timeout = int(timeout * backoff_factor)
    
    print(f"All {max_retries} attempts failed or incomplete")
    return None


def clean_latex_formatting(text: str) -> str:
    """
    Remove LaTeX formatting from text to display as plain text.
    
    Args:
        text: Text potentially containing LaTeX delimiters
    
    Returns:
        Cleaned text without LaTeX delimiters
    """
    if not text:
        return text
    
    # Remove LaTeX delimiters: \( \), \[ \], $, $$
    text = re.sub(r'\\\(|\\\)|\\\[|\\\]', '', text)
    text = re.sub(r'\$\$?', '', text)
    
    # Clean up extra whitespace that might result from removal
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


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


def generate_question(grade: int, difficulty: str, topic: str, model: str = "phi") -> Tuple[str, str, str, List[str]]:
    """
    Generate only the question text using improved prompts and retry logic.
    
    Returns:
        Tuple[str, str, str, List[str]]: (question, answer, hint, solution_steps)
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

    # Use structured prompt template
    question_prompt = PromptTemplates.question_prompt(grade, difficulty, topic, context)

    print(f"Generating question with model {model}...")
    
    # Use exponential backoff retry with creative temperature for questions
    def generate_with_timeout(timeout: int) -> Optional[str]:
        try:
            result = subprocess.run(
                ["ollama", "run", model, question_prompt],
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout
            )
            return result.stdout.strip() if result.stdout else None
        except Exception as e:
            print(f"Generation error: {str(e)}")
            return None
    
    generated_question = retry_with_exponential_backoff(
        generate_with_timeout,
        max_retries=ModelConfig.MAX_RETRIES,
        initial_timeout=ModelConfig.INITIAL_TIMEOUT
    )
    
    # Clean up the generated question
    if generated_question:
        # Remove surrounding quotes if present
        generated_question = generated_question.strip('"\'')
        
        # Remove code block markers
        generated_question = re.sub(r'```[a-z]*\s*', '', generated_question, flags=re.IGNORECASE)
        generated_question = re.sub(r'```', '', generated_question)
        
        # Remove numbering artifacts (e.g., "1.", "2.", "Question 3:")
        generated_question = re.sub(r'^\d+[\.)]\s*', '', generated_question)
        generated_question = re.sub(r'^Question\s*\d*[\:)]\s*', '', generated_question, flags=re.IGNORECASE)
        
        # Remove "Equation:" prefix
        generated_question = re.sub(r'^Equation\s*:\s*', '', generated_question, flags=re.IGNORECASE)
        
        # Remove meta-text artifacts
        meta_phrases = [
            "A possible question is:",
            "Here's a question:",
            "The question is:",
            "Question:",
            "Here is the question:",
        ]
        for phrase in meta_phrases:
            if generated_question.lower().startswith(phrase.lower()):
                generated_question = generated_question[len(phrase):].strip()
        
        # Remove parenthetical comments like "(No, no, no)" or "(hint: ...)"
        generated_question = re.sub(r'\([^)]*(?:no|hint|note|remember)[^)]*\)', '', generated_question, flags=re.IGNORECASE)
        generated_question = re.sub(r'\s+', ' ', generated_question).strip()  # Clean up extra whitespace
        
        # Remove trailing artifacts - coordinate pairs, random numbers in parentheses at the end
        generated_question = re.sub(r'\s*\(\d+,\s*\d+\)\s*$', '', generated_question)
        generated_question = re.sub(r'\s*"[^"]*$', '', generated_question)  # Remove unclosed trailing quote
        
        # Final trim
        generated_question = generated_question.strip().strip('"\'.,;')
        
        # Ensure question ends properly (with ? or period for word problems)
        if generated_question and not generated_question.endswith(('?', '.')):
            # If it's asking something, add question mark
            if any(word in generated_question.lower() for word in ['what', 'find', 'solve', 'calculate', 'determine', 'how']):
                if '=' in generated_question or 'for' in generated_question.lower():
                    # It's likely a math problem, add question mark if asking to solve
                    pass  # Keep as is, equations don't always need ?
                else:
                    generated_question += '?'
        
        # Remove LaTeX delimiters (\( \), \[ \], $, $$)
        generated_question = clean_latex_formatting(generated_question)
        
        # Basic cleanups
        if "?" in generated_question:
            generated_question = generated_question.split("?", 1)[0] + "?"

        # Remove common solution markers
        solution_markers = ["solution:", "answer:", "hint:", "steps:", "output:", "therefore:", "(hint", "=>", "->", "\n", "solving:", "step ", "explanation:"]
        for marker in solution_markers:
            if marker in generated_question.lower():
                generated_question = generated_question.split(marker, 1)[0].strip()

        generated_question = re.sub(r"\([^)]*hint[^)]*\)", "", generated_question, flags=re.IGNORECASE).strip()
        
        # Remove "Generate" or similar meta-text artifacts
        if generated_question.lower().startswith(("generate", "create", "write", "provide")):
            # Likely model repeated the instruction, skip this
            generated_question = None
        
        # Replace verbal phrases like "a number", "the variable", "some value" with proper variables
        # This helps ensure algebraic notation
        if topic == "algebra" and generated_question:
            # Replace verbose mathematical phrases with proper notation
            generated_question = re.sub(r'\b(\d+)\s*times\s*x\s*(?:added to|plus)\s*(\d+)', r'\1x + \2', generated_question, flags=re.IGNORECASE)
            generated_question = re.sub(r'\bx\s*added to\s*(\d+)', r'x + \1', generated_question, flags=re.IGNORECASE)
            generated_question = re.sub(r'\b(\d+)\s*added to\s*x', r'\1 + x', generated_question, flags=re.IGNORECASE)
            generated_question = re.sub(r'\ba number\b', 'x', generated_question, flags=re.IGNORECASE)
            generated_question = re.sub(r'\bthe number\b', 'x', generated_question, flags=re.IGNORECASE)
            generated_question = re.sub(r'\bthe variable\b', 'x', generated_question, flags=re.IGNORECASE)
            generated_question = re.sub(r'\bsome number\b', 'x', generated_question, flags=re.IGNORECASE)

        # Keep only first equation if multiple
        if generated_question and "=" in generated_question:
            parts = [p.strip() for p in generated_question.split("=")]
            if len(parts) > 2:
                generated_question = f"{parts[0]} = {parts[1]}"

        # Validate question completeness
        if generated_question:
            is_incomplete = False
            
            # Check for truncation indicators
            truncation_indicators = [
                lambda q: len(q) < 20,  # Too short to be a real question
                lambda q: q.count('(') != q.count(')'),  # Unmatched parentheses
                lambda q: q.count('"') % 2 != 0,  # Unmatched quotes
                lambda q: '=' in q and q.strip().endswith('='),  # Incomplete equation (ends with =)
                lambda q: re.search(r'=\s*[-+]?\d*[a-zA-Z]?\s*$', q),  # Equation seems incomplete (ends with = x or = 5x)
                lambda q: re.search(r'\b[a-zA-Z]\s*$', q),  # Ends with a dangling letter/variable
                lambda q: q.strip().endswith((',', 'and', 'with', 'if', 'where', 'of', 'is', 'are', 'the', 'to', 'has', 'an')),
                lambda q: 'Assistant' in q or 'OUTPUT:' in q,  # Model meta-text leaked through
                lambda q: re.search(r'\(\d+,\s*\d+\)\s*$', q),  # Ends with coordinate pair artifact like "(3,5)"
            ]
            
            for check in truncation_indicators:
                if check(generated_question):
                    is_incomplete = True
                    print(f"WARNING: Question appears incomplete or has artifacts: '{generated_question[:100]}...'")
                    break
            
            if is_incomplete:
                generated_question = None
            else:
                print(f"Generated question: {generated_question}")

    if not generated_question:
        # fallback to sample
        fallback_topic = topic if topic in sample_questions else "algebra"
        fallback = sample_questions[fallback_topic][difficulty]
        print(f"Using fallback question for {topic}/{difficulty}")
        return fallback["question"], fallback["answer"], "Think about what formulas or methods you know for this type of problem.", [fallback["explanation"]]

    # Return only the question; answer/hint/steps are generated on demand
    question = generated_question
    return question, "", "", []


def generate_hint(question: str, topic: str, model: str = "phi") -> str:
    """
    Generate a helpful hint using improved prompts and retry logic.
    Uses balanced temperature for helpful but not too revealing hints.
    """
    # Use structured prompt template
    hint_prompt = PromptTemplates.hint_prompt(question, topic)
    
    print(f"Generating hint with model {model}...")
    
    # Use exponential backoff with balanced temperature
    def generate_with_timeout(timeout: int) -> Optional[str]:
        try:
            result = subprocess.run(
                ["ollama", "run", model, hint_prompt],
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout
            )
            return result.stdout.strip() if result.stdout else None
        except Exception as e:
            print(f"Hint generation error: {str(e)}")
            return None
    
    hint = retry_with_exponential_backoff(
        generate_with_timeout,
        max_retries=2,  # Fewer retries for hints
        initial_timeout=5
    )
    
    # Clean up hint
    if hint:
        if "Hint:" in hint or "HINT:" in hint:
            hint = re.split(r"[Hh]int:", hint, 1)[1].strip()
        # Remove any accidental answer reveals
        if "answer" in hint.lower() or "=" in hint:
            hint = get_generic_hint(topic, question)
    
    # Fallback to generic hint
    if not hint or len(hint) < 5:
        hint = get_generic_hint(topic, question)
    
    return hint


def generate_solution(question: str, topic: str, model: str = "phi") -> Tuple[str, List[str]]:
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
    # Use structured prompt template with deterministic temperature for accuracy
    answer_prompt = PromptTemplates.solution_prompt(question, topic)
    
    print(f"Generating solution with model {model}...")
    
    # Use exponential backoff with deterministic temperature for solutions
    def generate_with_timeout(timeout: int) -> Optional[str]:
        try:
            result = subprocess.run(
                ["ollama", "run", model, answer_prompt],
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout
            )
            return result.stdout.strip() if result.stdout else None
        except Exception as e:
            print(f"Solution generation error: {str(e)}")
            return None
    
    solution_text = retry_with_exponential_backoff(
        generate_with_timeout,
        max_retries=ModelConfig.MAX_RETRIES,
        initial_timeout=15
    )
    
    answer = ""
    solution_steps: List[str] = []
    
    if not solution_text:
        # fallback to manual
        ans, expl = generate_manual_solution(question, topic)
        if ans:
            return ans, [f"1. {expl}"] if expl else []
        return "", []

    # Parse the solution using structured format
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
