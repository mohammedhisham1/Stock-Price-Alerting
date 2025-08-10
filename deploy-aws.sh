#!/bin/bash

# AWS Deployment Script for Stock Price Alerting Backend
# This script assumes you have:
# - AWS RDS PostgreSQL database already created
# - EC2 instance with Docker and Docker Compose installed
# - Your .env file configured with RDS credentials

echo "🚀 Deploying Stock Price Alerting Backend to AWS"
echo "================================================"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with your RDS and other configurations"
    exit 1
fi

echo "📋 Current configuration:"
echo "- Using AWS RDS PostgreSQL (external)"
echo "- Using local Redis container"
echo "- Django + Celery + Celery Beat"

# Pull latest code (if in git repository)
echo "📦 Pulling latest code..."
git pull origin main || echo "Not a git repository or no updates"

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build fresh images
echo "🔨 Building Docker images..."
docker-compose build --no-cache

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker-compose ps

# Test database connection
echo "🔍 Testing database connection..."
docker-compose exec -T backend python manage.py migrate --check || {
    echo "❌ Database connection failed!"
    echo "Please check your RDS configuration in .env file"
    exit 1
}

# Run migrations
echo "📊 Running database migrations..."
docker-compose exec -T backend python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
docker-compose exec -T backend python manage.py collectstatic --noinput

# Test API health
echo "🏥 Testing API health..."
sleep 5
curl -f http://localhost:8000/api/health/ || {
    echo "❌ API health check failed!"
    echo "Check logs with: docker-compose logs backend"
    exit 1
}

echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Your API is now running at:"
echo "- API: http://your-ec2-public-ip:8000"
echo "- Health Check: http://your-ec2-public-ip:8000/api/health/"
echo "- API Docs: http://your-ec2-public-ip:8000/api/docs/"
echo ""
echo "📋 Useful commands:"
echo "- View logs: docker-compose logs -f"
echo "- Check status: docker-compose ps"
echo "- Stop services: docker-compose down"
echo ""
echo "🔧 Don't forget to:"
echo "1. Update your EC2 security group to allow inbound traffic on port 8000"
echo "2. Update CORS_ALLOWED_ORIGINS in .env with your Vercel frontend URL"
echo "3. Update ALLOWED_HOSTS in .env with your EC2 public IP"
