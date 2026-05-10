@echo off
setlocal ENABLEDELAYEDEXPANSION

REM =====================================================
REM ContextAgent - Build and Publish Vector Index
REM (OneDrive / SharePoint safe)
REM =====================================================

REM Always run from project root
cd /d "%~dp0"

echo =====================================================
echo Build and Publish Vector Index
echo =====================================================

REM -----------------------------------------------------
REM Step 1: Enforce EXTERNAL storage mode
REM -----------------------------------------------------
echo.
echo [STEP 1] Enforcing external storage mode...
set CONTEXTAGENT_STORAGE_MODE=external
echo CONTEXTAGENT_STORAGE_MODE=%CONTEXTAGENT_STORAGE_MODE%

REM -----------------------------------------------------
REM Step 2: Remove LOCAL build artifacts (safe & required)
REM -----------------------------------------------------
echo.
echo [STEP 2] Removing local vector build artifacts...

if exist ".vector_build\vector_index" (
    rmdir /s /q ".vector_build\vector_index"
    echo [OK] Local build directory deleted.
) else (
    echo [INFO] Local build directory not present.
)

REM -----------------------------------------------------
REM Step 3: Ensure SharePoint vector_index directory exists
REM (DO NOT DELETE - OneDrive-safe contract)
REM -----------------------------------------------------
echo.
echo [STEP 3] Ensuring SharePoint vector_index directory exists...

set SP_INDEX_DIR=%OneDrive%\AI_Knowledge_Index\vector_index

if "%OneDrive%"=="" (
    echo [ERROR] OneDrive environment variable is not set.
    echo Please ensure OneDrive is installed and synced.
    exit /b 1
)

if not exist "%SP_INDEX_DIR%" (
    echo [INFO] vector_index folder not found. Creating it...
    mkdir "%SP_INDEX_DIR%"
) else (
    echo [INFO] vector_index folder already exists.
)

echo [OK] SharePoint vector_index directory ready:
echo      %SP_INDEX_DIR%

REM -----------------------------------------------------
REM Step 4: Run embeddings build + publish
REM -----------------------------------------------------
echo.
echo [STEP 4] Running embeddings build and publish...
echo.

cd src\context_agent\rag

python embeddings.py --publish
if errorlevel 1 (
    echo.
    echo [ERROR] Embeddings publish failed.
    echo Ensure FastAPI is stopped and OneDrive is idle.
    exit /b 1
)

echo.
echo =====================================================
echo SUCCESS: Vector index built and published successfully
echo =====================================================

pause
endlocal