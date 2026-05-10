@echo off

REM Activate the Python virtual environment located at %CD%\venv
REM This script must be run from the project root

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found at:
    echo         %CD%\venv
    echo.
    echo Please create it first:
    echo     python -m venv venv
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Optional: show confirmation
echo Virtual environment activated.
echo Python:
python --version