"""
Smart Number Generation for Math Questions
Generates grade-appropriate numbers that lead to 'nice' answers
"""

import random
from typing import Dict, Tuple, Any, List


class SmartNumberGenerator:
    """Generates numbers appropriate for grade level and difficulty"""
    
    @staticmethod
    def get_config(grade: int, difficulty: str, topic: str) -> Dict[str, Any]:
        """Get number generation configuration for given parameters"""
        
        config = {
            "range": (1, 10),
            "allow_decimals": False,
            "allow_fractions": False,
            "allow_negatives": False,
            "decimal_places": 1,
            "nice_answers": True,  # Prefer whole number results
        }
        
        # Adjust based on grade
        if grade <= 3:
            config["range"] = (1, 20)
            config["nice_answers"] = True
        elif grade <= 5:
            config["range"] = (5, 50)
            config["allow_decimals"] = difficulty != "easy"
            config["nice_answers"] = True
        elif grade <= 8:
            config["range"] = (10, 100)
            config["allow_decimals"] = True
            config["allow_fractions"] = difficulty in ["medium", "hard"]
            config["allow_negatives"] = difficulty == "hard"
        elif grade <= 10:
            config["range"] = (20, 200)
            config["allow_decimals"] = True
            config["allow_fractions"] = True
            config["allow_negatives"] = True
            config["decimal_places"] = 2
        else:  # grades 11-12
            config["range"] = (50, 500)
            config["allow_decimals"] = True
            config["allow_fractions"] = True
            config["allow_negatives"] = True
            config["decimal_places"] = 2
        
        # Adjust based on difficulty
        if difficulty == "easy":
            config["range"] = (config["range"][0], config["range"][1] // 2)
            config["nice_answers"] = True
            config["allow_negatives"] = False
        elif difficulty == "hard":
            config["range"] = (config["range"][0], config["range"][1] * 2)
            config["nice_answers"] = False
        
        # Topic-specific adjustments
        if topic == "geometry":
            config["allow_negatives"] = False  # No negative lengths
            config["range"] = (min(config["range"][0], 1), min(config["range"][1], 200))
        elif topic == "arithmetic":
            # Keep numbers manageable for mental math
            if grade <= 5:
                config["range"] = (1, 20)
        
        return config
    
    @staticmethod
    def generate_number(config: Dict[str, Any]) -> float:
        """Generate a single number based on configuration"""
        
        low, high = config["range"]
        
        # Generate base number
        num = random.randint(low, high)
        
        # Add decimal if allowed
        if config.get("allow_decimals") and random.random() < 0.3:
            decimal_places = config.get("decimal_places", 1)
            num += round(random.random(), decimal_places)
        
        # Make negative if allowed
        if config.get("allow_negatives") and random.random() < 0.2:
            num = -num
        
        return num
    
    @staticmethod
    def generate_fraction(config: Dict[str, Any]) -> Tuple[int, int]:
        """Generate a reasonable fraction"""
        
        # Common denominators for nice fractions
        common_denominators = [2, 3, 4, 5, 6, 8, 10, 12]
        
        if config.get("nice_answers", True):
            denominator = random.choice(common_denominators[:5])  # Simpler fractions
        else:
            denominator = random.choice(common_denominators)
        
        numerator = random.randint(1, denominator - 1)
        
        # Simplify if needed
        from math import gcd
        g = gcd(numerator, denominator)
        return (numerator // g, denominator // g)
    
    @staticmethod
    def generate_for_equation(grade: int, difficulty: str) -> Dict[str, int]:
        """
        Generate numbers for algebra equations that result in nice solutions
        
        Example: For ax + b = c, generate so that x is a whole number
        """
        
        config = SmartNumberGenerator.get_config(grade, difficulty, "algebra")
        
        # For linear equation: ax + b = c
        # We'll choose x first (the answer), then calculate b and c
        
        if difficulty == "easy":
            x = random.randint(1, 10)  # Simple answer
            a = random.randint(2, 10)
            b = random.randint(1, 20)
        elif difficulty == "medium":
            x = random.randint(1, 20)
            a = random.randint(2, 15)
            b = random.randint(-20, 20)
        else:  # hard
            x = random.randint(-20, 20)
            a = random.randint(2, 20)
            b = random.randint(-50, 50)
        
        c = a * x + b  # Calculate c so equation has integer solution
        
        return {"a": a, "b": b, "c": c, "x": x}
    
    @staticmethod
    def generate_for_geometry(shape: str, grade: int, difficulty: str) -> Dict[str, float]:
        """Generate appropriate measurements for geometry problems"""
        
        config = SmartNumberGenerator.get_config(grade, difficulty, "geometry")
        
        if shape == "rectangle":
            if difficulty == "easy":
                length = random.randint(5, 20)
                width = random.randint(3, 15)
            else:
                length = random.randint(10, 50)
                width = random.randint(5, 30)
            
            return {
                "length": length,
                "width": width,
                "area": length * width,
                "perimeter": 2 * (length + width)
            }
        
        elif shape == "circle":
            if difficulty == "easy":
                radius = random.choice([5, 10, 15, 20])  # Nice numbers
            else:
                radius = random.randint(5, 50)
            
            import math
            return {
                "radius": radius,
                "diameter": 2 * radius,
                "area": round(math.pi * radius ** 2, 2),
                "circumference": round(2 * math.pi * radius, 2)
            }
        
        elif shape == "cube":
            if difficulty == "easy":
                edge = random.choice([2, 3, 4, 5, 10])
            else:
                edge = random.randint(5, 20)
            
            return {
                "edge": edge,
                "volume": edge ** 3,
                "surface_area": 6 * edge ** 2
            }
        
        elif shape == "right_triangle":
            # Generate Pythagorean triples for nice answers
            pythagorean_triples = [
                (3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25),
                (6, 8, 10), (9, 12, 15), (12, 16, 20), (15, 20, 25)
            ]
            
            if difficulty == "easy":
                triple = random.choice(pythagorean_triples[:4])
            else:
                triple = random.choice(pythagorean_triples)
            
            return {
                "leg1": triple[0],
                "leg2": triple[1],
                "hypotenuse": triple[2]
            }
        
        return {}
    
    @staticmethod
    def generate_for_arithmetic(operation: str, grade: int, difficulty: str) -> Dict[str, Any]:
        """Generate numbers for arithmetic operations"""
        
        config = SmartNumberGenerator.get_config(grade, difficulty, "arithmetic")
        low, high = config["range"]
        
        if operation == "addition":
            a = random.randint(low, high)
            b = random.randint(low, high)
            return {"a": a, "b": b, "answer": a + b}
        
        elif operation == "subtraction":
            # Ensure non-negative result for easy questions
            if difficulty == "easy" or grade <= 5:
                b = random.randint(low, high)
                a = random.randint(b, high + b)  # a >= b
            else:
                a = random.randint(low, high)
                b = random.randint(low, high)
            
            return {"a": a, "b": b, "answer": a - b}
        
        elif operation == "multiplication":
            if difficulty == "easy":
                a = random.randint(2, 10)
                b = random.randint(2, 10)
            else:
                a = random.randint(low // 2, high // 2)
                b = random.randint(2, 20)
            
            return {"a": a, "b": b, "answer": a * b}
        
        elif operation == "division":
            # Generate so division is exact
            if difficulty == "easy":
                b = random.randint(2, 10)
                quotient = random.randint(2, 10)
            else:
                b = random.randint(2, 20)
                quotient = random.randint(2, high // b)
            
            a = b * quotient  # Ensures exact division
            
            return {"a": a, "b": b, "answer": quotient}
        
        elif operation == "fraction_addition":
            # Use common denominators
            if difficulty == "easy":
                denom = random.choice([2, 4, 5, 10])
            else:
                denom = random.choice([2, 3, 4, 5, 6, 8, 10, 12])
            
            num1 = random.randint(1, denom - 1)
            num2 = random.randint(1, denom - 1)
            
            return {
                "num1": num1,
                "denom1": denom,
                "num2": num2,
                "denom2": denom,
                "answer_num": num1 + num2,
                "answer_denom": denom
            }
        
        return {}
    
    @staticmethod
    def format_number(num: float, force_decimal: bool = False) -> str:
        """Format number for display"""
        
        if isinstance(num, int) or num == int(num):
            return str(int(num))
        
        if force_decimal or num != int(num):
            # Remove trailing zeros
            formatted = f"{num:.10f}".rstrip('0').rstrip('.')
            return formatted
        
        return str(num)


# Convenient function to get smart numbers for template substitution
def get_smart_numbers(template: str, grade: int, difficulty: str, topic: str) -> Dict[str, Any]:
    """
    Analyze template and generate appropriate numbers
    
    Example:
        template: "Solve: {a}x + {b} = {c}"
        Returns: {"a": 3, "b": 5, "c": 14}  # where x = 3
    """
    
    config = SmartNumberGenerator.get_config(grade, difficulty, topic)
    
    # Count how many unique placeholders in template
    import re
    placeholders = set(re.findall(r'\{([a-z])\}', template))
    
    numbers = {}
    
    # Special handling for common patterns
    if topic == "algebra" and "{a}x" in template:
        # Linear equation
        eq_nums = SmartNumberGenerator.generate_for_equation(grade, difficulty)
        numbers.update(eq_nums)
    
    elif topic == "geometry":
        # Try to detect shape
        if "rectangle" in template.lower():
            numbers.update(SmartNumberGenerator.generate_for_geometry("rectangle", grade, difficulty))
        elif "circle" in template.lower():
            numbers.update(SmartNumberGenerator.generate_for_geometry("circle", grade, difficulty))
        elif "triangle" in template.lower():
            numbers.update(SmartNumberGenerator.generate_for_geometry("right_triangle", grade, difficulty))
        elif "cube" in template.lower():
            numbers.update(SmartNumberGenerator.generate_for_geometry("cube", grade, difficulty))
    
    elif topic == "arithmetic":
        # Detect operation
        if "+" in template and "-" not in template:
            numbers.update(SmartNumberGenerator.generate_for_arithmetic("addition", grade, difficulty))
        elif "-" in template and "+" not in template:
            numbers.update(SmartNumberGenerator.generate_for_arithmetic("subtraction", grade, difficulty))
        elif "×" in template or "*" in template:
            numbers.update(SmartNumberGenerator.generate_for_arithmetic("multiplication", grade, difficulty))
        elif "÷" in template or "/" in template:
            numbers.update(SmartNumberGenerator.generate_for_arithmetic("division", grade, difficulty))
    
    # Fill in any remaining placeholders with generic numbers
    for placeholder in placeholders:
        if placeholder not in numbers:
            numbers[placeholder] = SmartNumberGenerator.generate_number(config)
    
    return numbers


if __name__ == "__main__":
    # Test smart number generation
    print("Testing Smart Number Generator\n")
    
    # Test algebra
    print("Algebra (Grade 8, Medium):")
    nums = get_smart_numbers("Solve: {a}x + {b} = {c}", 8, "medium", "algebra")
    print(f"  Numbers: {nums}")
    print(f"  Question: Solve: {nums['a']}x + {nums['b']} = {nums['c']}")
    print(f"  Answer: x = {nums.get('x', 'unknown')}\n")
    
    # Test geometry
    print("Geometry (Grade 6, Easy):")
    nums = get_smart_numbers("Find area of rectangle {a} cm by {b} cm", 6, "easy", "geometry")
    print(f"  Numbers: {nums}")
    print(f"  Area: {nums.get('area', 'N/A')}\n")
    
    # Test arithmetic
    print("Arithmetic (Grade 4, Easy):")
    nums = get_smart_numbers("What is {a} + {b}?", 4, "easy", "arithmetic")
    print(f"  Numbers: {nums}")
    print(f"  Answer: {nums.get('answer', 'N/A')}\n")
