# Stock Price Alerting System

A Django-based backend system that monitors real-time stock prices and sends alerts to users when certain conditions are met using free APIs and tools.

## Features

- **Real-time Stock Monitoring**: Fetches stock prices for 10 predefined companies using free APIs
- **Smart Alert System**: 
  - Threshold alerts (price above/below a value)
  - Duration alerts (price condition maintained for specified time)
- **Email Notifications**: Gmail SMTP integration for alert notifications
- **REST API**: Full CRUD operations with JWT authentication
- **Background Tasks**: Automated price fetching and alert evaluation
- **AWS Deployment Ready**: Configured for AWS Free Tier deployment

## Tech Stack

- **Backend**: Django 4.2.7
- **Database**: PostgreSQL (with SQLite fallback)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Task Scheduling**: Celery + Redis
- **API Source**: Twelve Data (free tier)
- **Email**: Gmail SMTP
- **Deployment**: AWS EC2

## Quick Start

🚀 **Fastest way to run the project:**

```cmd
# Navigate to project directory
cd e:\Stock-Price-Alerting

# Start development environment with Docker
.\docker-manage.bat dev
```

**Access the application:**
- Frontend: http://localhost:3000 (in development)
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin (admin/admin123)
- **API Documentation**: 
  - Swagger UI: http://localhost:8000/api/docs/
  - ReDoc: http://localhost:8000/api/redoc/

📖 **For detailed instructions, see [HOW_TO_RUN.md](HOW_TO_RUN.md)**

## Prerequisites

- Docker Desktop installed and running
- Git (optional, for cloning)
- Redis server
- PostgreSQL (optional, SQLite works for development)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
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
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
TWELVE_DATA_API_KEY=your-twelve-data-api-key
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
REDIS_URL=redis://localhost:6379/0
```

5. **Database Setup**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata seed_data.json
```

6. **Start Redis (required for Celery)**
```bash
# Windows (if Redis is installed)
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

## AWS Deployment

### EC2 Deployment Steps

1. **Launch EC2 Instance**
   - Ubuntu 20.04 LTS
   - t2.micro (Free Tier)
   - Security group: HTTP (80), HTTPS (443), SSH (22)

2. **Server Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib redis-server -y

# Create application user
sudo adduser stockalert
sudo usermod -aG sudo stockalert
```

3. **Application Deployment**
```bash
# Clone repository
git clone <your-repo-url> /home/stockalert/app
cd /home/stockalert/app

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with production values

# Setup database
python manage.py migrate
python manage.py collectstatic --noinput
```

4. **Configure Services**

Create systemd service files for:
- Django application (gunicorn)
- Celery worker
- Celery beat

5. **Configure Nginx**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /home/stockalert/app/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| SECRET_KEY | Django secret key | Yes |
| DEBUG | Debug mode (False for production) | Yes |
| DATABASE_URL | Database connection string | Yes |
| TWELVE_DATA_API_KEY | Stock API key | Yes |
| EMAIL_HOST_USER | Gmail address for notifications | Yes |
| EMAIL_HOST_PASSWORD | Gmail app password | Yes |
| REDIS_URL | Redis connection string | Yes |
| ALLOWED_HOSTS | Comma-separated allowed hosts | Production |

## Testing

Run the test suite:
```bash
python manage.py test
```

Run with coverage:
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## API Rate Limits

- **Twelve Data Free Tier**: 800 requests/day
- **Stock Price Fetching**: Optimized to stay within limits
- **Monitoring**: 10 stocks × 288 requests/day = 2,880 requests (requires paid plan)

For production, consider upgrading to Twelve Data paid plan or implementing request batching.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check the troubleshooting section below

## Troubleshooting

### Common Issues

1. **Celery not starting**
   - Ensure Redis is running
   - Check Redis connection string

2. **Email notifications not working**
   - Verify Gmail app password
   - Check 2FA is enabled on Gmail account

3. **Stock data not updating**
   - Verify API key is valid
   - Check API rate limits

4. **Database connection errors**
   - Verify DATABASE_URL format
   - Ensure PostgreSQL is running (if using PostgreSQL)

### Development Tips

- Use SQLite for local development
- Monitor Celery logs for task execution
- Test email notifications with console backend first
- Use Django admin for data inspection

## Video Walkthrough

[Link to 3-5 minute video demonstration will be added here]

The video covers:
- Main features demonstration
- Alert logic explanation
- Background task system
- Deployment overview
