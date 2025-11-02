@echo off
echo Starting NRRC Arabic PoV Backend...
echo.

cd /d %~dp0

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist .venv (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Install dependencies if needed
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Set environment variables
set PYTHONIOENCODING=utf-8
set TRANSFORMERS_CACHE=%CD%\.cache\transformers

REM Start the server
echo.
echo Starting server on http://localhost:8000
echo Press CTRL+C to stop
echo.
python run.py

pause

