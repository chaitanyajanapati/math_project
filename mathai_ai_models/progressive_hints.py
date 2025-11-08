"""Progressive hint generation module.

Provides 3-tier hint system:
- Tier 1 (Conceptual): What concept/formula to use
- Tier 2 (Strategic): What approach/strategy to take  
- Tier 3 (Procedural): Specific first step to begin

Each tier reveals more information while still requiring student work.
"""

import re
from typing import List, Tuple

def extract_numbers(question: str) -> List[str]:
    """Extract numeric values from question for use in hints."""
    return re.findall(r'-?\d+(?:\.\d+)?', question)

def extract_variables(question: str) -> List[str]:
    """Extract variable names (usually x, y, z) from question."""
    return list(set(re.findall(r'\b[xyz]\b', question.lower())))

def generate_progressive_hints(question: str, topic: str) -> Tuple[str, str, str]:
    """Generate 3 progressive hints for a question.
    
    Returns: (tier1_hint, tier2_hint, tier3_hint)
    """
    
    tier1 = _generate_conceptual_hint(question, topic)
    tier2 = _generate_strategic_hint(question, topic)
    tier3 = _generate_procedural_hint(question, topic)
    
    return (tier1, tier2, tier3)


def _generate_conceptual_hint(question: str, topic: str) -> str:
    """Tier 1: Conceptual hint - what concept/formula applies."""
    
    q_lower = question.lower()
    
    if topic == "algebra":
        if "system" in q_lower or ("=" in question and question.count("=") >= 2):
            return "💡 This is a system of equations. You'll need to use substitution or elimination to find both variables."
        elif "quadratic" in q_lower or "x^2" in question or "x²" in question:
            return "💡 This is a quadratic equation. Consider using the quadratic formula or factoring."
        elif "solve" in q_lower or "find x" in q_lower:
            return "💡 This is a linear equation. The goal is to isolate the variable on one side."
        elif "simplify" in q_lower:
            return "💡 Simplify by combining like terms and using the distributive property."
        else:
            return "💡 For equations, your goal is to isolate the variable by performing inverse operations on both sides."
    
    elif topic == "geometry":
        if "area" in q_lower and "circle" in q_lower:
            return "💡 Area of a circle: A = πr². Remember r is the radius."
        elif "area" in q_lower and ("rectangle" in q_lower or "square" in q_lower):
            return "💡 Area of a rectangle: A = length × width. For squares, all sides are equal."
        elif "perimeter" in q_lower:
            return "💡 Perimeter is the distance around the outside. Add all side lengths."
        elif "volume" in q_lower and "sphere" in q_lower:
            return "💡 Volume of a sphere: V = (4/3)πr³"
        elif "volume" in q_lower and ("cube" in q_lower or "rectangular" in q_lower):
            return "💡 Volume = length × width × height. For cubes, all dimensions are equal."
        elif "pythagorean" in q_lower or "hypotenuse" in q_lower or "right triangle" in q_lower:
            return "💡 Use the Pythagorean theorem: a² + b² = c², where c is the hypotenuse."
        elif "circumference" in q_lower:
            return "💡 Circumference of a circle: C = 2πr or C = πd"
        elif "surface area" in q_lower:
            return "💡 Surface area is the total area of all faces. Find the area of each face and add them."
        else:
            return "💡 Identify the shape and recall its formula. Most geometry problems need a specific formula."
    
    elif topic == "arithmetic":
        if "fraction" in q_lower or "/" in question:
            return "💡 For fractions: find common denominators to add/subtract, multiply straight across, flip and multiply to divide."
        elif "%" in question or "percent" in q_lower:
            return "💡 Convert percentages to decimals (divide by 100) or use the formula: (part/whole) × 100"
        elif "×" in question or "*" in question or "multiply" in q_lower:
            return "💡 Break multiplication into smaller steps if the numbers are large."
        elif "÷" in question or "/" in question or "divide" in q_lower:
            return "💡 Division is the opposite of multiplication. Check if you can simplify first."
        else:
            return "💡 Follow order of operations: Parentheses, Exponents, Multiplication/Division (left to right), Addition/Subtraction (left to right)."
    
    elif topic == "trigonometry":
        if "sin" in q_lower or "cos" in q_lower or "tan" in q_lower:
            return "💡 Remember SOH-CAH-TOA: Sin = Opposite/Hypotenuse, Cos = Adjacent/Hypotenuse, Tan = Opposite/Adjacent"
        elif "identity" in q_lower:
            return "💡 Use fundamental trig identities like sin²θ + cos²θ = 1"
        else:
            return "💡 Draw a triangle and label the sides relative to the angle you're working with."
    
    elif topic == "statistics":
        if "mean" in q_lower or "average" in q_lower:
            return "💡 Mean (average) = sum of all values ÷ number of values"
        elif "median" in q_lower:
            return "💡 Median is the middle value when numbers are arranged in order."
        elif "mode" in q_lower:
            return "💡 Mode is the value that appears most frequently."
        elif "standard deviation" in q_lower or "variance" in q_lower:
            return "💡 Standard deviation measures spread. Find the mean first, then calculate deviations."
        else:
            return "💡 Organize your data first. Most statistics problems need data to be sorted or summed."
    
    elif topic == "probability":
        if "independent" in q_lower:
            return "💡 For independent events, multiply their probabilities: P(A and B) = P(A) × P(B)"
        elif "or" in q_lower:
            return "💡 For 'or' events, add probabilities (subtract intersection if not mutually exclusive)."
        elif "conditional" in q_lower or "given" in q_lower:
            return "💡 Conditional probability: P(A|B) = P(A and B) / P(B)"
        else:
            return "💡 Probability = (favorable outcomes) / (total possible outcomes)"
    
    elif topic == "number_theory":
        if "prime" in q_lower:
            return "💡 A prime number is only divisible by 1 and itself. Test divisibility by small primes."
        elif "factor" in q_lower or "divisible" in q_lower:
            return "💡 Factorization: break the number down into its prime factors."
        elif "gcd" in q_lower or "greatest common" in q_lower:
            return "💡 Find GCD by listing factors or using the Euclidean algorithm."
        elif "lcm" in q_lower or "least common" in q_lower:
            return "💡 Find LCM using prime factorization or the formula: LCM(a,b) = (a×b)/GCD(a,b)"
        else:
            return "💡 Number theory often involves divisibility and prime factorization."
    
    elif topic == "calculus":
        if "derivative" in q_lower:
            return "💡 Use power rule: d/dx(x^n) = nx^(n-1). Don't forget the chain rule for compositions."
        elif "integral" in q_lower:
            return "💡 Integration is the reverse of differentiation. Add 1 to the exponent and divide."
        elif "limit" in q_lower:
            return "💡 For limits, try direct substitution first. If indeterminate, factor or use L'Hôpital's rule."
        else:
            return "💡 Identify whether you need to differentiate or integrate, then apply the appropriate rule."
    
    else:
        return "💡 Break the problem into smaller steps. What operation or concept is being tested?"


