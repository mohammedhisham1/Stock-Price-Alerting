# 📊 Stock Price Alerting System

A modern, scalable system for real-time stock monitoring and intelligent alerting.

## 🏗️ Architecture

**Production Deployment:**
- 🖥️ **Backend**: Django REST API on AWS EC2 
- 🌐 **Frontend**: React SPA on Vercel
- 🗄️ **Database**: PostgreSQL on AWS RDS
- 🔄 **Cache/Queue**: Redis on EC2 for background tasks

## ✨ Features

- 📈 **Real-time Stock Monitoring**: Tracks 10+ predefined companies using TwelveData API
- 🚨 **Smart Alert System**: 
  - Threshold alerts (price above/below target)
  - Duration alerts (condition maintained over time)
- 📧 **Email Notifications**: Instant Gmail alerts when conditions are met
- 🔐 **Secure REST API**: JWT authentication with comprehensive endpoints
- ⚡ **Background Processing**: Celery + Redis for automated price fetching
- 📱 **Responsive Frontend**: Modern React interface with real-time updates
- 📚 **API Documentation**: Auto-generated docs with drf-spectacular

## 🛠️ Tech Stack

**Backend:**
- Django 4.2.7 + Django REST Framework
- PostgreSQL database
- JWT authentication
- Celery + Redis for background tasks
- drf-spectacular for API documentation

**Frontend:**
- React with modern hooks
- Axios for API communication
- Bootstrap for responsive design
- Deployed on Vercel

**Infrastructure:**
- **Backend**: Ubuntu EC2 with Nginx + Supervisor
- **Database**: AWS RDS PostgreSQL  
- **Frontend**: Vercel deployment
- **Cache/Queue**: Redis on EC2

## 📁 Project Structure

```
Stock-Price-Alerting/
├── �️ Backend (Django REST API)
│   ├── stock_alerting/        # Main project settings
│   ├── authentication/       # User management & JWT
│   ├── stocks/               # Stock data & services
│   ├── alerts/               # Alert system & notifications
│   ├── requirements.txt      # Python dependencies
│   └── manage.py
├── 🌐 Frontend (React SPA)
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   ├── pages/           # Application pages
│   │   └── services/        # API services
│   ├── package.json
│   └── vercel.json          # Vercel deployment config
├── � Deployment
│   ├── ec2-setup.sh         # Automated EC2 setup
│   ├── manage-ec2.sh        # EC2 management script
│   ├── EC2_DEPLOYMENT.md    # Detailed EC2 guide
│   └── DEPLOYMENT_GUIDE.md  # Complete deployment guide
└── 📚 Documentation

## 🚀 Quick Deployment

**For production deployment (EC2 + Vercel + RDS):**

1. **📖 Read the Complete Guide**: See `DEPLOYMENT_GUIDE.md`
2. **🖥️ Deploy Backend on EC2**: Follow `EC2_DEPLOYMENT.md`
3. **🌐 Deploy Frontend on Vercel**: Use provided `vercel.json`

**One-command EC2 setup:**
```bash
git clone https://github.com/yourusername/Stock-Price-Alerting.git
cd Stock-Price-Alerting
chmod +x ec2-setup.sh && ./ec2-setup.sh
```

## 🔗 Live Access Points

After deployment, access your application at:

- 🌐 **Frontend**: `https://your-app.vercel.app`
- 🖥️ **API**: `http://your-ec2-ip:8000/api/`  
- 📚 **API Docs**: `http://your-ec2-ip:8000/api/docs/`
- ⚙️ **Admin**: `http://your-ec2-ip:8000/admin/`
- ❤️ **Health**: `http://your-ec2-ip:8000/api/health/`
```

**Access the application:**
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin (admin/admin123)
- **API Documentation**: 
  - Swagger UI: http://localhost:8000/api/docs/
  - ReDoc: http://localhost:8000/api/redoc/


## Prerequisites

**For Local Development:**
- Python 3.8+
- Redis server
- PostgreSQL (or use SQLite for development)
- Git (for cloning)

### Local Development Setup

Step-by-step development setup:

1. **Clone the repository**
```bash
git clone https://github.com/mohammedhisham1/Stock-Price-Alerting.git
cd Stock-Price-Alerting
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create environment file**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Database setup**
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py loaddata seed_data_fixed.json
```

6. **Start Redis (required for Celery)**
```bash
redis-server
```

7. **Start Celery Worker (new terminal)**
```bash
celery -A stock_alerting worker -l info
```

8. **Start Celery Beat (new terminal)**
```bash
celery -A stock_alerting beat -l info
```

9. **Start Django development server**
```bash
python manage.py runserver
```

The application will be available at:
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs/
- Admin Panel: http://localhost:8000/admin

### Production Deployment

For production deployment on AWS EC2, see [`EC2_DEPLOYMENT.md`](EC2_DEPLOYMENT.md) for complete setup instructions.

1. **Clone the repository**
```bash
git clone https://github.com/mohammedhisham1/Stock-Price-Alerting.git
cd Stock-Price-Alerting
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
Create a `.env` file in the root directory:
```env
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration (for AWS RDS)
DB_NAME=stockalertingdb
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=your-rds-endpoint.region.rds.amazonaws.com
DB_PORT=5432

# For local development, Django will use SQLite automatically
# if database connection fails

# External API
TWELVE_DATA_API_KEY=your-twelve-data-api-key

# Email Configuration
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# CORS Configuration (add your frontend URL)
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app
```

