from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class QuestionRequest(BaseModel):
    grade: int = Field(..., ge=1, le=12)
    difficulty: str = Field(..., pattern="^(easy|medium|hard)$")
    topic: str
    question_type: str = Field(default="open", pattern="^(open|mcq)$")  # "open" or "mcq"
    
class QuestionResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    grade: int
    difficulty: str
    topic: str
    correct_answer: str
    normalized_answers: Optional[List[str]] = None
    choices: Optional[List[str]] = None  # Multiple-choice options (correct one included)
    hints: List[str]
    solution_steps: List[str]
    created_at: datetime = Field(default_factory=datetime.now)

class AnswerSubmission(BaseModel):
    question_id: str
    student_answer: str
    attempt_number: int = Field(default=1)
    student_id: str | None = None
    
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