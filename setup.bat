@echo off
REM Quick setup script for Olist E-Commerce database

echo ============================================================
echo   Olist E-Commerce Database - Quick Setup
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/6] Checking Python installation...
python --version
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [2/6] Creating virtual environment...
    python -m venv venv
    echo.
) else (
    echo [2/6] Virtual environment already exists
    echo.
)

REM Activate virtual environment
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo [4/6] Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt --quiet
echo Dependencies installed!
echo.

REM Check if .env exists
if not exist ".env" (
    echo [5/6] Setting up environment variables...
    copy .env.example .env >nul
    echo.
    echo Please edit .env file with your credentials:
    echo   - PostgreSQL password
    echo   - Kaggle API credentials
    echo   - OpenAI API key (for agents)
    echo.
    notepad .env
) else (
    echo [5/6] Environment file already exists
    echo.
)

REM Test database connection
echo [6/6] Testing database connection...
python scripts\test_connection.py
echo.

echo ============================================================
echo   Setup Complete!
echo ============================================================
echo.
echo Next steps:
echo   1. If database is not ready, run these commands:
echo      python scripts\download_dataset.py
echo      python scripts\setup_database.py
echo      python scripts\load_data.py
echo.
echo   2. Explore the data:
echo      python scripts\explore_data.py
echo.
echo   3. See docs\SETUP_GUIDE.md for detailed instructions
echo.
pause
