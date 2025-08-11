# 🚀 EC2 Backend Deployment - Stock Price Alerting

**Deployment Architecture:**
- 🖥️ **Backend**: Django REST API on AWS EC2 (Ubuntu Linux)
- 🌐 **Frontend**: React app deployed on Vercel
- 🗄️ **Database**: PostgreSQL on AWS RDS
- 🔄 **Cache/Queue**: Redis on EC2 for Celery tasks

This guide will help you deploy the backend API on Ubuntu EC2 instance.

## Prerequisites

Before starting, ensure you have:
- ✅ AWS account with EC2, RDS access
- ✅ Vercel account for frontend deployment  
- ✅ Domain name (optional but recommended)
- ✅ TwelveData API key for stock data
- ✅ Gmail account with App Password for email alerts

## 🚀 EC2 Instance Setup

### 1. Launch EC2 Instance
- **Instance Type**: t3.medium or larger (minimum t3.small)
- **AMI**: Ubuntu Server 22.04 LTS (recommended) or Ubuntu Server 20.04 LTS
- **Storage**: 20GB GP3
- **Security Groups**:
  - SSH (22) - Your IP
  - HTTP (80) - Anywhere
  - HTTPS (443) - Anywhere
  - Custom TCP (8000) - Anywhere (for Django API)

### 2. Connect to EC2
```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ipide- Amazon Linux

This guide will help you deploy the Stock Price Alerting System directly on an Amazon Linux EC2 instance.

## 🚀 EC2 Instance Setup

### 1. Launch EC2 Instance
- **Instance Type**: t3.medium or larger (minimum t3.small)
- **AMI**: Amazon Linux 2023 (recommended) or Amazon Linux 2
- **Storage**: 20GB GP3
- **Security Groups**:
  - SSH (22) - Your IP
  - HTTP (80) - Anywhere
  - HTTPS (443) - Anywhere
  - Custom TCP (8000) - Anywhere (for Django)

### 2. Connect to EC2
```bash
ssh -i your-key.pem ec2-user@your-ec2-public-ip
```

## 📦 System Dependencies Installation

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Python 3 and Development Tools
```bash
# Install Python 3 and pip
sudo apt install -y python3 python3-pip python3-dev python3-venv

# Install development tools
sudo apt install -y build-essential gcc g++ make
```

### 3. Install System Dependencies
```bash
# Database client and libraries
sudo apt install -y postgresql-client libpq-dev

# Web server and process management
sudo apt install -y nginx supervisor

# Redis server
sudo apt install -y redis-server

# Git and utilities  
sudo apt install -y git curl wget htop tree
```

# Database client and libraries
sudo yum install -y postgresql15-devel postgresql15
# If PostgreSQL 15 not available, try:
# sudo yum install -y postgresql-devel postgresql

# Web server and process management
sudo yum install -y nginx supervisor

# Git and utilities
sudo yum install -y git curl wget

# Redis Server
sudo yum install -y redis
sudo systemctl enable redis
sudo systemctl start redis
```

### 4. Configure Redis
```bash
sudo nano /etc/redis/redis.conf
# Uncomment and set:
# bind 127.0.0.1
# maxmemory 256mb
# maxmemory-policy allkeys-lru

sudo systemctl restart redis
```

## 🔧 Application Deployment

### 1. Clone Repository
```bash
cd /home/ec2-user
git clone https://github.com/mohammedhisham1/Stock-Price-Alerting.git
cd Stock-Price-Alerting
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
pip install gunicorn
```

### 4. Environment Configuration
```bash
# Copy and edit environment file
cp .env.example .env
nano .env
```

**Edit `.env` with your EC2-specific settings:**
```env
# Django Configuration
SECRET_KEY=your-super-secret-key-change-this
DEBUG=False
ALLOWED_HOSTS=your-ec2-public-ip,your-domain.com,localhost

# Database Configuration (AWS RDS)
DB_NAME=your-database-name
DB_USER=your-database-user
DB_PASSWORD=your-database-password
DB_HOST=your-rds-endpoint.region.rds.amazonaws.com
DB_PORT=5432

# Redis Configuration (Local)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# External APIs
TWELVE_DATA_API_KEY=your-twelve-data-api-key

# Email Configuration
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Production Settings
LOAD_SEED_DATA=true
```

### 5. Database Setup
```bash
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py loaddata seed_data_fixed.json
```

