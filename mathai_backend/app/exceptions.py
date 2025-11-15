"""Custom exception classes for structured error handling."""
from fastapi import HTTPException, status


class MathAIException(Exception):
    """Base exception for MathAI application."""
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class QuestionGenerationError(MathAIException):
    """Raised when question generation fails."""
    def __init__(self, message: str = "Failed to generate question"):
        super().__init__(message, "QUESTION_GENERATION_FAILED")


class QuestionNotFoundError(MathAIException):
    """Raised when a question is not found."""
    def __init__(self, question_id: str):
        super().__init__(f"Question not found: {question_id}", "QUESTION_NOT_FOUND")


class ValidationError(MathAIException):
    """Raised when validation fails."""
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class DatabaseError(MathAIException):
    """Raised when database operations fail."""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, "DATABASE_ERROR")


class AuthenticationError(MathAIException):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_FAILED")


class OllamaTimeoutError(MathAIException):
    """Raised when Ollama service times out."""
    def __init__(self, message: str = "AI service timeout"):
        super().__init__(message, "OLLAMA_TIMEOUT")


# HTTP Exception factories
def http_exception_from_mathai_error(error: MathAIException) -> HTTPException:
    """Convert MathAI exception to HTTP exception."""
    status_map = {
        "QUESTION_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "VALIDATION_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "DATABASE_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "AUTHENTICATION_FAILED": status.HTTP_401_UNAUTHORIZED,
        "OLLAMA_TIMEOUT": status.HTTP_504_GATEWAY_TIMEOUT,
        "QUESTION_GENERATION_FAILED": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    
    status_code = status_map.get(error.code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return HTTPException(
        status_code=status_code,
        detail={
            "error": error.message,
            "code": error.code
        }
    )
