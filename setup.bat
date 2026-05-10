@echo off
setlocal

echo =============================================
echo Python Project Setup (Windows)
echo =============================================

REM Always run from the directory where this script is located
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not found in PATH.
    echo Please install Python 3 and ensure it is added to PATH.
    exit /b 1
)

REM Step 1: Create virtual environment if not exists
if not exist "venv\" (
    echo [INFO] Virtual environment not found.
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        exit /b 1
    )
) else (
    echo [INFO] Virtual environment already exists.
)

REM Step 2: Activate virtual environment (Windows)
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    exit /b 1
)

REM Step 3: Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERROR] Pip upgrade failed.
    exit /b 1
)

REM Step 4: Install dependencies
if exist "requirements.txt" (
    echo [INFO] Installing dependencies from requirements.txt...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        exit /b 1
    )
) else (
    echo [WARN] requirements.txt not found. Skipping dependency install.
)

REM Step 5: Install project in editable mode
echo [INFO] Installing project in editable mode (-e .)...
python -m pip install -e .
if errorlevel 1 (
    echo [ERROR] Editable install failed.
    exit /b 1
)

echo =============================================
echo Setup completed successfully!
echo =============================================
echo Virtual environment: venv
echo To activate later, run:
echo     venv\Scripts\activate.bat
echo =============================================

REM pause to allow user to read the output before closing the terminal
pause
endlocal