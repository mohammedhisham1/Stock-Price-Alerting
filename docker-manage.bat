@echo off
REM Docker Setup and Management Script for Stock Price Alerting System (Windows)

title Stock Price Alerting System - Docker Management

echo 🐳 Stock Price Alerting System - Docker Management
echo ==================================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

if "%1"=="build" goto build
if "%1"=="dev" goto dev
if "%1"=="prod" goto prod
if "%1"=="stop" goto stop
if "%1"=="cleanup" goto cleanup
if "%1"=="logs" goto logs
if "%1"=="status" goto status
if "%1"=="shell" goto shell
if "%1"=="manage" goto manage
if "%1"=="reset-db" goto reset_db
if "%1"=="" goto help
goto help

:build
echo [INFO] Building Docker images...
docker-compose build --no-cache
echo [INFO] Images built successfully
goto end

:dev
echo [INFO] Starting development environment...
echo [INFO] Using main docker-compose.yml with development settings
set DEBUG=True
docker-compose up -d
echo [INFO] Development environment started
echo [INFO] Backend: http://localhost:8000
echo [INFO] Database: localhost:5432
echo [INFO] Redis: localhost:6379
goto end

:prod
echo [INFO] Starting production environment...
set DEBUG=False
docker-compose up -d
echo [INFO] Production environment started
echo [INFO] Backend API: http://localhost:8000
echo [INFO] API Documentation: http://localhost:8000/api/docs/
echo [INFO] Note: Frontend should be deployed to Vercel separately
goto end

:stop
echo [INFO] Stopping all services...
docker-compose down
echo [INFO] All services stopped
goto end

:cleanup
echo [WARNING] This will remove all containers, images, and volumes!
set /p confirm="Are you sure? (y/N): "
if /i "%confirm%"=="y" (
    echo [INFO] Cleaning up...
    docker-compose down -v --rmi all
    docker system prune -f
    echo [INFO] Cleanup completed
) else (
    echo [INFO] Cleanup cancelled
)
goto end

:logs
docker-compose logs -f
goto end

:status
echo [INFO] Container Status:
docker-compose ps
goto end

:shell
docker-compose exec backend python manage.py shell
goto end

:manage
if "%2"=="" (
    echo [ERROR] Please provide a Django command
    goto end
)
echo [INFO] Running Django command: %2 %3 %4 %5 %6 %7 %8 %9
docker-compose exec backend python manage.py %2 %3 %4 %5 %6 %7 %8 %9
goto end

:reset_db
echo [WARNING] This will reset the database and load seed data!
set /p confirm="Are you sure? (y/N): "
if /i "%confirm%"=="y" (
    echo [INFO] Resetting database...
    docker-compose exec backend python manage.py flush --noinput
    docker-compose exec backend python manage.py migrate
    docker-compose exec backend python manage.py loaddata seed_data_fixed.json
    echo [INFO] Database reset completed
) else (
    echo [INFO] Database reset cancelled
)
goto end

:help
echo Usage: %0 [COMMAND]
echo.
echo Commands:
echo   build          Build Docker images
echo   dev            Start development environment
echo   prod           Start production environment
echo   stop           Stop all services
echo   cleanup        Remove all containers, images, and volumes
echo   logs [dev]     Show logs (add 'dev' for development environment)
echo   status         Show container status
echo   shell          Open Django shell in backend container
echo   manage ^<cmd^>   Run Django management command
echo   reset-db       Reset database and load seed data
echo   help           Show this help message
echo.
echo Examples:
echo   %0 dev                    # Start development environment
echo   %0 manage migrate         # Run migrations
echo   %0 manage createsuperuser # Create Django superuser
echo   %0 logs dev               # Show development logs
goto end

:end
if "%1"=="" pause
