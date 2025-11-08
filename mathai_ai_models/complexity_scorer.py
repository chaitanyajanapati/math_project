"""
Complexity Scoring System for Math Questions
Objectively measures question difficulty
"""

import re
from typing import Dict, List, Any


class ComplexityScorer:
    """
    Calculates objective complexity score for math questions
    Score ranges:
        0-30: Very Easy
        31-60: Easy  
        61-90: Medium
        91-120: Hard
        121+: Very Hard
    """
    
    @staticmethod
    def calculate_complexity(
        question: str,
        topic: str,
        answer: Any = None,
        operations: List[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate complexity score and provide breakdown
        
        Returns:
            - score: int (total complexity score)
            - level: str (difficulty level name)
            - breakdown: dict (score components)
        """
        
        breakdown = {
            "operation_count": 0,
            "operation_types": 0,
            "number_size": 0,
            "decimal_complexity": 0,
            "fraction_complexity": 0,
            "variable_complexity": 0,
            "steps_required": 0,
            "word_problem_bonus": 0,
            "concept_complexity": 0
        }
        
        # 1. Count operations
        op_symbols = ['+', '-', '×', '*', '÷', '/', '=', '^', '²', '³']
        operation_count = sum(question.count(op) for op in op_symbols)
        breakdown["operation_count"] = operation_count * 10
        
        # 2. Variety of operation types
        ops_found = set()
        if '+' in question: ops_found.add('addition')
        if '-' in question: ops_found.add('subtraction')
        if '×' in question or '*' in question: ops_found.add('multiplication')
        if '÷' in question or '/' in question: ops_found.add('division')
        if '^' in question or '²' in question: ops_found.add('exponent')
        breakdown["operation_types"] = len(ops_found) * 10
        
        # 3. Number size complexity
        numbers = [float(n) for n in re.findall(r'\d+\.?\d*', question)]
        if numbers:
            max_num = max(numbers)
            if max_num < 10:
                breakdown["number_size"] = 0
            elif max_num < 100:
                breakdown["number_size"] = 10
            elif max_num < 1000:
                breakdown["number_size"] = 20
            else:
                breakdown["number_size"] = 30
        
        # 4. Decimal complexity
        decimal_count = len(re.findall(r'\d+\.\d+', question))
        breakdown["decimal_complexity"] = decimal_count * 15
        
        # 5. Fraction complexity
        fraction_count = len(re.findall(r'\d+/\d+', question))
        breakdown["fraction_complexity"] = fraction_count * 20
        
        # 6. Variable complexity
        variables = re.findall(r'\b[a-z]\b', question.lower())
        unique_vars = len(set(variables))
        breakdown["variable_complexity"] = unique_vars * 15
        
        # 7. Steps required (estimated)
        steps = ComplexityScorer._estimate_steps(question, topic)
        breakdown["steps_required"] = steps * 15
        
        # 8. Word problem bonus
        word_indicators = ['buy', 'sell', 'cost', 'price', 'has', 'gets', 'people', 'distance']
        is_word_problem = any(indicator in question.lower() for indicator in word_indicators)
        if is_word_problem:
            breakdown["word_problem_bonus"] = 20
        
        # 9. Concept complexity
        advanced_concepts = {
            'quadratic': 40,
            'system': 35,
            'logarithm': 45,
            'trigonometry': 35,
            'derivative': 50,
            'integral': 50,
            'factorial': 30,
            'permutation': 35,
            'combination': 35,
            'probability': 25,
            'volume': 20,
            'surface area': 25,
            'pythagorean': 25,
            'slope': 20,
            'intercept': 20
        }
        
        question_lower = question.lower()
        for concept, points in advanced_concepts.items():
            if concept in question_lower:
                breakdown["concept_complexity"] = max(breakdown["concept_complexity"], points)
                break
        
        # Calculate total score
        total_score = sum(breakdown.values())
        
        # Determine level
        if total_score < 31:
            level = "very_easy"
        elif total_score < 61:
            level = "easy"
        elif total_score < 91:
            level = "medium"
        elif total_score < 121:
            level = "hard"
        else:
            level = "very_hard"
        
        return {
            "score": total_score,
            "level": level,
            "breakdown": breakdown,
            "normalized": min(1.0, total_score / 150)  # Normalize to 0-1
        }
    
    @staticmethod
    def _estimate_steps(question: str, topic: str) -> int:
        """Estimate number of steps required to solve"""
        
        # Base steps
        steps = 1
        
        # Count operations as proxy for steps
        operations = question.count('+') + question.count('-') + question.count('×') + \
                    question.count('*') + question.count('÷') + question.count('/')
        steps += operations
        
        # Parentheses indicate multi-step
        if '(' in question:
            steps += question.count('(')
        
        # Topic-specific adjustments
        if topic == "algebra":
            if 'solve' in question.lower():
                steps += 1
            if any(word in question.lower() for word in ['simplify', 'expand', 'factor']):
                steps += 2
        
        elif topic == "geometry":
            # Geometry often requires formula recall + calculation
            steps += 1
            if 'volume' in question.lower() or 'surface area' in question.lower():
                steps += 1
        
        # Multi-part questions
        if ' and ' in question.lower() or ', then' in question.lower():
            steps += 2
        
        return min(steps, 10)  # Cap at 10
    
    @staticmethod
    def match_difficulty_to_grade(
        complexity_score: int,
        grade: int
    ) -> str:
        """
        Determine if complexity matches expected difficulty for grade
        
        Returns: "too_easy", "appropriate", or "too_hard"
        """
        
        # Expected complexity ranges by grade
        grade_expectations = {
            (1, 3): (0, 50),
            (4, 5): (20, 70),
            (6, 8): (40, 100),
            (9, 10): (60, 130),
            (11, 12): (80, 160)
        }
        
        for grade_range, (min_complexity, max_complexity) in grade_expectations.items():
            if grade_range[0] <= grade <= grade_range[1]:
                if complexity_score < min_complexity - 20:
                    return "too_easy"
                elif complexity_score > max_complexity + 20:
                    return "too_hard"
                else:
                    return "appropriate"
        
        return "appropriate"  # Default
    
    @staticmethod
    def suggest_difficulty_level(complexity_score: int) -> str:
        """Suggest difficulty label based on complexity score"""
        
        if complexity_score < 31:
            return "easy"
        elif complexity_score < 61:
            return "easy-medium"
        elif complexity_score < 91:
            return "medium"
        elif complexity_score < 121:
            return "medium-hard"
        else:
            return "hard"
    
    @staticmethod
    def compare_questions(
        question1: str,
        question2: str,
        topic: str
    ) -> Dict[str, Any]:
        """Compare complexity of two questions"""
        
        c1 = ComplexityScorer.calculate_complexity(question1, topic)
        c2 = ComplexityScorer.calculate_complexity(question2, topic)
        
        difference = c1["score"] - c2["score"]
        
        if abs(difference) < 10:
            comparison = "similar difficulty"
        elif difference > 0:
            comparison = f"question 1 is harder (+{difference} points)"
        else:
            comparison = f"question 2 is harder (+{abs(difference)} points)"
        
        return {
            "question1_score": c1["score"],
            "question2_score": c2["score"],
            "difference": difference,
            "comparison": comparison,
            "question1_level": c1["level"],
            "question2_level": c2["level"]
        }


if __name__ == "__main__":
    print("Testing Complexity Scorer\n")
    print("=" * 70)
    
    # Test various questions
    test_cases = [
        ("What is 5 + 3?", "arithmetic", "Very easy addition"),
        ("Solve: 3x + 7 = 22", "algebra", "Easy linear equation"),
        ("Find the area of a circle with radius 5 cm. Use π ≈ 3.14.", "geometry", "Medium geometry"),
        ("Solve: 2x² - 5x + 3 = 0", "algebra", "Hard quadratic"),
        ("John buys 3 books at $12 each and 2 pens at $3 each. If he pays with $50, how much change?", 
         "arithmetic", "Complex word problem"),
    ]
    
    for question, topic, description in test_cases:
        print(f"\n{description}:")
        print(f"Q: {question}")
        
        result = ComplexityScorer.calculate_complexity(question, topic)
        print(f"Score: {result['score']} ({result['level']})")
        print(f"Breakdown: {result['breakdown']}")
        print("-" * 70)
    
    # Test comparison
    print("\n\nCOMPARISON TEST:")
    comparison = ComplexityScorer.compare_questions(
        "What is 5 + 3?",
        "Solve: 3x + 7 = 22",
        "arithmetic"
    )
    print(f"Comparison: {comparison['comparison']}")
    print(f"Q1: {comparison['question1_score']} ({comparison['question1_level']})")
    print(f"Q2: {comparison['question2_score']} ({comparison['question2_level']})")
