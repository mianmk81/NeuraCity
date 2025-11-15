@echo off
REM NeuraCity Backend Startup Script (Windows)

echo =====================================
echo    NeuraCity Backend Startup
echo =====================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and configure your API keys.
    echo.
    echo Run: copy .env.example .env
    pause
    exit /b 1
)

REM Create uploads directory
echo Creating uploads directory...
if not exist "uploads" mkdir uploads

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    echo Dependencies already installed.
)

echo.
echo Starting NeuraCity API server...
echo API will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python run.py
