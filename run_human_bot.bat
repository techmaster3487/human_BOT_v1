@echo off
REM Human B.O.T MVP - Demo Runner Script
REM Usage: run.bat

echo.
echo ========================================
echo   Human B.O.T MVP - Demo Runner
echo ========================================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [*] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [!] Virtual environment not found. Using system Python...
    echo [!] Consider creating a virtual environment: python -m venv venv
)

REM Check if demo.py exists
if not exist "demo\demo.py" (
    echo [ERROR] demo.py not found!
    echo Please make sure you're running this from the project root directory.
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.11 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Run the demo
echo.
echo [*] Starting demo with 10 sessions and 5 workers...
echo [*] Press Ctrl+C to stop
echo.

python ./demo/demo.py --session 10 --workers 5

if errorlevel 1 (
    echo.
    echo [ERROR] Demo script failed!
    pause
    exit /b 1
)

pause
