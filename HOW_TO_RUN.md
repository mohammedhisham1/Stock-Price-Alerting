# 🚀 How to Run the Stock Price Alerting System

## 🎯 Quick Start Guide

**Choose your setup:**

### 🔥 Full Stack Development (Recommended for Development)
```cmd
# Terminal 1: Backend services
cd e:\Stock-Price-Alerting
.\docker-manage.bat dev

# Terminal 2: Frontend with hot reload  
cd e:\Stock-Price-Alerting\frontend
npm install && npm start
```
**Access:** Frontend http://localhost:3000 | Backend http://localhost:8000

### 🚀 Full Stack Production (One Command)
```cmd
cd e:\Stock-Price-Alerting
.\docker-manage.bat prod
```
**Access:** Frontend http://localhost | Backend http://localhost:8000

### ⚙️ Backend Only (API Development)
```cmd
cd e:\Stock-Price-Alerting  
.\docker-manage.bat dev
```
**Access:** Backend API http://localhost:8000 | Admin http://localhost:8000/admin

## 📋 Prerequisites

Before running the project, make sure you have:

✅ **Docker Desktop** installed and running
✅ **Git** (to clone/manage the repository)
✅ **Windows PowerShell** or **Command Prompt**

### Check Prerequisites
```cmd
# Check Docker
docker --version
docker-compose --version

# Check if Docker is running
docker info
```

## 🐳 Running with Docker (Recommended)

### Option 1: Full Stack Development (Backend + Frontend)
```cmd
# Navigate to project directory
cd e:\Stock-Price-Alerting

# Start complete development environment
.\docker-manage.bat dev

# This starts:
# - Django backend (localhost:8000)
# - PostgreSQL database
# - Redis cache
# - Celery workers
# Note: Frontend runs separately for development
```

### Option 2: Full Stack Production (Backend + Frontend)
```cmd
# Navigate to project directory
cd e:\Stock-Price-Alerting

# Start complete production environment
.\docker-manage.bat prod

# This starts:
# - Django backend (localhost:8000)
# - React frontend (localhost:80)
# - PostgreSQL database
# - Redis cache  
# - Celery workers
# - Nginx web server
```

### Option 3: Backend Only (for API development)
```cmd
cd e:\Stock-Price-Alerting
docker-compose -f docker-compose.dev.yml up -d db redis backend celery

# This starts only:
# - Django backend (localhost:8000)
# - PostgreSQL database
# - Redis cache
# - Celery workers
```

### Option 4: Manual Docker Commands

#### Full Stack Development
```cmd
cd e:\Stock-Price-Alerting
docker-compose -f docker-compose.dev.yml up -d
```

#### Full Stack Production
```cmd
cd e:\Stock-Price-Alerting
docker-compose up -d
```

#### Backend Services Only
```cmd
cd e:\Stock-Price-Alerting
docker-compose -f docker-compose.dev.yml up -d db redis backend celery celery-beat
```

## 🌐 Access the Application

### Development Mode (Full Stack)
- **Frontend (React)**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/api/
- **Health Check**: http://localhost:8000/api/health/
- **Database**: localhost:5432 (PostgreSQL)
- **Redis**: localhost:6379

### Production Mode (Full Stack)
- **Frontend (Nginx)**: http://localhost (port 80)
- **Backend API**: http://localhost:8000 (or via proxy at /api/)
- **Django Admin**: http://localhost:8000/admin

### Backend Only Mode
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **API Endpoints**: http://localhost:8000/api/

## 🔧 Management Commands

### Using Management Script
```cmd
# View all available commands
.\docker-manage.bat help

# Check container status
.\docker-manage.bat status

# View logs
.\docker-manage.bat logs

# View development logs
.\docker-manage.bat logs dev

# Stop all services
.\docker-manage.bat stop

# Run Django management commands
.\docker-manage.bat manage migrate
.\docker-manage.bat manage createsuperuser
.\docker-manage.bat manage collectstatic

# Open Django shell
.\docker-manage.bat shell

# Reset database with seed data
.\docker-manage.bat reset-db

# Complete cleanup
.\docker-manage.bat cleanup
```

### Manual Docker Commands
```cmd
# View container status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Run Django commands
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser

# Access backend shell
docker-compose exec backend python manage.py shell

# Access container bash
docker-compose exec backend bash
```

