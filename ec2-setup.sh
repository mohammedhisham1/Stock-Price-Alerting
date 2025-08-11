#!/bin/bash

# EC2 Setup Script for Stock Price Alerting System - Amazon Linux
# Run this script on a fresh Amazon Linux 2023 or Amazon Linux 2 EC2 instance

set -e

echo "🚀 Starting EC2 setup for Stock Price Alerting System (Amazon Linux)..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Detect Amazon Linux version
if grep -q "Amazon Linux 2023" /etc/os-release; then
    AMAZON_LINUX_VERSION="2023"
elif grep -q "Amazon Linux 2" /etc/os-release; then
    AMAZON_LINUX_VERSION="2"
else
    print_error "Unsupported OS. This script is for Amazon Linux 2 or 2023."
    exit 1
fi

print_status "Detected Amazon Linux $AMAZON_LINUX_VERSION"

# Update system
print_status "Updating system packages..."
sudo yum update -y

# Install Python based on AL version
if [ "$AMAZON_LINUX_VERSION" = "2023" ]; then
    print_status "Installing Python 3.11 for Amazon Linux 2023..."
    sudo yum install -y python3.11 python3.11-pip python3.11-devel
    sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
    sudo alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.11 1
else
    print_status "Installing Python 3.8 for Amazon Linux 2..."
    sudo amazon-linux-extras install python3.8 -y
    sudo yum install -y python3-pip python3-devel
fi

# Install system dependencies
print_status "Installing system dependencies..."
sudo yum groupinstall -y "Development Tools"
sudo yum install -y gcc gcc-c++ make

# Database client
if [ "$AMAZON_LINUX_VERSION" = "2023" ]; then
    sudo yum install -y postgresql15-devel postgresql15 || sudo yum install -y postgresql-devel postgresql
else
    sudo yum install -y postgresql-devel postgresql
fi

# Web server and process management
sudo yum install -y nginx supervisor

# Git and utilities
sudo yum install -y git curl wget htop

# Redis Server
print_status "Installing and configuring Redis..."
sudo yum install -y redis
sudo systemctl enable redis
sudo systemctl start redis

# Clone repository (if not already present)
if [ ! -d "/home/ec2-user/Stock-Price-Alerting" ]; then
    print_status "Cloning repository..."
    cd /home/ec2-user
    git clone https://github.com/mohammedhisham1/Stock-Price-Alerting.git
fi

cd /home/ec2-user/Stock-Price-Alerting

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
    print_warning "IMPORTANT: Edit /home/ec2-user/Stock-Price-Alerting/.env with your configuration!"
    print_warning "Required: DB credentials, API keys, email settings"
fi

# Create supervisor configuration
print_status "Creating Supervisor configuration..."
sudo mkdir -p /var/log/supervisor
sudo tee /etc/supervisord.d/stockalerting.ini > /dev/null <<EOF
[program:stockalerting_django]
command=/home/ec2-user/Stock-Price-Alerting/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 stock_alerting.wsgi:application
directory=/home/ec2-user/Stock-Price-Alerting
user=ec2-user
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/stockalerting_django.log
environment=PATH="/home/ec2-user/Stock-Price-Alerting/venv/bin"

[program:stockalerting_celery]
command=/home/ec2-user/Stock-Price-Alerting/venv/bin/celery -A stock_alerting worker -l info
directory=/home/ec2-user/Stock-Price-Alerting
user=ec2-user
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/stockalerting_celery.log
environment=PATH="/home/ec2-user/Stock-Price-Alerting/venv/bin"

[program:stockalerting_beat]
command=/home/ec2-user/Stock-Price-Alerting/venv/bin/celery -A stock_alerting beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
directory=/home/ec2-user/Stock-Price-Alerting
user=ec2-user
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/stockalerting_beat.log
environment=PATH="/home/ec2-user/Stock-Price-Alerting/venv/bin"

[group:stockalerting]
programs=stockalerting_django,stockalerting_celery,stockalerting_beat
EOF

# Enable supervisord
sudo systemctl enable supervisord
sudo systemctl start supervisord

# Create Nginx configuration
print_status "Creating Nginx configuration..."
sudo tee /etc/nginx/conf.d/stockalerting.conf > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    client_max_body_size 4G;

    location /static/ {
        alias /home/ec2-user/Stock-Price-Alerting/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/ec2-user/Stock-Price-Alerting/media/;
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

# Test Nginx configuration
sudo nginx -t

# Setup firewall
print_status "Configuring firewall..."
if command -v firewall-cmd &> /dev/null; then
    sudo systemctl enable firewalld
    sudo systemctl start firewalld
    sudo firewall-cmd --permanent --add-service=ssh
    sudo firewall-cmd --permanent --add-service=http
    sudo firewall-cmd --permanent --add-service=https
    sudo firewall-cmd --reload
else
    print_warning "firewalld not available, please configure security groups in AWS console"
fi

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

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/stockalerting /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Setup firewall
print_status "Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

print_status "Base setup completed!"
print_warning "NEXT STEPS:"
print_warning "1. Edit .env file: nano /home/ec2-user/Stock-Price-Alerting/.env"
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
