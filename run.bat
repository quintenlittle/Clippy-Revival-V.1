@echo off
set VENV_PY=venv\Scripts\python.exe

if not exist "%VENV_PY%" (
    echo %VENV_PY% not found -- run install.bat first.
    pause
    exit /b 1
)

"%VENV_PY%" src\main.py
pause
