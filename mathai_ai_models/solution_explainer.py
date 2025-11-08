"""Enhanced solution explanations module.

Provides detailed step-by-step explanations with:
- Why this step is necessary
- What concept it uses
- Common mistakes to avoid
"""

from typing import List, Dict

def enhance_solution_steps(steps: List[str], question: str, topic: str) -> List[Dict[str, str]]:
    """Enhance solution steps with explanations and warnings.
    
    Returns: List of dicts with keys:
        - step: The original step text
        - why: Why this step is needed
        - concept: What concept/formula is being used
        - warning: Common mistake to avoid (if applicable)
    """
    
    enhanced = []
    
    for idx, step in enumerate(steps):
        step_lower = step.lower()
        enhanced_step = {
            "step": step,
            "why": _explain_why(step_lower, idx, topic),
            "concept": _identify_concept(step_lower, topic),
            "warning": _common_mistake(step_lower, topic),
        }
        enhanced.append(enhanced_step)
    
    return enhanced


def _explain_why(step: str, step_number: int, topic: str) -> str:
    """Explain why this step is necessary."""
    
    if topic == "algebra":
        if "distribute" in step or "expand" in step:
            return "We need to eliminate parentheses to see all terms clearly"
        elif "combine" in step or "collect" in step:
            return "Grouping like terms simplifies the equation"
        elif "subtract" in step or "add" in step and "both sides" in step:
            return "We maintain equality by doing the same operation to both sides"
        elif "divide" in step or "multiply" in step and "both sides" in step:
            return "This isolates the variable to solve for it"
        elif "factor" in step:
            return "Factoring helps us find the values that make the expression zero"
        elif "substitute" in step:
            return "Plugging in known values helps find unknown variables"
        elif "verify" in step or "check" in step:
            return "Always verify your answer works in the original equation"
        else:
            return "This step brings us closer to isolating the variable"
    
    elif topic == "geometry":
        if "formula" in step or "π" in step or "area" in step or "volume" in step:
            return "We apply the specific formula for this shape"
        elif "substitute" in step or "plug" in step:
            return "We replace variables with the given measurements"
        elif "calculate" in step or "multiply" in step:
            return "Perform the arithmetic to get the final answer"
        elif "square" in step and "²" in step:
            return "Squaring gives us the area for 2D or volume component for 3D"
        else:
            return "This calculation follows from the geometric formula"
    
    elif topic == "arithmetic":
        if step_number == 0:
            return "Start with the first operation according to order of operations (PEMDAS)"
        elif "parenthes" in step:
            return "Parentheses have highest priority in order of operations"
        elif "/" in step or "divide" in step:
            return "Division and multiplication are done left to right"
        elif "+" in step or "-" in step:
            return "Addition and subtraction are done last, left to right"
        else:
            return "Continue following the order of operations"
    
    elif topic == "trigonometry":
        if "soh-cah-toa" in step.lower() or "opposite" in step or "adjacent" in step:
            return "Identifying sides relative to the angle determines which ratio to use"
        elif "sin" in step or "cos" in step or "tan" in step:
            return "Using the appropriate trig ratio connects the known and unknown sides"
        elif "inverse" in step or "arcsin" in step or "arccos" in step:
            return "Inverse trig functions find the angle when we know the ratio"
        else:
            return "This step applies trigonometric relationships"
    
    elif topic == "calculus":
        if "power rule" in step:
            return "The power rule is the fundamental technique for differentiating polynomials"
        elif "chain rule" in step:
            return "The chain rule handles compositions of functions"
        elif "derivative" in step:
            return "We're finding the rate of change"
        elif "integral" in step:
            return "Integration finds the area or reverses differentiation"
        else:
            return "This step applies calculus rules to transform the expression"
    
    else:
        if step_number == 0:
            return "Start by setting up the problem with known information"
        else:
            return "This step moves us toward the solution"


