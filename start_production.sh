#!/bin/bash
# Production startup script with performance optimizations

echo "Starting MathAI Backend in Production Mode..."
echo "==========================================="
echo ""

# Set production environment
export PYTHONOPTIMIZE=2  # Enable Python optimizations
export PYTHONDONTWRITEBYTECODE=1  # Don't write .pyc files

# Start with multiple workers for better concurrency
# Workers = (2 x CPU cores) + 1
WORKERS=4

echo "Configuration:"
echo "- Workers: $WORKERS"
echo "- Host: 0.0.0.0"
echo "- Port: 8000"
echo "- Optimizations: Enabled"
echo ""

cd mathai_backend

# Start Uvicorn with production settings
uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers $WORKERS \
    --no-access-log \
    --log-level warning

echo ""
echo "Server stopped."
