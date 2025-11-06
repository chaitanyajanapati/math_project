import pytest
from app.utils.math_service import MathAIService

math = MathAIService()


def test_normalize_fraction():
    vals = math.normalize_answer("3/8")
    # Expect both fraction and decimal forms present
    assert "3/8" in vals
    assert any(v.startswith("0.3") or v == "0.375" for v in vals)


def test_validate_fraction_decimal_equivalence():
    # correct answer generated as fraction
    correct = "3/8"
    student_decimal = "0.375"
    is_correct, confidence, feedback, hint = math.validate_answer(correct, student_decimal, attempt_number=1)
    assert is_correct is True
    assert confidence >= 0.9


def test_validate_using_persisted_normalized():
    # Simulate a case where correct_answer string might be empty but normalized forms are stored
    correct = ""
    # persisted normalized forms (fraction + decimal)
    normalized = ["3/8", "0.375"]
    student = "3/8"
    is_correct, confidence, feedback, hint = math.validate_answer(correct, student, attempt_number=1, correct_normalized=normalized)
    assert is_correct is True


if __name__ == "__main__":
    pytest.main([__file__])
