# Docker Setup for Stock Price Alerting System

This document explains how to run the Stock Price Alerting System using Docker.

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0 or higher
- At least 4GB of available RAM
- At least 2GB of free disk space

## Quick Start

### 1. Clone and Navigate to Project
```bash
git clone <repository-url>
cd Stock-Price-Alerting
```

### 2. Start Development Environment
```bash
# On Linux/Mac
./docker-manage.sh dev

# On Windows
docker-manage.bat dev
```

### 3. Start Production Environment
```bash
# On Linux/Mac
./docker-manage.sh prod

# On Windows
docker-manage.bat prod
```

## Architecture

The Docker setup includes the following services:

### Development Environment (`docker-compose.dev.yml`)
- **Django Backend**: Development server with hot reload
- **PostgreSQL Database**: For data persistence
- **Redis**: For caching and Celery task queue

### Production Environment (`docker-compose.yml`)
- **Django Backend**: Gunicorn WSGI server
- **React Frontend**: Nginx-served optimized build
- **PostgreSQL Database**: Production database
- **Redis**: Caching and task queue
- **Celery Worker**: Background task processing
- **Celery Beat**: Periodic task scheduler

## Service Details

### Backend (Django)
- **Port**: 8000
- **Health Check**: `http://localhost:8000/api/health/`
- **Admin Panel**: `http://localhost:8000/admin/`
- **API Documentation**: `http://localhost:8000/api/`

### Frontend (React)
- **Port**: 80 (production), 3000 (development)
- **URL**: `http://localhost` (production)

### Database (PostgreSQL)
- **Port**: 5432
- **Database**: `stock_alerting`
- **Username**: `postgres`
- **Password**: `postgres`

### Redis
- **Port**: 6379
- **URL**: `redis://localhost:6379/0`

## Management Commands

### Using the Management Script

The project includes management scripts for easy Docker operations:

#### Linux/Mac (`docker-manage.sh`)
```bash
# Make script executable
chmod +x docker-manage.sh

# Available commands
./docker-manage.sh build          # Build images
./docker-manage.sh dev            # Start development
./docker-manage.sh prod           # Start production
./docker-manage.sh stop           # Stop all services
./docker-manage.sh status         # Show container status
./docker-manage.sh logs           # Show logs
./docker-manage.sh logs dev       # Show development logs
./docker-manage.sh shell          # Django shell
./docker-manage.sh manage migrate # Run Django commands
./docker-manage.sh reset-db       # Reset database
./docker-manage.sh cleanup        # Remove everything
```

#### Windows (`docker-manage.bat`)
```cmd
# Available commands
docker-manage.bat build          # Build images
docker-manage.bat dev            # Start development
docker-manage.bat prod           # Start production
docker-manage.bat stop           # Stop all services
docker-manage.bat status         # Show container status
docker-manage.bat logs           # Show logs
docker-manage.bat logs dev       # Show development logs
docker-manage.bat shell          # Django shell
docker-manage.bat manage migrate # Run Django commands
docker-manage.bat reset-db       # Reset database
docker-manage.bat cleanup        # Remove everything
```

### Manual Docker Commands

If you prefer using Docker commands directly:

#### Development Environment
```bash
# Start services
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

#### Production Environment
```bash
# Build and start services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Django Management Commands
```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Collect static files
docker-compose exec backend python manage.py collectstatic

# Load seed data
docker-compose exec backend python manage.py loaddata seed_data_fixed.json

# Django shell
docker-compose exec backend python manage.py shell
```

## Environment Configuration

### Development
The development environment uses default settings with:
- Debug mode enabled
- SQLite database (for development simplicity)
- Hot reload for code changes

### Production
For production deployment:

1. **Copy environment template**:
   ```bash
   cp .env.docker .env
   ```

2. **Edit environment variables**:
   ```bash
   # Required changes for production
   DEBUG=False
   SECRET_KEY=your-super-secret-production-key
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   
   # Optional: Email configuration
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   
   
   ```

## Persistent Data

Docker volumes are used for persistent data:

- **postgres_data**: PostgreSQL database files
- **redis_data**: Redis data files
- **static_volume**: Django static files
- **media_volume**: User uploaded files

## Troubleshooting

### Common Issues

1. **Port conflicts**: Make sure ports 80, 8000, 5432, and 6379 are not in use
2. **Permission denied**: On Linux/Mac, make sure Docker has proper permissions
3. **Out of memory**: Ensure at least 4GB RAM is available for Docker

### Health Checks

Check service health:
```bash
# Backend health
curl http://localhost:8000/api/health/

# Database connection
docker-compose exec backend python manage.py check --database default

# Redis connection
docker-compose exec redis redis-cli ping
```

### Viewing Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
docker-compose logs redis

# Follow logs in real-time
docker-compose logs -f backend
```

### Rebuilding Images

If you make changes to Dockerfile or requirements:
```bash
# Rebuild all images
docker-compose build --no-cache

# Rebuild specific service
docker-compose build --no-cache backend
```

### Reset Everything

To start fresh:
```bash
# Stop and remove everything
docker-compose down -v --rmi all

# Remove unused Docker resources
docker system prune -a

# Rebuild and start
docker-compose up -d --build
```

## Production Deployment

For production deployment on a server:

1. **Set up environment variables**
2. **Use proper domain names in ALLOWED_HOSTS**
3. **Set up SSL/TLS (not included in this setup)**
4. **Configure proper backup for database volumes**
5. **Set up monitoring and logging**
6. **Consider using orchestration (Docker Swarm/Kubernetes)**

## Security Considerations

- Change default passwords in production
- Use strong SECRET_KEY
- Set DEBUG=False in production
- Configure proper firewall rules
- Regularly update Docker images
- Use Docker secrets for sensitive data in production

## Performance Optimization

- Use multi-stage builds for smaller images
- Configure proper resource limits
- Use Redis for caching
- Optimize database queries
- Enable gzip compression in Nginx
- Use CDN for static files in production
