@echo off
call venv\Scripts\activate.bat

pip show pyinstaller >nul 2>nul
if errorlevel 1 (
    pip install pyinstaller
)

pyinstaller --onefile --windowed ^
    --icon=assets\icon.ico ^
    --add-data "assets;assets" ^
    --paths src ^
    --name Clippy ^
    src\main.py

echo.
echo ============================================
echo Build complete: dist\Clippy.exe
echo.
echo A config.json and clippy.log will be created next to Clippy.exe the
echo first time you run it. Move Clippy.exe (it can live on its own --
echo config.json travels with it) wherever you want, then:
echo.
echo   To launch at login: Win+R, type shell:startup, Enter, then drop a
echo   shortcut to Clippy.exe into that folder.
echo ============================================
pause