## 🔄 Process Management with Supervisor

### 1. Create Supervisor Configuration
```bash
sudo nano /etc/supervisord.d/stockalerting.ini
```

**Add this configuration:**
```ini
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
```

### 2. Start Services
```bash
# Create log directory
sudo mkdir -p /var/log/supervisor

# Enable and start supervisord
sudo systemctl enable supervisord
sudo systemctl start supervisord

# Load new configuration
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start stockalerting:*
sudo supervisorctl status
```

## 🌐 Nginx Reverse Proxy Setup

### 1. Create Nginx Configuration
```bash
sudo nano /etc/nginx/conf.d/stockalerting.conf
```

**Add this configuration:**
```nginx
server {
    listen 80;
    server_name your-ec2-public-ip your-domain.com;

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
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 2. Enable and Start Nginx
```bash
# Test Nginx configuration
sudo nginx -t

# Enable and start Nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# Set proper permissions for static files
sudo chown -R ec2-user:ec2-user /home/ec2-user/Stock-Price-Alerting/
```

## 🔒 SSL Certificate (Optional but Recommended)

### Using Let's Encrypt (Certbot)
```bash
# Install EPEL repository first (for Amazon Linux 2)
sudo amazon-linux-extras install epel -y

# Install certbot
sudo yum install -y certbot python3-certbot-nginx

# For Amazon Linux 2023, use snapd instead:
# sudo yum install snapd
# sudo systemctl enable --now snapd.socket
# sudo snap install core; sudo snap refresh core
# sudo snap install --classic certbot

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
sudo systemctl restart nginx
```

## 📊 Monitoring and Logs

### View Application Logs
```bash
# Django logs
sudo tail -f /var/log/supervisor/stockalerting_django.log

# Celery worker logs
sudo tail -f /var/log/supervisor/stockalerting_celery.log

# Celery beat logs
sudo tail -f /var/log/supervisor/stockalerting_beat.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -u nginx -f
sudo journalctl -u supervisord -f
sudo journalctl -u redis -f
```

### Service Management
```bash
# Restart all services
sudo supervisorctl restart stockalerting:*

# Check service status
sudo supervisorctl status

# Restart specific service
sudo supervisorctl restart stockalerting_django
sudo supervisorctl restart stockalerting_celery
sudo supervisorctl restart stockalerting_beat
```

## 🔧 Useful Management Commands

### Application Updates
```bash
cd /home/ec2-user/Stock-Price-Alerting
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart stockalerting:*
```

### Database Management
```bash
source venv/bin/activate
python manage.py shell
python manage.py dbshell
python manage.py migrate
```

### Check System Resources
```bash
htop  # Install with: sudo yum install -y htop
df -h
free -h
sudo supervisorctl status
systemctl status redis
systemctl status nginx
```

## 🌍 Access Your Application

After setup, your application will be available at:
- **API**: `http://your-ec2-public-ip/api/`
- **Admin**: `http://your-ec2-public-ip/admin/`
- **API Docs**: `http://your-ec2-public-ip/api/docs/`
- **Health Check**: `http://your-ec2-public-ip/api/health/`

## 🛡️ Security Considerations

1. **Firewall Setup (Amazon Linux)**:
```bash
# Amazon Linux uses different firewall management
sudo yum install -y firewalld
sudo systemctl enable firewalld
sudo systemctl start firewalld

# Open required ports
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# Check status
sudo firewall-cmd --list-all
```

2. **SELinux Configuration (if enabled)**:
```bash
# Check SELinux status
sudo getenforce

# If enforcing, configure for web server
sudo setsebool -P httpd_can_network_connect 1
sudo setsebool -P httpd_can_network_relay 1
```

2. **Regular Updates**:
```bash
sudo apt update && sudo apt upgrade -y
```

3. **Backup Strategy**:
- Database backups
- Application code backups
- Environment file backups

4. **Environment Variables**:
- Never commit `.env` to version control
- Use strong SECRET_KEY
- Set DEBUG=False in production

## 🎯 Performance Optimization

1. **Gunicorn Workers**: Adjust based on CPU cores (2 * cores + 1)
2. **Redis Memory**: Configure appropriate memory limits
3. **Nginx Caching**: Enable for static files
4. **Database Connection Pooling**: Consider pgbouncer for PostgreSQL

Your Stock Price Alerting System is now running directly on EC2 without Docker! 🚀
