@echo off
REM Human B.O.T Dashboard - Node.js API Backend Startup Script

echo.
echo ========================================
echo   Human B.O.T Dashboard - Node.js Backend
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

REM Change to API directory and run
cd api_node_version
npm start

cd ..
pause
