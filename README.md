# Stock Price Alerting System

A Django-based backend system that monitors real-time stock prices and sends alerts to users when certain conditions are met using free APIs and tools.

## Features

- **Real-time Stock Monitoring**: Fetches stock prices for 10 predefined companies using free API
- **Smart Alert System**: 
  - Threshold alerts (price above/below a value)
  - Duration alerts (price condition maintained for specified time)
- **Email Notifications**: Gmail SMTP integration for alert notifications
- **REST API**: CRUD operations with JWT authentication
- **Background Tasks**: Automated price fetching and alert evaluation

## Tech Stack

- **Backend**: Django 4.2.7
- **Database**: PostgreSQL 
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Task Scheduling**: Celery + Redis
- **API Source**: Twelve Data
- **Email**: Gmail SMTP
- **Deployment**: AWS EC2 + Vercel
- **Containerization**: Docker

## Project Structure

```
Stock-Price-Alerting/
├── 🐳 Docker Configuration
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── docker-entrypoint.sh
│   └── deploy-aws.sh
├── 🚀 Django Backend
│   ├── stock_alerting/        # Main Django project
│   ├── authentication/       # User management
│   ├── stocks/               # Stock data & services
│   ├── alerts/               # Alert system
│   └── manage.py
├── ⚛️ React Frontend
│   └── frontend/             # React app (deploy to Vercel)
└── 📚 Documentation
    ├── README.md

```

## Quick Start

🚀 **Fastest way to run the project:**

```cmd
# Navigate to project directory
cd e:\Stock-Price-Alerting

# Start development environment with Docker
.\docker-manage.bat dev
```

**Access the application:**
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin (admin/admin123)
- **API Documentation**: 
  - Swagger UI: http://localhost:8000/api/docs/
  - ReDoc: http://localhost:8000/api/redoc/


## Prerequisites

**For Docker Development (Recommended):**
- Docker Desktop installed and running
- Git (for cloning)

**For Manual Setup:**
- Python 3.8+
- Redis server
- PostgreSQL (or use SQLite for development)

### Docker Setup (Recommended)

Simple Docker commands for easy deployment:

1. **Create your environment file**
```bash
cp .env.example .env
# Edit .env with your configuration
```

2. **Start the application (production)**
```bash
docker-compose up -d
```

3. **Start with logs visible**
```bash
docker-compose up
```

4. **Stop the application**
```bash
docker-compose down
```

5. **Rebuild after code changes**
```bash
docker-compose up --build
```

The application will be available at:
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs/

### Docker Services
- **backend**: Django API server (port 8000)
- **celery**: Background task worker  
- **celery-beat**: Task scheduler
- **redis**: Message broker and cache

### Local Development Installation

For development without Docker:

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
# Or use Docker
docker run -d -p 6379:6379 redis:alpine
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

