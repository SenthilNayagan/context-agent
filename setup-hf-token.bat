@echo off
echo Hugging Face token setup (optional)
echo.
echo This enables faster model downloads.
echo Your documents NEVER leave your machine.
echo.

set /p HF_TOKEN="Enter your Hugging Face token (leave empty to skip): "

if "%HF_TOKEN%"=="" (
    echo Skipping HF token setup.
    goto :eof
)

setx HF_TOKEN "%HF_TOKEN%"
echo HF_TOKEN set successfully.
echo Restart your terminal for changes to take effect.
