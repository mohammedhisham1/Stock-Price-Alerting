# 🚀 Complete Deployment Guide

**Architecture Overview:**
- 🖥️ **Backend**: Django REST API on AWS EC2 (Ubuntu Linux)
- 🌐 **Frontend**: React app on Vercel  
- 🗄️ **Database**: PostgreSQL on AWS RDS
- 🔄 **Cache/Queue**: Redis on EC2

## 📋 Deployment Checklist

### ✅ Step 1: Set Up AWS RDS Database

1. **Create RDS PostgreSQL Instance:**
   - Engine: PostgreSQL 15+
   - Instance class: db.t3.micro (free tier) or db.t3.small
   - Storage: 20GB GP3
   - **Important**: Note down:
     - Database name: `stockalertingdb`
     - Username: (your choice)
     - Password: (secure password)
     - Endpoint: `your-db.region.rds.amazonaws.com`

2. **Configure Security Groups:**
   - Allow inbound connection on port 5432 from EC2 security group
   - Source: EC2 security group ID

### ✅ Step 2: Deploy Backend on EC2 (Ubuntu)

1. **Launch EC2 Instance** (see EC2_DEPLOYMENT.md for details)
   - Use Ubuntu Server 22.04 LTS or 20.04 LTS
   - Instance type: t3.medium or larger
   - User: `ubuntu` (not `ec2-user`)

2. **Clone and Setup:**
   ```bash
   # Connect to Ubuntu instance
   ssh -i your-key.pem ubuntu@your-ec2-public-ip
   
   # Clone and setup
   git clone https://github.com/yourusername/Stock-Price-Alerting.git
   cd Stock-Price-Alerting
   chmod +x ec2-setup.sh
   ./ec2-setup.sh
   ```

3. **Configure Environment Variables:**
   ```bash
   # Edit environment file (note: /home/ubuntu/ for Ubuntu)
   nano /home/ubuntu/Stock-Price-Alerting/.env
   ```
   
   **Required Configuration:**
   ```env
   # Django Settings
   SECRET_KEY=your-super-secret-key-256-bit-random
   DEBUG=False
   ALLOWED_HOSTS=your-ec2-ip,your-domain.com
   
   # RDS Database
   DB_NAME=stockalertingdb
   DB_USER=your-rds-username
   DB_PASSWORD=your-rds-password
   DB_HOST=your-db.region.rds.amazonaws.com
   DB_PORT=5432
   
   # Redis (local on EC2)
   REDIS_URL=redis://localhost:6379/0
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   
   # CORS for Vercel Frontend
   CORS_ALLOWED_ORIGINS=https://your-app.vercel.app
   
   # External APIs
   TWELVE_DATA_API_KEY=your-twelve-data-key
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

4. **Initialize Database:**
   ```bash
   # Navigate to project directory and activate virtual environment
   cd /home/ubuntu/Stock-Price-Alerting
   source venv/bin/activate
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic --noinput
   python manage.py loaddata seed_data_fixed.json
   ```

5. **Start Services:**
   ```bash
   # Update supervisor configuration and start services
   sudo supervisorctl reread
   sudo supervisorctl update
   sudo supervisorctl start stockalerting:*

   # Start and enable Nginx
   sudo systemctl enable nginx
   sudo systemctl start nginx
   ```

### ✅ Step 3: Deploy Frontend on Vercel

1. **Fork/Clone Repository on GitHub**
2. **Connect to Vercel:**
   - Go to vercel.com
   - Import your repository
   - Select `frontend` folder as root directory

3. **Configure Environment Variables in Vercel:**
   ```
   REACT_APP_API_URL = https://your-ec2-domain.com/api
   ```
   (or with IP: `http://your-ec2-ip:8000/api`)

4. **Deploy:**
   - Vercel will automatically build and deploy
   - Note your Vercel app URL: `https://your-app.vercel.app`

### ✅ Step 4: Update Backend CORS

1. **SSH into EC2:**
   ```bash
   ssh -i your-key.pem ec2-user@your-ec2-ip
   ```

2. **Update CORS settings:**
   ```bash
   cd Stock-Price-Alerting
   nano .env
   ```
   
   Update:
   ```env
   CORS_ALLOWED_ORIGINS=https://your-actual-vercel-app.vercel.app
   ```

3. **Restart services:**
   ```bash
   ./manage-ec2.sh restart
   ```

## 🔗 Final URLs

After successful deployment:

- 🌐 **Frontend**: `https://your-app.vercel.app`
- 🖥️ **Backend API**: `http://your-ec2-ip:8000/api/`
- 📚 **API Documentation**: `http://your-ec2-ip:8000/api/docs/`
- ⚙️ **Admin Panel**: `http://your-ec2-ip:8000/admin/`
- ❤️ **Health Check**: `http://your-ec2-ip:8000/api/health/`

## 🛠️ Management Commands

**On EC2:**
```bash
# Check status
./manage-ec2.sh status

# Restart services  
./manage-ec2.sh restart

# View logs
./manage-ec2.sh logs

# Health check
./manage-ec2.sh health
```

**On Vercel:**
- Deployments happen automatically on git push
- View logs in Vercel dashboard

## 🔒 Security Recommendations

1. **Use HTTPS:**
   - Set up SSL certificate on EC2 with Let's Encrypt
   - Use domain name instead of IP

2. **Environment Variables:**
   - Never commit `.env` files
   - Use strong SECRET_KEY (256-bit random)
   - Use App Passwords for Gmail

3. **Database:**
   - Keep RDS in private subnet
   - Regular backups enabled
   - Strong database password

4. **EC2 Security:**
   - Keep instance updated
   - Use IAM roles instead of access keys
   - Restrict security groups to minimum required

## 🚨 Troubleshooting

### Frontend can't connect to backend:
- Check CORS settings in backend `.env`
- Verify EC2 security groups allow port 8000
- Ensure API URL in Vercel env vars is correct

### Database connection failed:
- Verify RDS security group allows EC2 connections
- Check database credentials in `.env`
- Test connection: `python manage.py dbshell`

### Celery tasks not running:
- Check Redis status: `redis-cli ping`
- Check Celery status: `sudo supervisorctl status`
- View Celery logs: `sudo supervisorctl tail -f stockalerting-celery`

Need help? Check the individual deployment guides in `EC2_DEPLOYMENT.md` for detailed instructions!
