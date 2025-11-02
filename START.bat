@echo off
echo ============================================
echo   NRRC Arabic PoV - Backend Server
echo ============================================
echo.

cd /d %~dp0\backend

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

REM Set environment
set PYTHONIOENCODING=utf-8
set TRANSFORMERS_CACHE=%CD%\.cache\transformers

echo Starting backend server...
echo.
echo Server will run on: http://localhost:8000
echo API docs: http://localhost:8000/docs
echo.
echo Press CTRL+C to stop
echo.
echo ============================================
echo.

python run.py

