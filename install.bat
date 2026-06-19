@echo off
setlocal

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found on PATH.
    echo Install Python 3.11+ from https://www.python.org/downloads/
    echo IMPORTANT: during install, check "Add python.exe to PATH".
    pause
    exit /b 1
)

python -m venv venv

set VENV_PY=venv\Scripts\python.exe
if not exist "%VENV_PY%" (
    echo Something went wrong creating the virtual environment -- %VENV_PY% wasn't created.
    pause
    exit /b 1
)

"%VENV_PY%" -m pip install --upgrade pip
"%VENV_PY%" -m pip install -r requirements.txt

echo.
echo ============================================
echo Setup complete.
echo.
echo Next steps:
echo   1. (Optional) Install Ollama from https://ollama.com for a free local
echo      model, then run: ollama pull dolphin-mistral
echo   2. Edit config.json to pick a backend and/or add API keys.
echo   3. Run run.bat to test it, or build_exe.bat to build Clippy.exe.
echo ============================================
pause
