from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum
import uuid


class DifficultyLevel(str, Enum):
    """Difficulty levels for questions."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class MathTopic(str, Enum):
    """Supported math topics."""
    ALGEBRA = "algebra"
    GEOMETRY = "geometry"
    ARITHMETIC = "arithmetic"
    STATISTICS = "statistics"
    PROBABILITY = "probability"
    TRIGONOMETRY = "trigonometry"
    NUMBER_THEORY = "number_theory"
    CALCULUS = "calculus"


class QuestionType(str, Enum):
    """Question format types."""
    OPEN = "open"
    MCQ = "mcq"


class QuestionRequest(BaseModel):
    grade: int = Field(..., ge=1, le=12)
    difficulty: DifficultyLevel
    topic: MathTopic
    question_type: QuestionType = QuestionType.OPEN
    
    @field_validator('grade')
    @classmethod
    def validate_grade_range(cls, v: int) -> int:
        """Additional validation for grade."""
        if not 1 <= v <= 12:
            raise ValueError('Grade must be between 1 and 12')
        return v
    
class QuestionResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    grade: int
    difficulty: str  # Keep as string for backwards compatibility with stored data
    topic: str  # Keep as string for backwards compatibility
    correct_answer: str
    normalized_answers: Optional[List[str]] = None
    choices: Optional[List[str]] = None  # Multiple-choice options (correct one included)
    hints: List[str]
    solution_steps: List[str]
    created_at: datetime = Field(default_factory=datetime.now)

class AnswerSubmission(BaseModel):
    question_id: str = Field(..., min_length=1, description="Question UUID")
    student_answer: str = Field(..., min_length=1, max_length=1000, description="Student's answer")
    attempt_number: int = Field(default=1, ge=1, le=10, description="Attempt number (1-10)")
    student_id: str | None = Field(default=None, description="Student ID (optional)")
    
    @field_validator('question_id')
    @classmethod
    def validate_question_id(cls, v: str) -> str:
        """Validate question_id format."""
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError('Invalid question_id format')
        return v
    
    @field_validator('student_answer')
    @classmethod
    def validate_student_answer(cls, v: str) -> str:
        """Sanitize student answer."""
        return v.strip()
    
class AnswerResponse(BaseModel):
    is_correct: bool
    confidence: float = Field(..., ge=0, le=1)
    feedback: str
    hint: Optional[str]
    next_step: Optional[str]
    points_earned: int
    time_taken: Optional[float]
    # Optional: include solution steps and correct answer when appropriate
    solution_steps: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    
class StudentProgress(BaseModel):
    student_id: str
    question_id: str
    attempts: int
    solved: bool
    last_attempt_at: datetime
    time_spent: float
    points_earned: int