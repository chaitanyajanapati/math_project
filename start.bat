@echo off
REM Math AI Question Generator - Windows Quick Start
REM This script starts both backend and frontend servers

echo ========================================
echo   Math AI Question Generator
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Ollama is installed
where ollama >nul 2>&1
if errorlevel 1 (
    echo WARNING: Ollama is not installed!
    echo Some AI features may not work.
    echo Download from https://ollama.ai/
    echo.
)

echo [1/4] Checking dependencies...

REM Install backend dependencies if needed
if not exist "mathai_backend\venv\" (
    echo [2/4] Setting up backend virtual environment...
    cd mathai_backend
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
    cd ..
) else (
    echo [2/4] Backend dependencies already installed
)

REM Install frontend dependencies if needed
if not exist "mathai_frontend\node_modules\" (
    echo [3/4] Installing frontend dependencies...
    cd mathai_frontend
    call npm install
    cd ..
) else (
    echo [3/4] Frontend dependencies already installed
)

echo [4/4] Starting servers...
echo.

REM Start backend server
echo Starting backend on http://localhost:8000...
cd mathai_backend
if exist "venv\Scripts\activate" (
    call venv\Scripts\activate
)
start /B cmd /c "python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ..\backend.log 2>&1"
cd ..

REM Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Start frontend server
echo Starting frontend on http://localhost:5173...
cd mathai_frontend
start /B cmd /c "npm run dev > ..\frontend.log 2>&1"
cd ..

REM Wait for frontend to start
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo   Application Started Successfully!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Opening browser...
timeout /t 2 /nobreak >nul
start http://localhost:5173

echo.
echo Press Ctrl+C to stop the servers
echo Logs: backend.log and frontend.log
echo.
pause