## 🔑 Default Credentials

### Admin User (Auto-created)
- **Username**: admin
- **Password**: admin123
- **Email**: admin@example.com

### Test User (From seed data)
- **Username**: testuser
- **Email**: test@example.com
- **Password**: testpass123

## 📊 First Time Setup

### Full Stack Setup (Backend + Frontend)

1. **Start the backend services**:
   ```cmd
   .\docker-manage.bat dev
   ```

2. **Start the frontend** (in a new terminal):
   ```cmd
   cd frontend
   npm install
   npm start
   ```

3. **Wait for services to start** (about 1-2 minutes)

4. **Check health status**:
   ```cmd
   .\docker-manage.bat status
   ```

5. **Access the applications**:
   - **Frontend**: http://localhost:3000 (React development server)
   - **Backend API**: http://localhost:8000
   - **Admin Panel**: http://localhost:8000/admin

### Backend Only Setup

1. **Start backend services**:
   ```cmd
   .\docker-manage.bat dev
   ```

2. **Access the backend**:
   - **API**: http://localhost:8000/api/
   - **Admin Panel**: http://localhost:8000/admin
   - **Health Check**: http://localhost:8000/api/health/

### Production Setup (All-in-One)

1. **Start production environment**:
   ```cmd
   .\docker-manage.bat prod
   ```

2. **Access the application**:
   - **Frontend**: http://localhost (served by Nginx)
   - **Backend API**: http://localhost:8000 (or via /api/ proxy)
   - **Admin Panel**: http://localhost:8000/admin

### Additional Setup Steps

5. **Create additional users** (optional):
   ```cmd
   .\docker-manage.bat manage createsuperuser
   ```

6. **Test the API**:
   ```cmd
   # Health check
   curl http://localhost:8000/api/health/
   
   # Authentication test
   curl -X POST http://localhost:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d "{\"username\": \"admin\", \"password\": \"admin123\"}"
   ```

## 🛠️ Development Workflow

### Full Stack Development (Recommended)

#### Start Both Backend and Frontend
```cmd
# Terminal 1: Start backend services
.\docker-manage.bat dev

# Terminal 2: Start frontend separately for hot reload
cd frontend
npm install
npm start
```

**Access Points:**
- Frontend: http://localhost:3000 (with hot reload)
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin

### Backend Only Development
```cmd
# Start only backend services
.\docker-manage.bat dev

# View logs to see changes
.\docker-manage.bat logs dev
```

### Frontend Only Development
```cmd
# Make sure backend is running first
.\docker-manage.bat dev

# In a new terminal, start frontend
cd frontend
npm install
npm start

# Frontend will proxy API calls to localhost:8000
```

### Making Code Changes

#### Backend Changes (Django)
```cmd
# Development mode automatically reloads on code changes
# Just edit Python files and save

# View logs to see reload
.\docker-manage.bat logs backend
```

#### Frontend Changes (React)
```cmd
# If running frontend separately:
cd frontend
npm start
# Changes auto-reload at http://localhost:3000

# If using production build:
.\docker-manage.bat prod
# Rebuild required for changes
```

### Database Operations
```cmd
# Create new migrations
.\docker-manage.bat manage makemigrations

# Apply migrations
.\docker-manage.bat manage migrate

# Load seed data
.\docker-manage.bat manage loaddata seed_data_fixed.json

# Reset database completely
.\docker-manage.bat reset-db
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```cmd
# Check what's using backend port (8000)
netstat -ano | findstr :8000

# Check what's using frontend port (3000)
netstat -ano | findstr :3000

# Check what's using production port (80)
netstat -ano | findstr :80

# Stop conflicting services or change ports in docker-compose.yml
```

#### 2. Docker Not Running
```cmd
# Start Docker Desktop
# Wait for Docker to fully start
docker info
```

#### 3. Frontend Build Issues
```cmd
# Clear npm cache
cd frontend
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Or using Docker
.\docker-manage.bat cleanup
.\docker-manage.bat build
```

#### 4. Backend Database Connection Issues
```cmd
# Restart database service
.\docker-manage.bat stop
.\docker-manage.bat dev

