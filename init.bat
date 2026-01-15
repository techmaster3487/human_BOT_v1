@echo off
REM Human B.O.T MVP Initialization Script (Windows)
REM Usage: init.bat

echo.
echo 🤖 Human B.O.T MVP - Initialization Script
echo ==========================================
echo.

REM Check Python installation
echo 🔍 Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH.
    echo Please install Python 3.11 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo ✅ Python is installed
python --version
echo.

REM Create directory structure
echo 📁 Creating directory structure...
if not exist "config" mkdir config
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "tests" mkdir tests
if not exist "demo" mkdir demo
if not exist "dashboard" mkdir dashboard
if not exist "core" mkdir core
if not exist "ip_management" mkdir ip_management
if not exist "logging" mkdir logging

echo ✅ Directories created
echo.

REM Create __init__.py files
echo 📝 Creating Python package files...
type nul > core\__init__.py
type nul > ip_management\__init__.py
type nul > event_logging\__init__.py
type nul > dashboard\__init__.py
type nul > tests\__init__.py
type nul > demo\__init__.py

echo ✅ Package files created
echo.

REM Create virtual environment
echo 🐍 Creating virtual environment...
if exist "venv" (
    echo ⚠️  Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    echo ✅ Virtual environment created
)
echo.

REM Activate virtual environment
echo ✅ Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install dependencies
echo 📦 Installing dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt --quiet
    echo ✅ Dependencies installed
) else (
    echo ⚠️  requirements.txt not found. Skipping dependency installation.
)
echo.

REM Create default config.yaml
echo ⚙️  Creating default configuration...
if not exist "config\config.yaml" (
    (
        echo simulation:
        echo   concurrent_sessions: 5
        echo   total_sessions: 100
        echo   session_duration_range: [30, 180]  # seconds
        echo   clicks_per_session_range: [2, 8]
        echo.
        echo ip_pool:
        echo   source: "config/ips.csv"
        echo   rotation_strategy: "weighted"  # round-robin, random, weighted
        echo   reputation_threshold: 0.7
        echo   max_requests_per_ip: 1000
        echo.
        echo behavior:
        echo   dwell_time_mean: 45  # seconds
        echo   dwell_time_stddev: 15
        echo   scroll_probability: 0.8
        echo   click_delay_range: [1, 5]
        echo   search_queries:
        echo     - "aseraffles.com"
        echo     - "python tutorial for beginners"
        echo     - "weather forecast today"
        echo.
        echo logging:
        echo   database: "data/events.db"
        echo   log_level: "INFO"
        echo   log_file: "logs/bot.log"
        echo.
        echo dashboard:
        echo   type: "cli"  # cli or web
        echo   refresh_rate: 2  # seconds
    ) > config\config.yaml
    echo ✅ config\config.yaml created
) else (
    echo ⚠️  config\config.yaml already exists. Skipping.
)
echo.

REM Create default ips.csv
echo 🌐 Creating IP pool...
if not exist "config\ips.csv" (
    (
        echo ip,proxy_type,country,reputation_score
        echo 192.168.1.1,residential,US,1.0
        echo 192.168.1.2,residential,US,1.0
        echo 192.168.1.3,residential,US,1.0
        echo 192.168.1.4,residential,US,1.0
        echo 192.168.1.5,residential,US,1.0
        echo 192.168.1.6,residential,US,1.0
        echo 192.168.1.7,residential,US,1.0
        echo 192.168.1.8,residential,US,1.0
        echo 192.168.1.9,residential,US,1.0
        echo 192.168.1.10,residential,US,1.0
        echo 192.168.1.11,residential,UK,1.0
        echo 192.168.1.12,residential,UK,1.0
        echo 192.168.1.13,residential,CA,1.0
        echo 192.168.1.14,residential,CA,1.0
        echo 192.168.1.15,residential,AU,1.0
        echo 192.168.1.16,residential,AU,1.0
        echo 192.168.1.17,residential,DE,1.0
        echo 192.168.1.18,residential,DE,1.0
        echo 192.168.1.19,residential,FR,1.0
        echo 192.168.1.20,residential,FR,1.0
    ) > config\ips.csv
    echo ✅ config\ips.csv created (20 sample IPs)
) else (
    echo ⚠️  config\ips.csv already exists. Skipping.
)
echo.

REM Create .gitignore
echo 📋 Creating .gitignore...
if not exist ".gitignore" (
    (
        echo # Python
        echo __pycache__/
        echo *.py[cod]
        echo *$py.class
        echo *.so
        echo .Python
        echo build/
        echo develop-eggs/
        echo dist/
        echo downloads/
        echo eggs/
        echo .eggs/
        echo lib/
        echo lib64/
        echo parts/
        echo sdist/
        echo var/
        echo wheels/
        echo *.egg-info/
        echo .installed.cfg
        echo *.egg
        echo MANIFEST
        echo.
        echo # Virtual Environment
        echo venv/
        echo env/
        echo ENV/
        echo env.bak/
        echo venv.bak/
        echo.
        echo # Database
        echo data/
        echo *.db
        echo *.sqlite
        echo *.sqlite3
        echo.
        echo # Logs
        echo logs/
        echo *.log
        echo.
        echo # IDE
        echo .vscode/
        echo .idea/
        echo *.swp
        echo *.swo
        echo.
        echo # OS
        echo .DS_Store
        echo Thumbs.db
        echo.
        echo # Temporary
        echo *.tmp
        echo temp/
        echo tmp/
        echo.
        echo # Environment variables
        echo .env
        echo .env.local
    ) > .gitignore
    echo ✅ .gitignore created
) else (
    echo ⚠️  .gitignore already exists. Skipping.
)
echo.

REM Create placeholder files
type nul > logs\.gitkeep
type nul > data\.gitkeep

REM Summary
echo ==========================================
echo ✅ Initialization complete!
echo ==========================================
echo.
echo 📊 Project Structure:
echo    ├── config\           ✅ Configuration files
echo    ├── core\             ✅ Core simulation engine
echo    ├── ip_management\    ✅ IP rotation system
echo    ├── logging\          ✅ Event logging
echo    ├── dashboard\        ✅ Monitoring dashboard
echo    ├── demo\             ✅ Demo scripts
echo    ├── data\             ✅ Database storage
echo    ├── logs\             ✅ Log files
echo    └── venv\             ✅ Virtual environment
echo.
echo 🚀 Quick Start Commands:
echo.
echo    1. Activate virtual environment:
echo       venv\Scripts\activate.bat
echo.
echo    2. Run a small test (10 sessions):
echo       python demo\demo.py --sessions 10 --workers 2
echo.
echo    3. Run full demo (100 sessions):
echo       python demo\demo.py --sessions 100 --workers 5
echo.
echo    4. View dashboard (in separate terminal):
echo       python dashboard\cli_dashboard.py
echo.
echo 📚 Next Steps:
echo    - Ensure all Python files are in place
echo    - Review config\config.yaml settings
echo    - Add real proxy IPs to config\ips.csv (optional)
echo    - Run demo to generate test data
echo    - View README.md for detailed documentation
echo.
echo ⚠️  Remember: This is an MVP. See documentation for limitations.
echo.
pause