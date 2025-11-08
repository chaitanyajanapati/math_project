#!/bin/bash
# Math AI Question Generator - Linux/Mac Quick Start
# This script starts both backend and frontend servers

echo "========================================"
echo "  Math AI Question Generator"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed!"
    echo "Please install Python 3.9+ from https://www.python.org/"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed!"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "WARNING: Ollama is not installed!"
    echo "Some AI features may not work."
    echo "Download from https://ollama.ai/"
    echo ""
fi

echo "[1/4] Checking dependencies..."

# Install backend dependencies if needed
if [ ! -d "mathai_backend/venv" ]; then
    echo "[2/4] Setting up backend virtual environment..."
    cd mathai_backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
else
    echo "[2/4] Backend dependencies already installed"
fi

# Install frontend dependencies if needed
if [ ! -d "mathai_frontend/node_modules" ]; then
    echo "[3/4] Installing frontend dependencies..."
    cd mathai_frontend
    npm install
    cd ..
else
    echo "[3/4] Frontend dependencies already installed"
fi

echo "[4/4] Starting servers..."
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

# Trap CTRL+C and cleanup
trap cleanup INT TERM

# Start backend server
echo "Starting backend on http://localhost:8000..."
cd mathai_backend
if [ -d "venv" ]; then
    source venv/bin/activate
fi
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "Waiting for backend to initialize..."
sleep 5

# Start frontend server
echo "Starting frontend on http://localhost:5173..."
cd mathai_frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 5

echo ""
echo "========================================"
echo "  Application Started Successfully!"
echo "========================================"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Opening browser..."
sleep 2

# Open browser based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:5173
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open http://localhost:5173 2>/dev/null || echo "Please open http://localhost:5173 in your browser"
fi

echo ""
echo "Press Ctrl+C to stop the servers"
echo "Logs: backend.log and frontend.log"
echo ""

# Keep script running
wait
