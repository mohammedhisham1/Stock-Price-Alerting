@echo off
REM AWS Deployment Script for Stock Price Alerting Backend (Windows)
REM This script assumes you have:
REM - AWS RDS PostgreSQL database already created
REM - EC2 instance with Docker and Docker Compose installed
REM - Your .env file configured with RDS credentials

title Stock Price Alerting - AWS Deployment

echo 🚀 Deploying Stock Price Alerting Backend to AWS
echo ================================================

REM Check if .env file exists
if not exist ".env" (
    echo ❌ Error: .env file not found!
    echo Please create .env file with your RDS and other configurations
    pause
    exit /b 1
)

echo 📋 Current configuration:
echo - Using AWS RDS PostgreSQL (external)
echo - Using local Redis container
echo - Django + Celery + Celery Beat
echo.

REM Pull latest code (if in git repository)
echo 📦 Pulling latest code...
git pull origin main 2>nul || echo Not a git repository or no updates

REM Stop any existing containers
echo 🛑 Stopping existing containers...
docker-compose down

REM Build fresh images
echo 🔨 Building Docker images...
docker-compose build --no-cache

REM Start services
echo 🚀 Starting services...
docker-compose up -d

REM Wait for services to start
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check service status
echo 📊 Service Status:
docker-compose ps

REM Test database connection
echo 🔍 Testing database connection...
docker-compose exec -T backend python manage.py migrate --check
if %errorlevel% neq 0 (
    echo ❌ Database connection failed!
    echo Please check your RDS configuration in .env file
    pause
    exit /b 1
)

REM Run migrations
echo 📊 Running database migrations...
docker-compose exec -T backend python manage.py migrate

REM Collect static files
echo 📁 Collecting static files...
docker-compose exec -T backend python manage.py collectstatic --noinput

REM Test API health
echo 🏥 Testing API health...
timeout /t 5 /nobreak >nul
curl -f http://localhost:8000/api/health/ >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ API health check failed!
    echo Check logs with: docker-compose logs backend
    pause
    exit /b 1
)

echo ✅ Deployment completed successfully!
echo.
echo 🌐 Your API is now running at:
echo - API: http://your-ec2-public-ip:8000
echo - Health Check: http://your-ec2-public-ip:8000/api/health/
echo - API Docs: http://your-ec2-public-ip:8000/api/docs/
echo.
echo 📋 Useful commands:
echo - View logs: docker-compose logs -f
echo - Check status: docker-compose ps
echo - Stop services: docker-compose down
echo.
echo 🔧 Don't forget to:
echo 1. Update your EC2 security group to allow inbound traffic on port 8000
echo 2. Update CORS_ALLOWED_ORIGINS in .env with your Vercel frontend URL
echo 3. Update ALLOWED_HOSTS in .env with your EC2 public IP

pause
