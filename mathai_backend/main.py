from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator
from contextlib import asynccontextmanager
import time

from app.routers import ai_router
from app.config import settings
from app.logging_config import setup_logging, RequestIDMiddleware, get_logger

# Setup logging
setup_logging(log_level=settings.log_level, log_format=settings.log_format)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info(
        "Application startup",
        extra={
            "version": settings.api_version,
            "cors_origins": settings.cors_origins,
            "rate_limiting": settings.enable_rate_limiting,
            "metrics": settings.enable_metrics,
        }
    )
    yield
    # Shutdown
    logger.info("Application shutdown")


# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"]
)

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url=None,  # Disable ReDoc to reduce overhead
    lifespan=lifespan
)

# Add rate limiter state to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Request ID Middleware (first for logging) ---
app.add_middleware(RequestIDMiddleware)

# --- Performance: Enable Gzip compression ---
app.add_middleware(GZipMiddleware, minimum_size=1000)

# --- Enable CORS with restricted origins ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Prometheus Metrics ---
if settings.enable_metrics:
    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )
    instrumentator.instrument(app).expose(app, endpoint="/metrics")
    logger.info("Prometheus metrics enabled at /metrics")

# Include the AI router
app.include_router(ai_router.router, prefix="/api")

# --- Root test endpoint ---
@app.get("/")
def root():
    return {"message": "MathAI backend is running!", "version": settings.api_version}

# --- Health check endpoint ---
@app.get("/health")
def health_check():
    return {"status": "healthy", "version": settings.api_version}