def _identify_concept(step: str, topic: str) -> str:
    """Identify the mathematical concept being used."""
    
    # Common concepts across topics
    if "=" in step and "both sides" in step:
        return "💡 Properties of Equality"
    elif "distribute" in step:
        return "💡 Distributive Property: a(b + c) = ab + ac"
    elif "factor" in step:
        return "💡 Factoring"
    elif "combine" in step or "like terms" in step:
        return "💡 Combining Like Terms"
    
    # Topic-specific
    if topic == "algebra":
        if "quadratic formula" in step:
            return "💡 Quadratic Formula: x = (-b ± √(b²-4ac)) / 2a"
        elif "substitution" in step:
            return "💡 Substitution Method"
        elif "elimination" in step:
            return "💡 Elimination Method"
        else:
            return "💡 Algebraic Manipulation"
    
    elif topic == "geometry":
        if "area" in step and "circle" in step:
            return "💡 Area of Circle: A = πr²"
        elif "area" in step and ("rectangle" in step or "square" in step):
            return "💡 Area of Rectangle: A = length × width"
        elif "volume" in step and "sphere" in step:
            return "💡 Volume of Sphere: V = (4/3)πr³"
        elif "volume" in step:
            return "💡 Volume = length × width × height"
        elif "pythagorean" in step:
            return "💡 Pythagorean Theorem: a² + b² = c²"
        else:
            return "💡 Geometric Formula"
    
    elif topic == "arithmetic":
        if "/" in step or "fraction" in step:
            return "💡 Fraction Operations"
        elif "%" in step:
            return "💡 Percentage Calculations"
        else:
            return "💡 Order of Operations (PEMDAS)"
    
    elif topic == "trigonometry":
        if "sin" in step or "cos" in step or "tan" in step:
            return "💡 Trigonometric Ratios (SOH-CAH-TOA)"
        else:
            return "💡 Trigonometry"
    
    elif topic == "statistics":
        if "mean" in step or "average" in step:
            return "💡 Mean = Sum / Count"
        elif "median" in step:
            return "💡 Median = Middle Value"
        else:
            return "💡 Statistical Measure"
    
    elif topic == "probability":
        return "💡 Probability = Favorable / Total"
    
    elif topic == "calculus":
        if "power rule" in step:
            return "💡 Power Rule: d/dx(x^n) = nx^(n-1)"
        elif "chain rule" in step:
            return "💡 Chain Rule: d/dx(f(g(x))) = f'(g(x))·g'(x)"
        else:
            return "💡 Calculus Operation"
    
    else:
        return "💡 Mathematical Operation"


def _common_mistake(step: str, topic: str) -> str:
    """Identify common mistakes students make on this type of step."""
    
    if topic == "algebra":
        if "both sides" in step:
            return "⚠️ Remember to do the SAME operation to BOTH sides"
        elif "distribute" in step:
            return "⚠️ Don't forget to multiply EVERY term inside the parentheses"
        elif "sign" in step or "-" in step:
            return "⚠️ Watch out for sign errors when moving terms"
        elif "divide" in step and "0" not in step:
            return "⚠️ Never divide by zero"
        elif "square root" in step:
            return "⚠️ Remember ±when taking square roots (unless context specifies positive)"
    
    elif topic == "geometry":
        if "radius" in step and "diameter" in step:
            return "⚠️ Don't confuse radius and diameter (diameter = 2 × radius)"
        elif "π" in step:
            return "⚠️ Use π ≈ 3.14 or leave as π, don't use 3"
        elif "square" in step:
            return "⚠️ Remember to square the value (multiply by itself)"
        elif "area" in step and "perimeter" in step:
            return "⚠️ Area and perimeter use different formulas"
    
    elif topic == "arithmetic":
        if "/" in step:
            return "⚠️ Division by zero is undefined"
        elif "order" in step.lower() or "pemdas" in step.lower():
            return "⚠️ Follow order of operations: Parentheses → Exponents → Multiply/Divide → Add/Subtract"
        elif "fraction" in step:
            return "⚠️ Find common denominator before adding/subtracting fractions"
    
    elif topic == "trigonometry":
        if "opposite" in step or "adjacent" in step:
            return "⚠️ Opposite and adjacent are relative to the specific angle you're using"
        elif "degree" in step or "radian" in step:
            return "⚠️ Check if your calculator is in degree or radian mode"
    
    elif topic == "calculus":
        if "power rule" in step:
            return "⚠️ Subtract 1 from the exponent after bringing it down"
        elif "chain rule" in step:
            return "⚠️ Don't forget to multiply by the derivative of the inner function"
    
    return ""  # No specific warning for this step


if __name__ == "__main__":
    # Test
    test_steps = [
        "1. Distribute: 3(x - 2) = 3x - 6",
        "2. Combine like terms: 3x - 6 + 7 = 3x + 1",
        "3. Add 6 to both sides",
        "4. Divide both sides by 3",
    ]
    
    enhanced = enhance_solution_steps(test_steps, "Solve: 3(x - 2) + 7 = 22", "algebra")
    
    for e in enhanced:
        print(f"\nStep: {e['step']}")
        print(f"  Why: {e['why']}")
        print(f"  Concept: {e['concept']}")
        if e['warning']:
            print(f"  Warning: {e['warning']}")
