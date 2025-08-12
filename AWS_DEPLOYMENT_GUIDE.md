# AWS EC2 Deployment Guide

## Prerequisites
- AWS Account with EC2 access
- Key pair for SSH access
- Security group allowing HTTP (80), HTTPS (443), SSH (22)

## 1. Launch EC2 Instance
```bash
# Launch Ubuntu 22.04 LTS instance (t2.micro for free tier)
# Configure security group:
# - SSH (22): Your IP
# - HTTP (80): Anywhere
# - HTTPS (443): Anywhere
# - Custom (8000): Anywhere (for development)
```

## 2. Connect and Setup Server
```bash
# Connect to instance
ssh -i your-key.pem ubuntu@your-ec2-public-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx git -y

# Install Node.js for frontend
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y
```

## 3. Setup Database
```bash
# Configure PostgreSQL
sudo -u postgres psql
CREATE DATABASE stock_alerting;
CREATE USER stockuser WITH ENCRYPTED PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE stock_alerting TO stockuser;
ALTER USER stockuser CREATEDB;
\q
```

## 4. Deploy Backend
```bash
# Clone repository
git clone https://github.com/mohammedhisham1/Stock-Price-Alerting.git
cd Stock-Price-Alerting

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
sudo nano .env
```

### Environment Variables (.env)
```bash
DEBUG=False
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://stockuser:your-secure-password@localhost:5432/stock_alerting
ALLOWED_HOSTS=your-domain.com,your-ec2-public-ip,localhost
TWELVE_DATA_API_KEY=your-api-key
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 5. Deploy Application
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Test server
python manage.py runserver 0.0.0.0:8000
```

## 6. Setup Services
```bash
# Copy service files
sudo cp deployment/stock-alerting.service /etc/systemd/system/
sudo cp deployment/celery.service /etc/systemd/system/
sudo cp deployment/celerybeat.service /etc/systemd/system/

# Enable services
sudo systemctl enable stock-alerting celery celerybeat
sudo systemctl start stock-alerting celery celerybeat
```

## 7. Configure Nginx
```bash
# Copy nginx config
sudo cp deployment/nginx.conf /etc/nginx/sites-available/stock-alerting
sudo ln -s /etc/nginx/sites-available/stock-alerting /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test and restart nginx
sudo nginx -t
sudo systemctl restart nginx
```

## 8. Frontend Development (Local)
```bash
# Run frontend locally for development
cd frontend
npm install
npm start

# Frontend will be available at http://localhost:3000
# Configure API_BASE_URL to point to your EC2 backend
```

## Monitoring
```bash
# Check service status
sudo systemctl status stock-alerting
sudo systemctl status celery
sudo systemctl status celerybeat

# View logs
sudo journalctl -u stock-alerting -f
sudo journalctl -u celery -f
```