def _generate_strategic_hint(question: str, topic: str) -> str:
    """Tier 2: Strategic hint - what approach/strategy to use."""
    
    q_lower = question.lower()
    numbers = extract_numbers(question)
    variables = extract_variables(question)
    
    if topic == "algebra":
        if "solve" in q_lower and variables:
            var = variables[0] if variables else "x"
            if "(" in question:
                return f"📋 Strategy: First expand/simplify using the distributive property, then collect all terms with {var} on one side."
            else:
                return f"📋 Strategy: Move all terms containing {var} to the left side and constants to the right side."
        elif "system" in q_lower:
            return "📋 Strategy: Choose either substitution (solve one equation for a variable) or elimination (add/subtract equations)."
        elif "quadratic" in q_lower or "^2" in question:
            return "📋 Strategy: Try factoring first. If that doesn't work easily, use the quadratic formula."
        else:
            return "📋 Strategy: Perform inverse operations step by step to isolate the variable."
    
    elif topic == "geometry":
        if numbers:
            if len(numbers) == 1:
                return f"📋 Strategy: You're given one measurement ({numbers[0]}). Identify which formula applies and substitute this value."
            else:
                return f"📋 Strategy: You have measurements {', '.join(numbers[:3])}. Plug these into the appropriate formula."
        else:
            return "📋 Strategy: Identify the shape, recall its formula, and substitute the given values."
    
    elif topic == "arithmetic":
        if "/" in question or "fraction" in q_lower:
            return "📋 Strategy: For adding/subtracting fractions, find the least common denominator first. For multiplying, multiply numerators and denominators directly."
        elif "%" in question:
            return "📋 Strategy: Convert the percentage to a decimal by dividing by 100, then multiply or divide as needed."
        else:
            return "📋 Strategy: Follow PEMDAS order of operations. Work from innermost parentheses outward."
    
    elif topic == "trigonometry":
        return "📋 Strategy: Identify which sides of the triangle you know and which you need to find. Choose the trig ratio that connects them."
    
    elif topic == "statistics":
        if "mean" in q_lower:
            return "📋 Strategy: Add all the numbers together, then divide by how many numbers there are."
        elif "median" in q_lower:
            return "📋 Strategy: Sort the numbers from smallest to largest, then find the middle value."
        else:
            return "📋 Strategy: Organize your data (list it out or sort it) before calculating."
    
    elif topic == "probability":
        return "📋 Strategy: Count the favorable outcomes and total possible outcomes. Then form the fraction favorable/total."
    
    elif topic == "number_theory":
        if "factor" in q_lower or "prime" in q_lower:
            return "📋 Strategy: Start dividing by small primes (2, 3, 5, 7...) until you can't divide anymore."
        else:
            return "📋 Strategy: Break the problem into prime factorization, then use those factors."
    
    elif topic == "calculus":
        if "derivative" in q_lower:
            return "📋 Strategy: Apply the power rule to each term. If there's a composition, use the chain rule."
        elif "integral" in q_lower:
            return "📋 Strategy: Reverse the power rule - add 1 to exponent and divide. Don't forget + C for indefinite integrals."
        else:
            return "📋 Strategy: Identify the operation needed (differentiation or integration), then apply rules term by term."
    
    else:
        return "📋 Strategy: Start by identifying what you know and what you need to find. Work step by step toward the unknown."


