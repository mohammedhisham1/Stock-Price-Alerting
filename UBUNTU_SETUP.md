# 🐧 Ubuntu EC2 Quick Start Guide

## 🚀 One-Command Setup

For Ubuntu 22.04 LTS or 20.04 LTS EC2 instances:

```bash
# Connect to your Ubuntu EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-public-ip

# Clone and run automated setup
git clone https://github.com/yourusername/Stock-Price-Alerting.git
cd Stock-Price-Alerting
chmod +x ec2-setup.sh
./ec2-setup.sh
```

## 🔧 Key Differences from Amazon Linux

### **User and Paths:**
- **User**: `ubuntu` (not `ec2-user`)
- **Home**: `/home/ubuntu/` (not `/home/ec2-user/`)
- **SSH**: `ssh -i key.pem ubuntu@ip` (not `ec2-user@ip`)

### **Package Management:**
- **Ubuntu**: `apt update && apt install` 
- **Amazon Linux**: `yum update && yum install`

### **Services:**
- **Supervisor config**: `/etc/supervisor/conf.d/` (not `/etc/supervisord.d/`)
- **Nginx sites**: `/etc/nginx/sites-available/` and `/etc/nginx/sites-enabled/`
- **Firewall**: UFW (not firewalld)

### **Python:**
- **Ubuntu 22.04**: Python 3.10 by default
- **Ubuntu 20.04**: Python 3.8 by default
- No need for alternatives command like Amazon Linux

## 📋 Post-Setup Steps

After running the setup script:

1. **Configure Environment:**
   ```bash
   cd /home/ubuntu/Stock-Price-Alerting
   nano .env
   ```

2. **Initialize Database:**
   ```bash
   source venv/bin/activate
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic --noinput
   python manage.py loaddata seed_data_fixed.json
   ```

3. **Start All Services:**
   ```bash
   sudo supervisorctl reread
   sudo supervisorctl update  
   sudo supervisorctl start stockalerting:*
   sudo systemctl enable nginx
   sudo systemctl start nginx
   ```

4. **Check Status:**
   ```bash
   # Use the management script
   ./manage-ec2.sh status
   
   # Or check individually
   sudo supervisorctl status
   sudo systemctl status nginx
   sudo systemctl status redis
   ```

## 🔗 Access Your Application

- **API**: `http://your-ubuntu-ec2-ip:8000/api/`
- **API Docs**: `http://your-ubuntu-ec2-ip:8000/api/docs/`
- **Admin**: `http://your-ubuntu-ec2-ip:8000/admin/`
- **Health**: `http://your-ubuntu-ec2-ip:8000/api/health/`

## 🛠️ Management Commands

```bash
# All management via the script
./manage-ec2.sh start     # Start all services
./manage-ec2.sh stop      # Stop all services  
./manage-ec2.sh restart   # Restart all services
./manage-ec2.sh status    # Check service status
./manage-ec2.sh logs      # View recent logs
./manage-ec2.sh health    # Health check
```

## 🚨 Common Ubuntu-Specific Issues

### **Permission Issues:**
```bash
# Fix ownership if needed
sudo chown -R ubuntu:ubuntu /home/ubuntu/Stock-Price-Alerting
```

### **Firewall:**
```bash
# Check UFW status
sudo ufw status

# Allow ports if needed
sudo ufw allow 8000/tcp
sudo ufw allow 'Nginx Full'
```

### **Service Issues:**
```bash
# Check logs
sudo journalctl -u nginx
sudo journalctl -u supervisor
tail -f /var/log/supervisor/stockalerting_*.log
```

Your Ubuntu EC2 setup is ready! 🎉
