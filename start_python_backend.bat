@echo off
REM Human B.O.T Dashboard - FastAPI Backend Startup Script
REM This script starts the FastAPI backend server

echo.
echo ========================================
echo   Human B.O.T Dashboard - FastAPI Backend
echo ========================================
echo.

REM Check if backend directory exists
if not exist "api_python_version" (
    echo [ERROR] api directory not found!
    echo Please run this script from the project root directory.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [*] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [!] Virtual environment not found. Using system Python...
    echo [!] Consider creating a virtual environment: python -m venv venv
)

REM Change to backend directory
cd api_python_version

REM Check if requirements are installed
echo [*] Checking dependencies...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo [!] FastAPI not found. Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies!
        cd ..
        pause
        exit /b 1
    )
)

REM Check if websockets is installed (required for WebSocket support)
python -c "import websockets" 2>nul
if errorlevel 1 (
    echo [!] WebSocket library not found. Installing websockets...
    pip install websockets
    if errorlevel 1 (
        echo [WARNING] Failed to install websockets. WebSocket support may not work.
    )
)

REM Start the FastAPI server
echo.
echo [*] Starting FastAPI backend server...
echo [*] Server will be available at: http://localhost:3000
echo [*] API Documentation: http://localhost:3000/docs
echo [*] WebSocket: ws://localhost:3000/
echo [*] Press Ctrl+C to stop the server
echo.

uvicorn main:app --host 0.0.0.0 --port 3000 --reload

REM If uvicorn command fails, try alternative
if errorlevel 1 (
    echo.
    echo [!] uvicorn command failed. Trying alternative method...
    python -m uvicorn main:app --host 0.0.0.0 --port 3000 --reload
)

cd ..
pause
