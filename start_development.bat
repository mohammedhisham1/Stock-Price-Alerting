@echo off
REM Full Stack Development Startup Script for Windows
REM This script starts both Django backend and React frontend

echo 🚀 Starting Stock Price Alerting System...
echo =========================================

REM Check prerequisites
echo Checking prerequisites...

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python is required but not installed.
    pause
    exit /b 1
)

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js is required but not installed.
    pause
    exit /b 1
)

where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ npm is required but not installed.
    pause
    exit /b 1
)

echo ✅ All prerequisites are installed

REM Navigate to project directory
cd /d "%~dp0"

REM Install Python dependencies
if exist requirements.txt (
    echo Installing Python dependencies...
    pip install -r requirements.txt
)

REM Run Django migrations
echo Running database migrations...
python manage.py migrate

REM Load initial stock data
echo Loading initial stock data...
python manage.py loaddata seed_data.json

REM Start Django development server
echo Starting Django server on http://localhost:8000...
start "Django Server" cmd /k "python manage.py runserver 8000"

REM Wait a moment for Django to start
timeout /t 3

REM Start Celery worker
echo Starting Celery worker...
start "Celery Worker" cmd /k "celery -A stock_alerting worker --loglevel=info"

REM Start Celery beat
echo Starting Celery beat scheduler...
start "Celery Beat" cmd /k "celery -A stock_alerting beat --loglevel=info"

REM Start React frontend
echo Starting React frontend...
cd frontend

REM Install Node dependencies
if exist package.json (
    echo Installing Node.js dependencies...
    npm install
)

REM Start React development server
echo Starting React server on http://localhost:3000...
start "React Server" cmd /k "npm start"

echo.
echo ✅ Django backend started
echo ✅ React frontend started
echo.
echo 🎉 Stock Price Alerting System is now running!
echo =========================================
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000/api
echo Django Admin: http://localhost:8000/admin
echo.
echo Note: Separate command windows have been opened for each service.
echo Close those windows to stop the respective services.
echo.

pause
