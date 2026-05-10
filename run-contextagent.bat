@echo off
setlocal ENABLEDELAYEDEXPANSION

REM =====================================================
REM ContextAgent - One Runner Script (Windows / cmd.exe)
REM =====================================================

REM Always run from project root
cd /d "%~dp0"

echo =====================================================
echo ContextAgent - Unified Startup
echo =====================================================

REM -----------------------------------------------------
REM Step 1: Ollama prerequisites
REM -----------------------------------------------------
echo.
echo [STEP 1] Checking Ollama prerequisites...
call ollama-setup.bat
if errorlevel 1 (
    echo [ERROR] Ollama setup failed.
    exit /b 1
)

REM -----------------------------------------------------
REM Step 2: Python environment setup
REM -----------------------------------------------------
echo.
echo [STEP 2] Ensuring Python virtual environment...
call setup.bat
if errorlevel 1 (
    echo [ERROR] Python setup failed.
    exit /b 1
)

REM -----------------------------------------------------
REM Step 3: Activate virtual environment
REM -----------------------------------------------------
echo.
echo [STEP 3] Activating virtual environment...
call activate-venv.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    exit /b 1
)

REM -----------------------------------------------------
REM Step 4: Enforce external (remote) storage mode
REM -----------------------------------------------------
echo.
echo [STEP 4] Enforcing storage mode: EXTERNAL (SharePoint / OneDrive)

set CONTEXTAGENT_STORAGE_MODE=external

echo CONTEXTAGENT_STORAGE_MODE=%CONTEXTAGENT_STORAGE_MODE%

REM -----------------------------------------------------
REM Step 5: Start FastAPI server
REM -----------------------------------------------------
echo.
echo [STEP 5] Starting ContextAgent FastAPI server...
echo.
echo   -> API: http://127.0.0.1:8000
echo   -> Docs: http://127.0.0.1:8000/docs
echo.

start "ContextAgent API" cmd /k ^
    python -m context_agent.api.server

REM -----------------------------------------------------
REM Step 6: Open UI in browser
REM -----------------------------------------------------
echo.
echo [STEP 6] Launching UI...

set UI_PATH=%CD%\src\context_agent\ui\static\index.html

if exist "%UI_PATH%" (
    start "" "%UI_PATH%"
) else (
    echo [WARN] UI file not found at:
    echo        %UI_PATH%
    echo [INFO] API is still running.
)

echo.
echo =====================================================
echo ContextAgent is running
echo =====================================================
echo.
echo Press Ctrl+C in the API window to stop the server.
echo.

endlocal