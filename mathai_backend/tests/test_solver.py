"""
Test suite for the symbolic solver module.
"""
import pytest
from app.utils.solver import (
    solve_question,
    solve_linear_equation,
    solve_quadratic_equation,
    solve_geometry_area,
    solve_percentage,
    solve_arithmetic
)


class TestLinearEquations:
    def test_simple_linear(self):
        result = solve_linear_equation("Solve for x: 2x + 3 = 11")
        assert result is not None
        answer, steps = result
        assert answer == "4"
        assert len(steps) > 0
    
    def test_negative_solution(self):
        result = solve_linear_equation("Solve for y: 3y - 5 = -14")
        assert result is not None
        answer, steps = result
        assert answer == "-3"
    
    def test_fractional_solution(self):
        result = solve_linear_equation("Solve for x: 5x + 2 = 12")
        assert result is not None
        answer, steps = result
        # Answer should be 2
        assert float(answer) == 2.0


class TestQuadraticEquations:
    def test_simple_quadratic(self):
        result = solve_quadratic_equation("Solve: x² - 5x + 6 = 0")
        assert result is not None
        answer, steps = result
        # Solutions are 2 and 3
        assert "2" in answer and "3" in answer
    
    def test_quadratic_alt_notation(self):
        result = solve_quadratic_equation("Solve: x^2 - 4 = 0")
        assert result is not None
        answer, steps = result
        assert "-2" in answer and "2" in answer


class TestGeometry:
    def test_rectangle_area(self):
        result = solve_geometry_area("Find the area of a rectangle with length 6 cm and width 4 cm")
        assert result is not None
        answer, steps = result
        assert answer == "24" or answer == "24.0"
        assert "6" in steps[1] and "4" in steps[1]
    
    def test_square_area(self):
        result = solve_geometry_area("Calculate the area of a square with side 5 meters")
        assert result is not None
        answer, steps = result
        assert answer == "25" or answer == "25.0"
    
    def test_triangle_area(self):
        result = solve_geometry_area("Find the area of a triangle with base 8 cm and height 5 cm")
        assert result is not None
        answer, steps = result
        assert float(answer) == 20.0


class TestPercentages:
    def test_percentage_of(self):
        result = solve_percentage("What is 25% of 80?")
        assert result is not None
        answer, steps = result
        assert float(answer) == 20.0
    
    def test_what_percent(self):
        result = solve_percentage("30 is what percent of 150?")
        assert result is not None
        answer, steps = result
        assert float(answer) == 20.0


class TestArithmetic:
    def test_simple_addition(self):
        result = solve_arithmetic("What is 15 + 27?")
        assert result is not None
        answer, steps = result
        assert float(answer) == 42.0
    
    def test_multiplication(self):
        result = solve_arithmetic("Calculate 6 * 7")
        assert result is not None
        answer, steps = result
        assert float(answer) == 42.0


class TestMainSolver:
    def test_solve_question_router(self):
        # Test that solve_question routes to the correct solver
        test_cases = [
            ("Solve for x: 3x = 15", "algebra", "5"),
            ("Find the area of a rectangle with length 10 and width 5", "geometry", "50"),
            ("What is 50% of 100?", "percentages", "50"),
        ]
        
        for question, topic, expected in test_cases:
            result = solve_question(question, topic)
            assert result is not None, f"Failed to solve: {question}"
            answer, steps = result
            assert float(answer) == float(expected), f"Expected {expected}, got {answer}"
    
    def test_fallback_to_any_solver(self):
        # Even if topic is wrong, solver should try all patterns
        result = solve_question("Solve for x: x + 5 = 10", "wrong_topic")
        assert result is not None
        answer, steps = result
        assert answer == "5"
