#!/bin/bash

# AWS EC2 Deployment Script for Stock Price Alerting System
# Run this script on your EC2 instance as ubuntu user

set -e

echo "🚀 Starting deployment of Stock Price Alerting System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Update system
echo -e "${YELLOW}Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# Install required packages
echo -e "${YELLOW}Installing system dependencies...${NC}"
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx git curl -y

# Setup PostgreSQL
echo -e "${YELLOW}Setting up PostgreSQL database...${NC}"
sudo -u postgres psql -c "CREATE DATABASE stock_alerting;" || true
sudo -u postgres psql -c "CREATE USER stockuser WITH ENCRYPTED PASSWORD 'stockuser123';" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE stock_alerting TO stockuser;" || true
sudo -u postgres psql -c "ALTER USER stockuser CREATEDB;" || true

# Start services
echo -e "${YELLOW}Starting services...${NC}"
sudo systemctl start postgresql redis-server
sudo systemctl enable postgresql redis-server

# Setup application
echo -e "${YELLOW}Setting up application...${NC}"
cd /home/ubuntu

# Clone or update repository
if [ -d "Stock-Price-Alerting" ]; then
    cd Stock-Price-Alerting
    git pull
else
    git clone https://github.com/mohammedhisham1/Stock-Price-Alerting.git
    cd Stock-Price-Alerting
fi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cat > .env << EOL
DEBUG=False
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DATABASE_URL=postgresql://stockuser:stockuser123@localhost:5432/stock_alerting
ALLOWED_HOSTS=*
TWELVE_DATA_API_KEY=your-api-key-here
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
EOL
    echo -e "${RED}⚠️  Please edit .env file with your actual configuration values${NC}"
fi

# Run Django setup
echo -e "${YELLOW}Running Django migrations...${NC}"
python manage.py migrate

# Create superuser (skip if exists)
echo -e "${YELLOW}Creating superuser...${NC}"
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
" || true

# Collect static files
echo -e "${YELLOW}Collecting static files...${NC}"
python manage.py collectstatic --noinput

# Setup systemd services
echo -e "${YELLOW}Setting up systemd services...${NC}"
sudo cp deployment/stock-alerting.service /etc/systemd/system/
sudo cp deployment/celery.service /etc/systemd/system/
sudo cp deployment/celerybeat.service /etc/systemd/system/

# Create required directories
sudo mkdir -p /var/run/celery /var/log/celery
sudo chown ubuntu:ubuntu /var/run/celery /var/log/celery

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable stock-alerting celery celerybeat
sudo systemctl start stock-alerting celery celerybeat

# Setup Nginx
echo -e "${YELLOW}Setting up Nginx...${NC}"
sudo cp deployment/nginx.conf /etc/nginx/sites-available/stock-alerting
sudo ln -sf /etc/nginx/sites-available/stock-alerting /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and restart Nginx
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit .env file with your actual API keys and credentials"
echo "2. Update Nginx config with your domain name"
echo "3. Setup SSL with Let's Encrypt (optional)"
echo "4. Add your stocks to the database"
echo ""
echo -e "${GREEN}Your application is running on:${NC}"
echo "🌐 Backend API: http://$(curl -s ifconfig.me):8000/api/"
echo "📚 API Docs: http://$(curl -s ifconfig.me):8000/api/docs/"
echo "🔧 Admin Panel: http://$(curl -s ifconfig.me):8000/admin/"
echo ""
echo -e "${YELLOW}Service management commands:${NC}"
echo "sudo systemctl status stock-alerting"
echo "sudo systemctl status celery"
echo "sudo systemctl status celerybeat"
echo "sudo journalctl -u stock-alerting -f"
