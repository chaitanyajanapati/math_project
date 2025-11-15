"""Database models for SQLAlchemy."""
from sqlalchemy import Column, String, Integer, Boolean, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


def generate_uuid():
    """Generate a UUID string."""
    return str(uuid.uuid4())


class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    grade = Column(Integer, default=8)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    progress = relationship("Progress", back_populates="user", cascade="all, delete-orphan")


class Question(Base):
    """Question model."""
    __tablename__ = "questions"

    id = Column(String, primary_key=True, default=generate_uuid)
    question = Column(Text, nullable=False)
    grade = Column(Integer, nullable=False)
    difficulty = Column(String, nullable=False)
    topic = Column(String, nullable=False, index=True)
    correct_answer = Column(String, nullable=False)
    normalized_answers = Column(JSON, default=list)  # Store as JSON array
    choices = Column(JSON, nullable=True)  # MCQ choices
    hints = Column(JSON, default=list)  # Store hints as JSON array
    solution_steps = Column(JSON, default=list)  # Store steps as JSON array
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    attempts = relationship("Progress", back_populates="question", cascade="all, delete-orphan")


class Progress(Base):
    """Student progress model."""
    __tablename__ = "progress"

    id = Column(String, primary_key=True, default=generate_uuid)
    student_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(String, ForeignKey("questions.id"), nullable=False, index=True)
    attempts = Column(Integer, default=1)
    solved = Column(Boolean, default=False)
    last_attempt_at = Column(DateTime, default=datetime.utcnow)
    time_spent = Column(Float, default=0.0)
    points_earned = Column(Float, default=0.0)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    question = relationship("Question", back_populates="attempts")
