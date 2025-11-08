"""
Question Validator - Ensures generated questions meet quality standards
"""

import re
from typing import Dict, List, Tuple, Optional, Any


class QuestionValidator:
    """Validates math questions for quality, correctness, and appropriateness"""
    
    @staticmethod
    def validate(
        question: str,
        answer: Any,
        steps: List[str],
        grade: int,
        difficulty: str,
        topic: str
    ) -> Dict[str, Any]:
        """
        Run all validation checks on a question
        
        Returns dict with:
            - checks: dict of individual check results
            - overall_quality: float 0-1
            - issues: list of problems found
            - passed: bool whether question meets minimum standards
        """
        
        checks = {
            "has_question": QuestionValidator._check_has_question(question),
            "has_answer": QuestionValidator._check_has_answer(answer),
            "answer_reasonable": QuestionValidator._check_answer_reasonable(answer, topic),
            "no_math_errors": QuestionValidator._check_no_math_errors(question, answer, topic),
            "clear_wording": QuestionValidator._check_clear_wording(question),
            "appropriate_length": QuestionValidator._check_length(question, grade),
            "no_negatives_in_geometry": QuestionValidator._check_geometry_values(question, answer, topic),
            "has_solution_steps": len(steps) > 0 if answer else True,
            "grade_appropriate": QuestionValidator._check_grade_appropriate(question, grade, difficulty),
        }
        
        # Calculate overall quality score
        quality_score = sum(1 for v in checks.values() if v) / len(checks)
        
        # Identify issues
        issues = [k for k, v in checks.items() if not v]
        
        # Determine if passes minimum standards
        critical_checks = ["has_question", "has_answer", "no_math_errors", "answer_reasonable"]
        passed = all(checks[k] for k in critical_checks if k in checks)
        
        return {
            "checks": checks,
            "overall_quality": quality_score,
            "issues": issues,
            "passed": passed,
            "warnings": QuestionValidator._generate_warnings(checks, issues)
        }
    
    @staticmethod
    def _check_has_question(question: str) -> bool:
        """Check if question text exists and is meaningful"""
        if not question or len(question) < 10:
            return False
        
        # Should have some mathematical content
        math_indicators = ['solve', 'find', 'calculate', 'what', 'how', 'is', '=', '+', '-', '×', '÷', 'x']
        return any(indicator in question.lower() for indicator in math_indicators)
    
    @staticmethod
    def _check_has_answer(answer: Any) -> bool:
        """Check if answer exists and is not empty"""
        if answer is None or answer == "":
            return False
        
        # Convert to string and check
        answer_str = str(answer).strip()
        return len(answer_str) > 0 and answer_str.lower() not in ['none', 'nan', 'null']
    
    @staticmethod
    def _check_answer_reasonable(answer: Any, topic: str) -> bool:
        """Check if answer value is reasonable"""
        try:
            # Try to convert to float
            if isinstance(answer, str):
                # Remove common formatting
                answer_clean = answer.replace(',', '').strip()
                
                # Handle fractions
                if '/' in answer_clean:
                    parts = answer_clean.split('/')
                    if len(parts) == 2:
                        num_val = float(parts[0]) / float(parts[1])
                    else:
                        return False
                else:
                    num_val = float(answer_clean)
            else:
                num_val = float(answer)
            
            # Check for extreme values
            if abs(num_val) > 1_000_000:
                return False
            
            # Check for too many decimal places
            answer_str = str(num_val)
            if '.' in answer_str:
                decimal_places = len(answer_str.split('.')[1])
                if decimal_places > 4:
                    return False
            
            # Geometry-specific: no negative values
            if topic == "geometry" and num_val < 0:
                return False
            
            # Check for NaN or infinity
            if str(num_val).lower() in ['nan', 'inf', '-inf']:
                return False
            
            return True
            
        except (ValueError, TypeError, ZeroDivisionError):
            # If can't convert to number, check if it's a valid non-numeric answer
            answer_str = str(answer).lower()
            # Some questions might have text answers
            if len(answer_str) > 0 and answer_str not in ['error', 'undefined', 'none']:
                return True
            return False
    
    @staticmethod
    def _check_no_math_errors(question: str, answer: Any, topic: str) -> bool:
        """Check for common mathematical errors"""
        
        question_lower = question.lower()
        
        # Check for division by zero
        if '/0' in question or '÷ 0' in question or '÷0' in question:
            return False
        
        # Check for negative measurements in geometry
        if topic == "geometry":
            # Extract numbers from question
            numbers = re.findall(r'-\d+', question)
            if numbers:
                return False  # Negative measurements in geometry
        
        # Check for impossible geometry (e.g., triangle inequality)
        if "triangle" in question_lower:
            # Extract three numbers (potential sides)
            numbers = [float(n) for n in re.findall(r'\d+\.?\d*', question)]
            if len(numbers) >= 3:
                a, b, c = sorted(numbers[:3])
                # Triangle inequality: sum of two smaller sides > largest side
                if a + b <= c:
                    return False
        
        # Check for square root of negative (basic check)
        if 'sqrt' in question_lower or '√' in question:
            # Look for sqrt(-number)
            if re.search(r'sqrt\s*\(\s*-\d+', question_lower) or re.search(r'√\s*-\d+', question):
                return False
        
        return True
    
    @staticmethod
    def _check_clear_wording(question: str) -> bool:
        """Check if question wording is clear and proper"""
        
        # Should end with proper punctuation
        if not question.strip().endswith(('?', '.')):
            return False
        
        # Check for common clarity issues
        unclear_phrases = [
            'etc.', '...', 'something', 'some number', 'somehow'
        ]
        
        question_lower = question.lower()
        if any(phrase in question_lower for phrase in unclear_phrases):
            return False
        
        # Should not have multiple question marks
        if question.count('?') > 1:
            return False
        
        # Should not be too repetitive
        words = question.lower().split()
        if len(words) > 5:
            word_freq = {}
            for word in words:
                if len(word) > 3:  # Only count substantial words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Check if any word appears too many times
            if any(count > 3 for count in word_freq.values()):
                return False
        
        return True
    
    @staticmethod
    def _check_length(question: str, grade: int) -> bool:
        """Check if question length is appropriate for grade level"""
        
        word_count = len(question.split())
        
        # Shorter questions for younger grades
        if grade <= 3:
            return 5 <= word_count <= 30
        elif grade <= 6:
            return 5 <= word_count <= 50
        elif grade <= 9:
            return 5 <= word_count <= 70
        else:
            return 5 <= word_count <= 100
    
    @staticmethod
    def _check_geometry_values(question: str, answer: Any, topic: str) -> bool:
        """Check geometry-specific constraints"""
        
        if topic != "geometry":
            return True  # Not applicable
        
        # Extract all numbers from question
        numbers = [float(n) for n in re.findall(r'\d+\.?\d*', question)]
        
        # No negative values
        if any(n < 0 for n in numbers):
            return False
        
        # Check answer is not negative
        try:
            if isinstance(answer, (int, float)) and answer < 0:
                return False
            elif isinstance(answer, str):
                answer_num = float(answer.replace(',', ''))
                if answer_num < 0:
                    return False
        except:
            pass
        
        return True
    
    @staticmethod
    def _check_grade_appropriate(question: str, grade: int, difficulty: str) -> bool:
        """Check if question complexity matches grade level"""
        
        question_lower = question.lower()
        
        # Check for concepts too advanced for grade
        if grade <= 5:
            # Too advanced for elementary
            advanced_concepts = ['quadratic', 'logarithm', 'exponential', 'derivative', 'integral', 
                                 'trigonometry', 'sine', 'cosine', 'tangent']
            if any(concept in question_lower for concept in advanced_concepts):
                return False
        
        if grade <= 8:
            # Too advanced for middle school
            advanced_concepts = ['calculus', 'derivative', 'integral', 'limit', 'series']
            if any(concept in question_lower for concept in advanced_concepts):
                return False
        
        # Check number size appropriateness
        numbers = [float(n) for n in re.findall(r'\d+\.?\d*', question)]
        if numbers:
            max_num = max(numbers)
            
            if grade <= 3 and max_num > 100:
                return False
            elif grade <= 5 and max_num > 1000:
                return False
            elif grade <= 8 and max_num > 10000:
                return False
        
        return True
    
    @staticmethod
    def _generate_warnings(checks: Dict[str, bool], issues: List[str]) -> List[str]:
        """Generate human-readable warnings for failed checks"""
        
        warnings = []
        
        warning_messages = {
            "has_question": "Question text is missing or too short",
            "has_answer": "Answer is missing or invalid",
            "answer_reasonable": "Answer value is unreasonable (too large, too many decimals, or invalid)",
            "no_math_errors": "Mathematical error detected (division by zero, negative geometry, etc.)",
            "clear_wording": "Question wording is unclear or improperly formatted",
            "appropriate_length": "Question length inappropriate for grade level",
            "no_negatives_in_geometry": "Geometry problem has negative measurements",
            "has_solution_steps": "Solution steps are missing",
            "grade_appropriate": "Question difficulty/concepts inappropriate for grade level"
        }
        
        for issue in issues:
            if issue in warning_messages:
                warnings.append(warning_messages[issue])
        
        return warnings


