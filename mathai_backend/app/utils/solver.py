"""
solver.py
---------
Deterministic symbolic math solver using SymPy.
Returns exact answers for common patterns when possible, with step-by-step explanations.
"""

import re
from typing import Tuple, List, Optional
import sympy as sp
from sympy import symbols, solve, Eq, simplify, latex
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application


def safe_parse_expr(expr_str: str):
    """Parse a mathematical expression string safely."""
    try:
        transformations = standard_transformations + (implicit_multiplication_application,)
        return parse_expr(expr_str, transformations=transformations)
    except Exception:
        return None


def solve_linear_equation(question: str) -> Optional[Tuple[str, List[str]]]:
    """Solve simple linear equations like 'Solve for x: 2x + 3 = 11'."""
    try:
        # Extract equation pattern: something = something
        match = re.search(r':\s*(.+?)\s*=\s*(.+?)(?:\?|$)', question)
        if not match:
            return None
        
        left, right = match.group(1).strip(), match.group(2).strip()
        
        # Parse both sides
        left_expr = safe_parse_expr(left)
        right_expr = safe_parse_expr(right)
        
        if left_expr is None or right_expr is None:
            return None
        
        # Find the variable (usually x, but could be y, z, etc.)
        free_symbols = list((left_expr.free_symbols | right_expr.free_symbols))
        if len(free_symbols) != 1:
            return None
        
        var = free_symbols[0]
        
        # Solve equation
        solutions = solve(Eq(left_expr, right_expr), var)
        
        if not solutions:
            return None
        
        # Format answer
        if len(solutions) == 1:
            answer = str(solutions[0])
        else:
            answer = ", ".join(str(s) for s in solutions)
        
        # Generate steps
        steps = [
            f"1. Start with the equation: {left} = {right}",
            f"2. Rearrange to isolate {var}",
            f"3. Simplify to get {var} = {answer}"
        ]
        
        return answer, steps
    
    except Exception as e:
        print(f"Error in solve_linear_equation: {e}")
        return None


def solve_quadratic_equation(question: str) -> Optional[Tuple[str, List[str]]]:
    """Solve quadratic equations like 'Solve: x² - 5x + 6 = 0'."""
    try:
        match = re.search(r':\s*(.+?)\s*=\s*(.+?)(?:\?|$)', question)
        if not match:
            return None
        
        left, right = match.group(1).strip(), match.group(2).strip()
        
        # Replace common patterns
        left = left.replace('²', '**2').replace('^2', '**2')
        right = right.replace('²', '**2').replace('^2', '**2')
        
        left_expr = safe_parse_expr(left)
        right_expr = safe_parse_expr(right)
        
        if left_expr is None or right_expr is None:
            return None
        
        free_symbols = list((left_expr.free_symbols | right_expr.free_symbols))
        if len(free_symbols) != 1:
            return None
        
        var = free_symbols[0]
        
        # Solve
        solutions = solve(Eq(left_expr, right_expr), var)
        
        if not solutions:
            return None
        
        # Format answer
        answer = ", ".join(str(s) for s in solutions)
        
        steps = [
            f"1. Write the equation: {left} = {right}",
            f"2. Rearrange to standard form",
            f"3. Use quadratic formula or factoring",
            f"4. Solutions: {var} = {answer}"
        ]
        
        return answer, steps
    
    except Exception as e:
        print(f"Error in solve_quadratic_equation: {e}")
        return None


def solve_geometry_area(question: str) -> Optional[Tuple[str, List[str]]]:
    """Solve area problems for rectangles, triangles, circles, etc."""
    try:
        q_lower = question.lower()
        
        # Extract numbers from question
        numbers = re.findall(r'\d+\.?\d*', question)
        if not numbers:
            return None
        
        # Rectangle area
        if 'rectangle' in q_lower and 'area' in q_lower:
            if len(numbers) >= 2:
                length, width = float(numbers[0]), float(numbers[1])
                area = length * width
                steps = [
                    f"1. Formula for rectangle area: Area = length × width",
                    f"2. Substitute values: Area = {length} × {width}",
                    f"3. Calculate: Area = {area}"
                ]
                return str(area), steps
        
        # Square area
        if 'square' in q_lower and 'area' in q_lower:
            if len(numbers) >= 1:
                side = float(numbers[0])
                area = side * side
                steps = [
                    f"1. Formula for square area: Area = side²",
                    f"2. Substitute: Area = {side}²",
                    f"3. Calculate: Area = {area}"
                ]
                return str(area), steps
        
        # Triangle area
        if 'triangle' in q_lower and 'area' in q_lower:
            if len(numbers) >= 2:
                base, height = float(numbers[0]), float(numbers[1])
                area = 0.5 * base * height
                steps = [
                    f"1. Formula for triangle area: Area = ½ × base × height",
                    f"2. Substitute: Area = ½ × {base} × {height}",
                    f"3. Calculate: Area = {area}"
                ]
                return str(area), steps
        
        # Circle area
        if 'circle' in q_lower and 'area' in q_lower:
            if len(numbers) >= 1:
                radius = float(numbers[0])
                area = float(sp.pi * radius**2)
                steps = [
                    f"1. Formula for circle area: Area = πr²",
                    f"2. Substitute: Area = π × {radius}²",
                    f"3. Calculate: Area ≈ {area:.2f}"
                ]
                return f"{area:.2f}", steps
        
        # Cube volume
        if 'cube' in q_lower and 'volume' in q_lower:
            if len(numbers) >= 1:
                side = float(numbers[0])
                volume = side ** 3
                steps = [
                    f"1. Formula for cube volume: Volume = side³",
                    f"2. Substitute: Volume = {side}³",
                    f"3. Calculate: Volume = {volume}"
                ]
                return str(volume), steps
        
        # Cylinder volume
        if 'cylinder' in q_lower and 'volume' in q_lower:
            if len(numbers) >= 2:
                radius, height = float(numbers[0]), float(numbers[1])
                volume = float(sp.pi * radius**2 * height)
                steps = [
                    f"1. Formula for cylinder volume: Volume = πr²h",
                    f"2. Substitute: Volume = π × {radius}² × {height}",
                    f"3. Calculate: Volume ≈ {volume:.2f}"
                ]
                return f"{volume:.2f}", steps
        
        return None
    
    except Exception as e:
        print(f"Error in solve_geometry_area: {e}")
        return None


