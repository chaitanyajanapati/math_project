"""
Logging middleware for request/response tracking and performance monitoring.
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.logging_config import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all HTTP requests and responses.
    
    Features:
    - Assigns unique request ID to each request
    - Logs request details (method, path, client)
    - Logs response details (status, duration)
    - Tracks performance metrics
    - Provides hooks for error tracking integration
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]
        
        # Store request ID in request state for use in handlers
        request.state.request_id = request_id
        
        # Start timer
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            "Incoming request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent", "unknown"),
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                }
            )
            
            # Add request ID to response headers for tracing
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as exc:
            # Calculate duration even on error
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration_ms, 2),
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                },
                exc_info=True
            )
            
            # Re-raise to let FastAPI handle it
            raise


class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for tracking slow requests and performance metrics.
    
    Logs warnings for requests that exceed threshold duration.
    """
    
    def __init__(self, app: ASGIApp, slow_request_threshold_ms: float = 1000.0):
        super().__init__(app)
        self.slow_request_threshold_ms = slow_request_threshold_ms
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Track request performance."""
        start_time = time.time()
        
        response = await call_next(request)
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Log slow requests
        if duration_ms > self.slow_request_threshold_ms:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.warning(
                "Slow request detected",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration_ms, 2),
                    "threshold_ms": self.slow_request_threshold_ms,
                }
            )
        
        return response


def add_request_id_to_logs(request: Request) -> dict:
    """
    Helper function to extract request ID from request state.
    Use in route handlers to include request ID in logs.
    
    Example:
        logger.info("Processing data", extra=add_request_id_to_logs(request))
    """
    request_id = getattr(request.state, "request_id", "no-request")
    return {"request_id": request_id}