# Check database logs
.\docker-manage.bat logs db
```

#### 5. CORS Issues (Frontend-Backend Communication)
```cmd
# Check if backend allows frontend origin
# Backend should allow http://localhost:3000

# Check browser network tab for CORS errors
# Verify API calls are going to correct backend URL
```

#### 6. Permission Issues
```cmd
# Run PowerShell as Administrator
# Or use Command Prompt as Administrator
```

### Viewing Logs

#### All Services
```cmd
.\docker-manage.bat logs
```

#### Specific Services
```cmd
# Backend logs
docker-compose logs backend

# Frontend logs (if using Docker)
docker-compose logs frontend

# Database logs
docker-compose logs db

# Redis logs
docker-compose logs redis

# Celery worker logs
docker-compose logs celery
```

#### Frontend Development Logs
```cmd
# If running frontend with npm start
cd frontend
npm start
# Logs appear in terminal
```

### Clean Restart

#### Full Clean Restart
```cmd
# Stop everything
.\docker-manage.bat stop

# Clean up (removes all data!)
.\docker-manage.bat cleanup

# Rebuild and start fresh
.\docker-manage.bat build
.\docker-manage.bat dev

# Restart frontend separately
cd frontend
npm install
npm start
```

#### Backend Only Clean Restart
```cmd
# Stop backend services
docker-compose -f docker-compose.dev.yml down

# Remove volumes (database data)
docker-compose -f docker-compose.dev.yml down -v

# Restart
.\docker-manage.bat dev
```

#### Frontend Only Clean Restart
```cmd
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

## 🎯 Quick Test

### Test Backend API
```cmd
# Health check
curl http://localhost:8000/api/health/

# Authentication test
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"admin\", \"password\": \"admin123\"}"

# Get stocks list
curl http://localhost:8000/api/stocks/

# Register new user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"newuser\", \"email\": \"new@example.com\", \"password\": \"newpass123\", \"password2\": \"newpass123\"}"
```

### Test Frontend (Browser)
1. **Open Frontend**: http://localhost:3000 (development) or http://localhost (production)
2. **Test Registration**: Create a new account
3. **Test Login**: Login with created account or admin/admin123
4. **Test Navigation**: Check different pages/routes
5. **Test API Integration**: Create alerts, view stocks, etc.

### Test Full Stack Integration
1. **Backend Running**: ✅ http://localhost:8000/api/health/ returns OK
2. **Frontend Running**: ✅ http://localhost:3000 loads React app
3. **API Communication**: ✅ Frontend can call backend APIs
4. **Authentication Flow**: ✅ Login/register works between frontend and backend
5. **CORS Working**: ✅ No CORS errors in browser console

## 📱 Using the Application

1. **Register a new account** or use existing credentials
2. **Add stock symbols** to monitor (AAPL, TSLA, etc.)
3. **Create price alerts** with target prices
4. **View triggered alerts** in the dashboard
5. **Manage your profile** and notification settings

## 🚀 Production Deployment

### Full Stack Production (Recommended)
```cmd
# Use complete production environment (Frontend + Backend)
.\docker-manage.bat prod

# This includes:
# - React frontend (built and served by Nginx on port 80)
# - Django backend (Gunicorn on port 8000)  
# - PostgreSQL database
# - Redis cache
# - Celery workers and beat scheduler
```

**Access Points:**
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000 (or via /api/ proxy)
- **Admin**: http://localhost:8000/admin

### Backend Only Production
```cmd
cd e:\Stock-Price-Alerting
docker-compose up -d db redis backend celery celery-beat
```

### Custom Production Environment
```cmd
# Copy environment template
copy .env.docker .env

# Edit .env with production values:
# - Set DEBUG=False
# - Update SECRET_KEY
# - Configure database URLs
# - Set allowed hosts
# - Configure email settings

# Start with custom environment
docker-compose up -d
```

### Environment Variables for Production
```env
# Security
DEBUG=False
SECRET_KEY=your-super-secret-production-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Email (for alerts)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Frontend URL (for CORS)
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 📞 Getting Help

- Check logs: `.\docker-manage.bat logs`
- View status: `.\docker-manage.bat status`
- Full command list: `.\docker-manage.bat help`
- Documentation: Read `README.md` and `DOCKER_README.md`

---

**That's it! Your Stock Price Alerting System should now be running! 🎉**