5. **Database Setup**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
python manage.py loaddata seed_data_fixed.json
```

6. **Start Redis (required for Celery)**
```bash
redis-server
# On Windows, you may need to install Redis from https://redis.io/download
# Or use Redis on Windows from Microsoft: https://github.com/microsoftarchive/redis/releases
```

7. **Start Celery Worker**
```bash
celery -A stock_alerting worker -l info
```

8. **Start Celery Beat (scheduler)**
```bash
celery -A stock_alerting beat -l info
```

9. **Run Development Server**
```bash
python manage.py runserver
```

## API Documentation

📚 **Interactive API Documentation Available:**

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/  
- **OpenAPI Schema**: http://localhost:8000/api/schema/


### Authentication

#### Register User
```http
POST /api/auth/register/
Content-Type: application/json

{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123"
}
```

#### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
    "username": "testuser",
    "password": "securepassword123"
}
```

Response:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Alerts Management

All alert endpoints require JWT authentication:
```http
Authorization: Bearer <access_token>
```

#### Create Alert
```http
POST /api/alerts/
Content-Type: application/json

{
    "stock_symbol": "AAPL",
    "alert_type": "threshold",
    "condition": "above",
    "threshold_price": 200.00,
    "duration_minutes": null
}
```

#### List User Alerts
```http
GET /api/alerts/
```

#### Delete Alert
```http
DELETE /api/alerts/{alert_id}/
```

#### Get Triggered Alerts
```http
GET /api/alerts/triggered/
```

### Stock Data

#### Get Current Stock Prices
```http
GET /api/stocks/
```

## Monitored Stocks

The system monitors these 10 stocks by default:
- AAPL (Apple Inc.)
- TSLA (Tesla Inc.)
- GOOGL (Alphabet Inc.)
- AMZN (Amazon.com Inc.)
- MSFT (Microsoft Corporation)
- META (Meta Platforms Inc.)
- NVDA (NVIDIA Corporation)
- NFLX (Netflix Inc.)
- UBER (Uber Technologies Inc.)
- SPOT (Spotify Technology S.A.)

## Alert Types

### Threshold Alert
Triggers when stock price crosses a specified threshold:
```json
{
    "alert_type": "threshold",
    "condition": "above",  // or "below"
    "threshold_price": 200.00
}
```

### Duration Alert
Triggers when stock price maintains a condition for specified duration:
```json
{
    "alert_type": "duration",
    "condition": "below",
    "threshold_price": 600.00,
    "duration_minutes": 120
}
```

## Background Tasks

The system runs automated tasks:

- **Stock Price Fetching**: Every 5 minutes during market hours
- **Alert Evaluation**: Every 2 minutes
- **Cleanup**: Daily cleanup of old triggered alerts

## Email Notifications

Configure Gmail SMTP in your `.env` file:

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password for this application
3. Use the App Password in `EMAIL_HOST_PASSWORD`

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| SECRET_KEY | Django secret key | Yes |
| DEBUG | Debug mode (False for production) | Yes |
| DB_NAME | Database name | Yes (Production) |
| DB_USER | Database username | Yes (Production) |
| DB_PASSWORD | Database password | Yes (Production) |
| DB_HOST | Database host (RDS endpoint) | Yes (Production) |
| DB_PORT | Database port | Yes (Production) |
| TWELVE_DATA_API_KEY | Stock API key | Yes |
| EMAIL_HOST_USER | Gmail address for notifications | Yes |
| EMAIL_HOST_PASSWORD | Gmail app password | Yes |
| REDIS_URL | Redis connection string | Yes |
| ALLOWED_HOSTS | Comma-separated allowed hosts | Production |
| CORS_ALLOWED_ORIGINS | Frontend URLs for CORS | Production |

## Testing

Run the test suite:
```bash
python manage.py test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.



## Troubleshooting

### Common Issues

1. **Celery not starting**
   - Ensure Redis is running
   - Check Redis connection string

2. **Email notifications not working**
   - Verify Gmail app password
   - Check 2FA is enabled on Gmail account

