#!/bin/bash

# AWS EC2 Deployment Script for Stock Price Alerting System
# Run this script on your Ubuntu 20.04 EC2 instance

set -e

echo "Starting deployment of Stock Price Alerting System..."

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "Installing required packages..."
sudo apt install -y python3-pip python3-venv nginx postgresql postgresql-contrib redis-server git

# Create application user
echo "Creating application user..."
sudo adduser --disabled-password --gecos "" stockalert
sudo usermod -aG sudo stockalert

# Clone repository (replace with your actual repository URL)
echo "Cloning repository..."
sudo -u stockalert git clone https://github.com/yourusername/Stock-Price-Alerting.git /home/stockalert/app

# Setup virtual environment
echo "Setting up Python virtual environment..."
cd /home/stockalert/app
sudo -u stockalert python3 -m venv venv
sudo -u stockalert /home/stockalert/app/venv/bin/pip install -r requirements.txt

# Setup environment variables
echo "Setting up environment variables..."
sudo -u stockalert cp .env.example .env
echo "Please edit /home/stockalert/app/.env with your production values"

# Setup PostgreSQL database
echo "Setting up PostgreSQL database..."
sudo -u postgres createuser --createdb stockalert
sudo -u postgres createdb stockalert_db
sudo -u postgres psql -c "ALTER USER stockalert WITH PASSWORD 'your_password_here';"

# Run Django migrations
echo "Running Django migrations..."
cd /home/stockalert/app
sudo -u stockalert /home/stockalert/app/venv/bin/python manage.py migrate
sudo -u stockalert /home/stockalert/app/venv/bin/python manage.py collectstatic --noinput
sudo -u stockalert /home/stockalert/app/venv/bin/python manage.py loaddata seed_data.json

# Setup systemd services
echo "Setting up systemd services..."
sudo cp deployment/stockalert.service /etc/systemd/system/
sudo cp deployment/celery.service /etc/systemd/system/
sudo cp deployment/celerybeat.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable stockalert celery celerybeat
sudo systemctl start stockalert celery celerybeat

# Setup Nginx
echo "Setting up Nginx..."
sudo cp deployment/nginx.conf /etc/nginx/sites-available/stockalert
sudo ln -sf /etc/nginx/sites-available/stockalert /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Setup firewall
echo "Setting up firewall..."
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

echo "Deployment completed!"
echo ""
echo "Next steps:"
echo "1. Edit /home/stockalert/app/.env with your production values"
echo "2. Update the domain name in /etc/nginx/sites-available/stockalert"
echo "3. Set up SSL certificate with Let's Encrypt (optional)"
echo "4. Create a Django superuser: sudo -u stockalert /home/stockalert/app/venv/bin/python /home/stockalert/app/manage.py createsuperuser"
echo "5. Initialize stocks: sudo -u stockalert /home/stockalert/app/venv/bin/python /home/stockalert/app/manage.py init_stocks"
echo ""
echo "Your application should be accessible at http://your-server-ip/"
