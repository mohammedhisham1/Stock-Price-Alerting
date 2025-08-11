#!/bin/bash

# EC2 Backend Setup Script for Stock Price Alerting System
# Architecture: EC2 Backend + Vercel Frontend + RDS Database
# Run this script on a fresh Ubuntu 22.04 LTS or Ubuntu 20.04 LTS EC2 instance

set -e

echo "🚀 Starting EC2 Backend setup for Stock Price Alerting System..."
echo "📊 Architecture: EC2 Backend + Vercel Frontend + RDS Database"
echo "🐧 Operating System: Ubuntu Linux"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Detect Ubuntu version
UBUNTU_VERSION=$(lsb_release -rs)
print_info "Detected Ubuntu $UBUNTU_VERSION"

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip
print_status "Installing Python 3 and pip..."
sudo apt install -y python3 python3-pip python3-dev python3-venv

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt install -y build-essential gcc g++ make

# Database client
print_status "Installing PostgreSQL client..."
sudo apt install -y postgresql-client libpq-dev

# Web server and process management  
print_status "Installing Nginx and Supervisor..."
sudo apt install -y nginx supervisor

# Git and utilities
print_status "Installing utilities..."
sudo apt install -y git curl wget htop tree

# Redis Server
print_status "Installing and configuring Redis..."
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Clone repository (if not already present)
if [ ! -d "/home/ubuntu/Stock-Price-Alerting" ]; then
    print_status "Cloning repository..."
    cd /home/ubuntu
    git clone https://github.com/mohammedhisham1/Stock-Price-Alerting.git
fi

cd /home/ubuntu/Stock-Price-Alerting

# Create virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Setup environment file
if [ ! -f ".env" ]; then
    print_status "Creating environment file..."
    cp .env.example .env
    print_warning "IMPORTANT: Edit /home/ubuntu/Stock-Price-Alerting/.env with your configuration!"
    print_warning "Required: DB credentials, API keys, email settings"
fi

# Create supervisor configuration
print_status "Creating Supervisor configuration..."
sudo mkdir -p /var/log/supervisor
sudo tee /etc/supervisor/conf.d/stockalerting.conf > /dev/null <<EOF
[program:stockalerting_django]
command=/home/ubuntu/Stock-Price-Alerting/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 stock_alerting.wsgi:application
directory=/home/ubuntu/Stock-Price-Alerting
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/stockalerting_django.log
environment=PATH="/home/ubuntu/Stock-Price-Alerting/venv/bin"

[program:stockalerting_celery]
command=/home/ubuntu/Stock-Price-Alerting/venv/bin/celery -A stock_alerting worker -l info
directory=/home/ubuntu/Stock-Price-Alerting
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/stockalerting_celery.log
environment=PATH="/home/ubuntu/Stock-Price-Alerting/venv/bin"

[program:stockalerting_beat]
command=/home/ubuntu/Stock-Price-Alerting/venv/bin/celery -A stock_alerting beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
directory=/home/ubuntu/Stock-Price-Alerting
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/stockalerting_beat.log
environment=PATH="/home/ubuntu/Stock-Price-Alerting/venv/bin"

[group:stockalerting]
programs=stockalerting_django,stockalerting_celery,stockalerting_beat
EOF

# Enable supervisor
sudo systemctl enable supervisor
sudo systemctl start supervisor

# Create Nginx configuration
print_status "Creating Nginx configuration..."
sudo tee /etc/nginx/sites-available/stockalerting > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    client_max_body_size 4G;

    location /static/ {
        alias /home/ubuntu/Stock-Price-Alerting/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/ubuntu/Stock-Price-Alerting/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/stockalerting /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Setup firewall (Ubuntu uses ufw)
print_status "Configuring UFW firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
print_status "Firewall configured"

print_status "Base setup completed!"
print_warning "NEXT STEPS:"
print_warning "1. Edit .env file: nano /home/ubuntu/Stock-Price-Alerting/.env"
print_warning "2. Configure database, API keys, and email settings"
print_warning "3. Run: source venv/bin/activate && python manage.py migrate"
print_warning "4. Run: python manage.py createsuperuser"
print_warning "5. Run: python manage.py collectstatic --noinput"
print_warning "6. Run: python manage.py loaddata seed_data_fixed.json"
print_warning "7. Start services: sudo supervisorctl reread && sudo supervisorctl update"
print_warning "8. Start services: sudo supervisorctl start stockalerting:*"
print_warning "9. Start Nginx: sudo systemctl enable nginx && sudo systemctl start nginx"

echo ""
print_status "Setup script completed! Follow the next steps above."

# Get public IP for convenience
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "your-ec2-ip")
print_status "Access your application at: http://$PUBLIC_IP/api/"
