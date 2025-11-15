"""Logging configuration with structured JSON output and request tracking."""
import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Optional
from pythonjsonlogger.json import JsonFormatter
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Context variable to store request ID across async boundaries
request_id_context: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class RequestIDFilter(logging.Filter):
    """Add request_id to log records from context."""
    
    def filter(self, record):
        record.request_id = request_id_context.get() or "no-request"
        return True


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to generate and store request ID for each request."""
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        req_id = str(uuid.uuid4())[:8]
        
        # Store in context for logging
        request_id_context.set(req_id)
        
        # Add to request state for access in endpoints
        request.state.request_id = req_id
        
        # Add to response headers for client-side tracking
        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        
        return response


def setup_logging(log_level: str = "INFO", log_format: str = "json"):
    """Configure application logging with structured output.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format type - 'json' for structured JSON or 'text' for human-readable
    """
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    if log_format == "json":
        # JSON formatter for structured logging
        formatter = JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(request_id)s %(message)s',
            timestamp=True
        )
    else:
        # Text formatter for development
        formatter = logging.Formatter(
            '%(asctime)s - %(request_id)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    handler.setFormatter(formatter)
    handler.addFilter(RequestIDFilter())
    
    logger.addHandler(handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return logger


# Get application logger
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given module name."""
    return logging.getLogger(name)
