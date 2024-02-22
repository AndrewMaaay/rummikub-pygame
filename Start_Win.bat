@echo off
@echo off
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo This Rummikub requires a Python environment.
    echo Please visit https://www.python.org/downloads/ to download and install Python.
) else (
    echo Python is fine
    python main.py
)

pause