def solve_percentage(question: str) -> Optional[Tuple[str, List[str]]]:
    """Solve percentage problems like 'What is 25% of 80?'."""
    try:
        q_lower = question.lower()
        
        # Pattern: "X% of Y"
        match = re.search(r'(\d+\.?\d*)%?\s+(?:percent\s+)?of\s+(\d+\.?\d*)', q_lower)
        if match:
            percent = float(match.group(1))
            total = float(match.group(2))
            result = (percent / 100) * total
            
            steps = [
                f"1. Convert percentage to decimal: {percent}% = {percent/100}",
                f"2. Multiply by the total: {percent/100} × {total}",
                f"3. Calculate: {result}"
            ]
            return str(result), steps
        
        # Pattern: "X is what percent of Y"
        match = re.search(r'(\d+\.?\d*)\s+is\s+(?:what|how\s+much)\s+percent\s+of\s+(\d+\.?\d*)', q_lower)
        if match:
            part = float(match.group(1))
            whole = float(match.group(2))
            percent = (part / whole) * 100
            
            steps = [
                f"1. Formula: (part ÷ whole) × 100",
                f"2. Substitute: ({part} ÷ {whole}) × 100",
                f"3. Calculate: {percent}%"
            ]
            return f"{percent}", steps
        
        return None
    
    except Exception as e:
        print(f"Error in solve_percentage: {e}")
        return None


def solve_arithmetic(question: str) -> Optional[Tuple[str, List[str]]]:
    """Solve basic arithmetic problems."""
    try:
        # Extract expression after "what is" or similar
        q_lower = question.lower()
        
        # Pattern: "What is X + Y?" or "Calculate X * Y"
        match = re.search(r'(?:what is|calculate|find|compute)\s+(.+?)(?:\?|$)', q_lower, re.IGNORECASE)
        if not match:
            return None
        
        expr_str = match.group(1).strip()
        
        # Replace common symbols
        expr_str = expr_str.replace('×', '*').replace('÷', '/')
        
        # Try to parse and evaluate
        expr = safe_parse_expr(expr_str)
        if expr is None or expr.free_symbols:
            return None
        
        result = float(expr)
        
        steps = [
            f"1. Expression: {expr_str}",
            f"2. Evaluate: {result}"
        ]
        
        return str(result), steps
    
    except Exception as e:
        print(f"Error in solve_arithmetic: {e}")
        return None


def solve_question(question: str, topic: str) -> Optional[Tuple[str, List[str]]]:
    """
    Main entry point for symbolic solver.
    Try to solve the question deterministically based on topic and pattern.
    
    Returns:
        (answer, steps) if solvable, None otherwise
    """
    # Try solvers based on topic
    if topic in ("algebra", "equations"):
        # Try quadratic first (more specific), then linear
        result = solve_quadratic_equation(question)
        if result:
            return result
        result = solve_linear_equation(question)
        if result:
            return result
    
    if topic in ("geometry", "mensuration"):
        result = solve_geometry_area(question)
        if result:
            return result
    
    if topic in ("percentages", "percentage"):
        result = solve_percentage(question)
        if result:
            return result
    
    if topic in ("arithmetic", "basic_arithmetic"):
        result = solve_arithmetic(question)
        if result:
            return result
    
    # Fallback: try all solvers regardless of topic
    for solver_func in [
        solve_linear_equation,
        solve_quadratic_equation,
        solve_geometry_area,
        solve_percentage,
        solve_arithmetic
    ]:
        result = solver_func(question)
        if result:
            return result
    
    return None


if __name__ == "__main__":
    # Quick tests
    test_cases = [
        ("Solve for x: 2x + 3 = 11", "algebra"),
        ("Find the area of a rectangle with length 6 cm and width 4 cm", "geometry"),
        ("What is 25% of 80?", "percentages"),
        ("Solve: x² - 5x + 6 = 0", "algebra"),
    ]
    
    for q, topic in test_cases:
        print(f"\nQuestion: {q}")
        result = solve_question(q, topic)
        if result:
            ans, steps = result
            print(f"Answer: {ans}")
            print("Steps:")
            for step in steps:
                print(f"  {step}")
        else:
            print("  Could not solve")