def _generate_procedural_hint(question: str, topic: str) -> str:
    """Tier 3: Procedural hint - specific first step."""
    
    q_lower = question.lower()
    numbers = extract_numbers(question)
    variables = extract_variables(question)
    
    if topic == "algebra":
        if "solve" in q_lower and variables:
            var = variables[0] if variables else "x"
            # Look for parentheses
            if "(" in question:
                return f"🔧 First Step: Distribute/expand the parentheses. For example, 3(x - 2) becomes 3{var} - 6."
            # Look for variable on both sides
            elif question.count(var) >= 2 or question.count(var.upper()) >= 2:
                return f"🔧 First Step: Collect all {var} terms on one side by adding or subtracting {var} terms from both sides."
            else:
                # Simple equation - suggest first operation
                if "+" in question and numbers:
                    return f"🔧 First Step: Subtract {numbers[-1] if len(numbers) > 1 else numbers[0]} from both sides to start isolating {var}."
                elif "-" in question and numbers:
                    return f"🔧 First Step: Add {numbers[-1] if len(numbers) > 1 else numbers[0]} to both sides to eliminate the subtraction."
                else:
                    return f"🔧 First Step: Perform the inverse operation to start isolating {var}."
        elif "quadratic" in q_lower or "^2" in question:
            return "🔧 First Step: Set the equation equal to zero, then try to factor it into (x + a)(x + b) = 0."
        else:
            return "🔧 First Step: Simplify each side of the equation, combining like terms."
    
    elif topic == "geometry":
        if "area" in q_lower and "circle" in q_lower:
            if numbers:
                return f"🔧 First Step: Substitute r = {numbers[0]} into the formula A = πr², giving A = π × {numbers[0]}²."
            else:
                return "🔧 First Step: Identify the radius value and substitute it into A = πr²."
        elif "area" in q_lower:
            if len(numbers) >= 2:
                return f"🔧 First Step: Multiply the length ({numbers[0]}) by the width ({numbers[1]})."
            else:
                return "🔧 First Step: Identify the length and width, then multiply them together."
        elif "perimeter" in q_lower:
            if numbers:
                return f"🔧 First Step: Add all the sides: {' + '.join(numbers[:4])}."
            else:
                return "🔧 First Step: Add all the side lengths together."
        elif "volume" in q_lower:
            if len(numbers) >= 3:
                return f"🔧 First Step: Multiply length × width × height: {numbers[0]} × {numbers[1]} × {numbers[2]}."
            elif numbers:
                return f"🔧 First Step: Substitute the measurement ({numbers[0]}) into the volume formula."
            else:
                return "🔧 First Step: Identify all three dimensions and multiply them together."
        else:
            return "🔧 First Step: Write down the formula for this shape, then substitute the known values."
    
    elif topic == "arithmetic":
        if "/" in question and numbers and len(numbers) >= 2:
            return f"🔧 First Step: Divide {numbers[0]} by {numbers[1]}."
        elif "+" in question and "-" in question:
            return "🔧 First Step: Work through the operations from left to right, doing addition and subtraction in order."
        elif numbers and len(numbers) >= 2:
            return f"🔧 First Step: Start by calculating {numbers[0]} {question.split()[1] if len(question.split()) > 1 else '+'} {numbers[1]}."
        else:
            return "🔧 First Step: Start with the innermost parentheses or the first operation."
    
    elif topic == "trigonometry":
        return "🔧 First Step: Label the triangle sides as opposite, adjacent, and hypotenuse relative to the given angle."
    
    elif topic == "statistics":
        if "mean" in q_lower and numbers:
            return f"🔧 First Step: Add all the numbers: {' + '.join(numbers)}."
        elif "median" in q_lower and numbers:
            return f"🔧 First Step: Sort the numbers from least to greatest: {', '.join(sorted(numbers, key=float))}."
        else:
            return "🔧 First Step: Write out all the data values in a list."
    
    elif topic == "probability":
        return "🔧 First Step: Count how many total possible outcomes there are."
    
    elif topic == "number_theory":
        if numbers and len(numbers) >= 1:
            num = int(float(numbers[0]))
            if num % 2 == 0:
                return f"🔧 First Step: Since {num} is even, divide it by 2."
            else:
                return f"🔧 First Step: Test if {num} is divisible by small primes like 3, 5, or 7."
        else:
            return "🔧 First Step: Start testing divisibility by 2, then 3, then 5, etc."
    
    elif topic == "calculus":
        if "derivative" in q_lower:
            return "🔧 First Step: Apply the power rule to each term: bring down the exponent and reduce it by 1."
        elif "integral" in q_lower:
            return "🔧 First Step: Add 1 to each exponent, then divide by the new exponent."
        else:
            return "🔧 First Step: Identify each term and apply the appropriate differentiation or integration rule."
    
    else:
        return "🔧 First Step: Write down what you know and what you need to find."


if __name__ == "__main__":
    # Test the hint system
    test_questions = [
        ("Solve for x: 3x + 7 = 22", "algebra"),
        ("Find the area of a circle with radius 5 cm", "geometry"),
        ("What is 3/4 + 1/2?", "arithmetic"),
    ]
    
    for question, topic in test_questions:
        print(f"\nQuestion: {question}")
        print(f"Topic: {topic}")
        tier1, tier2, tier3 = generate_progressive_hints(question, topic)
        print(f"  Tier 1 (Conceptual): {tier1}")
        print(f"  Tier 2 (Strategic): {tier2}")
        print(f"  Tier 3 (Procedural): {tier3}")
