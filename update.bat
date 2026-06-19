@echo off
setlocal

if "%~1"=="" (
    echo Usage: update.bat "your commit message here"
    pause
    exit /b 1
)

git add -A
git commit -m "%~1"
git push

echo.
echo ============================================
echo Done -- check above for any errors.
echo ============================================
pause
