@echo off
REM AI Governance Register — One-command launcher (Windows)
REM Usage: start.bat

cd /d "%~dp0"

echo === AI Governance Register ===
echo.

REM Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.11+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Create virtual environment if needed
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate venv
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q fastapi uvicorn[standard] sqlalchemy pydantic python-dotenv anthropic reportlab python-docx requests streamlit plotly 2>nul

REM Create data directory
if not exist "data" mkdir data

REM Start API in background
echo Starting API on port 8000...
start /b "API" uvicorn api.main:app --host 0.0.0.0 --port 8000

REM Wait for API
timeout /t 3 /nobreak >nul

REM Start Streamlit
echo Starting frontend on port 8501...
start /b "Frontend" streamlit run agr_frontend/app.py --server.port 8501 --server.headless true

REM Wait and open browser
timeout /t 3 /nobreak >nul
echo.
echo Ready!
echo   Frontend: http://localhost:8501
echo   API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop.

start http://localhost:8501

REM Keep window open
pause
