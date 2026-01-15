@echo off
REM Human B.O.T Dashboard - React Frontend Startup Script

echo.
echo ========================================
echo   Human B.O.T Dashboard - React Frontend
echo ========================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo Please install Node.js from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo [*] Node.js version:
node --version
echo.

REM Change to dashboard directory and run
cd dashboard
npm start

cd ..
pause
