@echo off
echo 🚀 Setting up Stock Price Alerting System...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed.
    pause
    exit /b 1
)

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Copy environment file
echo ⚙️ Setting up environment variables...
if not exist .env (
    copy .env.example .env
    echo ✅ Created .env file. Please edit it with your configuration.
) else (
    echo ✅ .env file already exists.
)

REM Run migrations
echo 🗄️ Setting up database...
python manage.py makemigrations
python manage.py migrate

REM Load seed data
echo 🌱 Loading seed data...
python manage.py loaddata seed_data.json

REM Initialize stocks
echo 📈 Initializing monitored stocks...
python manage.py init_stocks

REM Collect static files
echo 📁 Collecting static files...
python manage.py collectstatic --noinput

echo.
echo ✅ Setup completed successfully!
echo.
echo 🔧 Next steps:
echo 1. Edit .env file with your API keys and email configuration:
echo    - Get a free API key from https://twelvedata.com/
echo    - Configure Gmail SMTP settings
echo.
echo 2. Start Redis server (required for Celery):
echo    - Download Redis for Windows or use Docker
echo    - Start Redis: redis-server
echo.
echo 3. Start the development server:
echo    python manage.py runserver
echo.
echo 4. In separate terminals, start Celery worker and beat:
echo    celery -A stock_alerting worker -l info
echo    celery -A stock_alerting beat -l info
echo.
echo 5. Visit http://localhost:8000/admin/ to access Django admin
echo 6. API documentation is available in API_DOCUMENTATION.md
echo 7. Test the health endpoint: http://localhost:8000/health/
echo.
echo 🎉 Happy coding!
pause
