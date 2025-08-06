#!/bin/bash

# Full Stack Development Startup Script
# This script starts both Django backend and React frontend

echo "🚀 Starting Stock Price Alerting System..."
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is required but not installed.${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ npm is required but not installed.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites are installed${NC}"

# Start Redis (if available)
echo -e "${BLUE}Starting Redis server...${NC}"
if command_exists redis-server; then
    redis-server --daemonize yes
    echo -e "${GREEN}✅ Redis server started${NC}"
else
    echo -e "${YELLOW}⚠️ Redis not found. Install Redis for background tasks.${NC}"
fi

# Start Django backend
echo -e "${BLUE}Starting Django backend...${NC}"
cd "$(dirname "$0")"

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip3 install -r requirements.txt
fi

# Run Django migrations
echo "Running database migrations..."
python3 manage.py migrate

# Load initial stock data
echo "Loading initial stock data..."
python3 manage.py loaddata seed_data.json

# Start Django development server in background
echo "Starting Django server on http://localhost:8000..."
python3 manage.py runserver 8000 &
DJANGO_PID=$!

# Start Celery worker in background
echo "Starting Celery worker..."
celery -A stock_alerting worker --loglevel=info &
CELERY_WORKER_PID=$!

# Start Celery beat in background
echo "Starting Celery beat scheduler..."
celery -A stock_alerting beat --loglevel=info &
CELERY_BEAT_PID=$!

echo -e "${GREEN}✅ Django backend started (PID: $DJANGO_PID)${NC}"

# Start React frontend
echo -e "${BLUE}Starting React frontend...${NC}"
cd frontend

# Install Node dependencies
if [ -f "package.json" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Start React development server
echo "Starting React server on http://localhost:3000..."
npm start &
REACT_PID=$!

echo -e "${GREEN}✅ React frontend started (PID: $REACT_PID)${NC}"

# Display startup information
echo ""
echo -e "${GREEN}🎉 Stock Price Alerting System is now running!${NC}"
echo "========================================="
echo -e "${BLUE}Frontend:${NC} http://localhost:3000"
echo -e "${BLUE}Backend API:${NC} http://localhost:8000/api"
echo -e "${BLUE}Django Admin:${NC} http://localhost:8000/admin"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping all services...${NC}"
    
    if [ ! -z "$REACT_PID" ]; then
        kill $REACT_PID 2>/dev/null
        echo -e "${GREEN}✅ React frontend stopped${NC}"
    fi
    
    if [ ! -z "$DJANGO_PID" ]; then
        kill $DJANGO_PID 2>/dev/null
        echo -e "${GREEN}✅ Django backend stopped${NC}"
    fi
    
    if [ ! -z "$CELERY_WORKER_PID" ]; then
        kill $CELERY_WORKER_PID 2>/dev/null
        echo -e "${GREEN}✅ Celery worker stopped${NC}"
    fi
    
    if [ ! -z "$CELERY_BEAT_PID" ]; then
        kill $CELERY_BEAT_PID 2>/dev/null
        echo -e "${GREEN}✅ Celery beat stopped${NC}"
    fi
    
    echo -e "${GREEN}👋 All services stopped. Goodbye!${NC}"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user input to keep script running
while true; do
    sleep 1
done
