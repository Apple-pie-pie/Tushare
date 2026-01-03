@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
cls
echo ========================================
echo    Tushare Data System - Quick Start
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Python not found. Please install Python 3.8+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check .env
if not exist ".env" (
    echo [INFO] First run - creating config file...
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [IMPORTANT] Please edit .env file and add your Tushare token
        echo.
        echo 1. Open .env with Notepad
        echo 2. Change TUSHARE_TOKEN=your_token_here
        echo 3. Save and run this script again
        pause
        exit /b 0
    )
)

REM Update from Git
if exist ".git\" (
    echo [INFO] Checking for updates...
    git fetch origin >nul 2>&1
    
    git rev-parse HEAD >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "delims=" %%i in ('git rev-parse HEAD 2^>nul') do set LOCAL=%%i
        for /f "delims=" %%i in ('git rev-parse @{u} 2^>nul') do set REMOTE=%%i
        
        if not "!LOCAL!"=="!REMOTE!" (
            if not "!REMOTE!"=="" (
                echo [UPDATE] Pulling latest code from GitHub...
                echo [INFO] Local changes will be overwritten
                git reset --hard origin/main >nul 2>&1
                git pull origin main
                if !errorlevel! neq 0 (
                    echo [WARN] Update failed
                ) else (
                    echo [OK] Code updated successfully!
                )
            ) else (
                echo [OK] Already up to date
            )
        ) else (
            echo [OK] Already up to date
        )
    )
    echo.
)

REM Create venv
if not exist "venv\" (
    echo [1/4] Creating virtual environment...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create venv
        pause
        exit /b 1
    )
)

REM Activate venv
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [3/4] Checking dependencies...
python -c "import loguru, duckdb, streamlit, retry" >nul 2>&1
if !errorlevel! neq 0 (
    echo [INFO] Installing dependencies (may take a few minutes)...
    echo.
    python -m pip install --upgrade pip --quiet
    pip install -r requirements.txt --no-cache-dir
    
    if !errorlevel! neq 0 (
        echo.
        echo [ERROR] Installation failed. Please run: install_dependencies.bat
        pause
        exit /b 1
    )
    echo.
    echo [OK] Dependencies installed!
) else (
    echo [OK] Dependencies ready
)

REM Init database
if not exist "data\serve\tushare.duckdb" (
    echo [4/4] Initializing database...
    python scripts\init_db.py
) else (
    echo [4/4] Database exists
)

echo.
echo ========================================
echo    Starting Streamlit...
echo    Browser will open at http://localhost:8501
echo ========================================
echo.
echo Press Ctrl+C to stop
echo.

streamlit run ui\app.py