class QuestionQualityScorer:
    """Scores question quality on multiple dimensions"""
    
    @staticmethod
    def score_question(question: str, answer: Any, topic: str, grade: int) -> Dict[str, float]:
        """
        Score question on multiple quality dimensions
        
        Returns scores (0-1) for:
            - clarity: how clear the question is
            - difficulty_calibration: how well difficulty matches grade
            - educational_value: how good for learning
            - engagement: how interesting/relevant
            - overall: aggregate score
        """
        
        scores = {
            "clarity": QuestionQualityScorer._score_clarity(question),
            "difficulty_calibration": QuestionQualityScorer._score_difficulty(question, grade),
            "educational_value": QuestionQualityScorer._score_educational_value(question, topic),
            "engagement": QuestionQualityScorer._score_engagement(question),
        }
        
        # Calculate overall as weighted average
        weights = {
            "clarity": 0.3,
            "difficulty_calibration": 0.3,
            "educational_value": 0.25,
            "engagement": 0.15
        }
        
        scores["overall"] = sum(scores[k] * weights[k] for k in weights.keys())
        
        return scores
    
    @staticmethod
    def _score_clarity(question: str) -> float:
        """Score question clarity (0-1)"""
        
        score = 1.0
        
        # Proper punctuation
        if not question.strip().endswith(('?', '.')):
            score -= 0.3
        
        # Reasonable length
        word_count = len(question.split())
        if word_count < 5:
            score -= 0.3
        elif word_count > 100:
            score -= 0.2
        
        # No excessive punctuation
        if question.count(',') > 5:
            score -= 0.1
        
        # Has clear instruction verb
        instruction_verbs = ['find', 'calculate', 'solve', 'determine', 'what', 'how']
        if not any(verb in question.lower() for verb in instruction_verbs):
            score -= 0.2
        
        return max(0, score)
    
    @staticmethod
    def _score_difficulty(question: str, grade: int) -> float:
        """Score how well difficulty matches grade level (0-1)"""
        
        # Extract numbers to check complexity
        numbers = [float(n) for n in re.findall(r'\d+\.?\d*', question)]
        
        if not numbers:
            return 0.5  # Neutral if no numbers
        
        max_num = max(numbers)
        avg_num = sum(numbers) / len(numbers)
        
        # Expected number ranges by grade
        expected_ranges = {
            (1, 3): (1, 50),
            (4, 5): (10, 100),
            (6, 8): (10, 500),
            (9, 10): (50, 1000),
            (11, 12): (50, 10000)
        }
        
        # Find appropriate range
        for grade_range, num_range in expected_ranges.items():
            if grade_range[0] <= grade <= grade_range[1]:
                expected_min, expected_max = num_range
                
                # Score based on how well numbers fit expected range
                if expected_min <= avg_num <= expected_max:
                    return 1.0
                elif avg_num < expected_min / 2 or avg_num > expected_max * 2:
                    return 0.3  # Way off
                else:
                    return 0.7  # Somewhat off
        
        return 0.5
    
    @staticmethod
    def _score_educational_value(question: str, topic: str) -> float:
        """Score educational value (0-1)"""
        
        score = 0.6  # Base score
        
        # Real-world context adds value
        real_world_keywords = ['buy', 'cost', 'price', 'distance', 'time', 'speed', 
                               'people', 'students', 'room', 'field', 'garden']
        if any(keyword in question.lower() for keyword in real_world_keywords):
            score += 0.2
        
        # Multi-step problems have higher value
        steps_indicators = ['then', 'after', 'next', 'finally', 'and then']
        if any(indicator in question.lower() for indicator in steps_indicators):
            score += 0.1
        
        # Conceptual understanding questions
        concept_words = ['why', 'explain', 'which', 'compare', 'determine']
        if any(word in question.lower() for word in concept_words):
            score += 0.1
        
        return min(1.0, score)
    
    @staticmethod
    def _score_engagement(question: str) -> float:
        """Score how engaging/interesting the question is (0-1)"""
        
        score = 0.5  # Base score
        
        # Personal context (names, "you") is more engaging
        if any(word in question.lower() for word in ['you', 'your']):
            score += 0.15
        
        # Named characters
        common_names = ['sarah', 'john', 'mary', 'tom', 'jane', 'mike', 'lisa']
        if any(name in question.lower() for name in common_names):
            score += 0.1
        
        # Interesting scenarios
        engaging_contexts = ['game', 'party', 'trip', 'adventure', 'competition', 'prize']
        if any(context in question.lower() for context in engaging_contexts):
            score += 0.15
        
        # Variety in wording (not just "solve for x")
        if not question.lower().startswith(('solve', 'find x', 'calculate')):
            score += 0.1
        
        return min(1.0, score)


