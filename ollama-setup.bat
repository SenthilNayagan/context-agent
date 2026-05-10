@echo off
setlocal

echo =============================================
echo M1 OpsAgent - Ollama Prerequisites Check
echo =============================================

REM Step 1: Check if Ollama is installed
where ollama >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Ollama is not installed or not in PATH.
    echo Please install Ollama from:
    echo     https://ollama.com/download
    exit /b 1
)

echo [INFO] Ollama is installed.

REM Step 2: Check if Ollama service is running
ollama list >nul 2>&1
if errorlevel 1 (
    echo [INFO] Ollama is not running. Starting Ollama...
    start "" ollama serve
    timeout /t 5 >nul
) else (
    echo [INFO] Ollama is already running.
)

REM Step 3: Check if required model exists
set MODEL=llama3.2:1b
ollama list | findstr /i "%MODEL%" >nul
if errorlevel 1 (
    echo [INFO] Model %MODEL% not found. Pulling...
    ollama pull %MODEL%
    if errorlevel 1 (
        echo [ERROR] Failed to pull model %MODEL%.
        exit /b 1
    )
) else (
    echo [INFO] Model %MODEL% already available.
)

echo =============================================
echo Ollama prerequisites satisfied
echo =============================================

pause
endlocal