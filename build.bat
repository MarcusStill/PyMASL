@echo off
REM Переход в папку с bat-файлом
cd /d "%~dp0"

echo ===================================================
echo   Building PyMASL with PyInstaller (.venv)
echo ===================================================

.\.venv\Scripts\python.exe -m PyInstaller ^
  --noconfirm ^
  --onedir ^
  --windowed ^
  --icon "files\logo.ico" ^
  --add-data "modules;modules/" ^
  --add-data "scripts;scripts/" ^
  main.py

echo.
echo ===================================================
echo   Build complete! Output in dist/ directory.
echo ===================================================
pause