if __name__ == "__main__":
    # Test validation
    print("Testing Question Validator\n")
    print("=" * 60)
    
    # Good question
    print("\n1. GOOD QUESTION:")
    result = QuestionValidator.validate(
        question="Sarah has 5 apples. She gets 3 more. How many apples does she have now?",
        answer=8,
        steps=["Add 5 + 3", "5 + 3 = 8"],
        grade=3,
        difficulty="easy",
        topic="arithmetic"
    )
    print(f"Quality: {result['overall_quality']:.2f}")
    print(f"Passed: {result['passed']}")
    print(f"Issues: {result['issues']}")
    
    # Bad question (division by zero)
    print("\n2. BAD QUESTION (division by zero):")
    result = QuestionValidator.validate(
        question="What is 10 ÷ 0?",
        answer="undefined",
        steps=[],
        grade=5,
        difficulty="easy",
        topic="arithmetic"
    )
    print(f"Quality: {result['overall_quality']:.2f}")
    print(f"Passed: {result['passed']}")
    print(f"Issues: {result['issues']}")
    print(f"Warnings: {result['warnings']}")
    
    # Test quality scoring
    print("\n3. QUALITY SCORING:")
    scores = QuestionQualityScorer.score_question(
        question="John buys 3 books at $12 each. How much does he spend?",
        answer=36,
        topic="arithmetic",
        grade=4
    )
    print(f"Scores: {scores}")
    
    print("\n" + "=" * 60)
