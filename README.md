# 📊 Stock Price Alerting System

## 🎯 **Project Overview**

This system provides users with powerful stock monitoring capabilities without requiring paid APIs or tools. Built with Django REST Framework and React, it delivers real-time price tracking, intelligent alerts, and seamless notifications via email.



---

## 🏗️ **Architecture**

**Production Deployment:**
- 🖥️ **Backend**: Django REST API on AWS EC2 
- 🌐 **Frontend**: React SPA running locally
- 🗄️ **Database**: PostgreSQL on AWS RDS

## ✨ **Features**

### **📈 Real-time Stock Monitoring**
- Tracks 10 predefined companies using TwelveData API
- Market-aware fetching (only during trading hours)
- Historical price data with interactive charts

### **🚨 Smart Alert System** 
- **Threshold Alerts**: "Notify me if AAPL > $200"
- **Duration Alerts**: "Alert me if TSLA stays below $600 for 2 hours"
- **Intelligent Processing**: Background evaluation every 2 minutes
- **Auto-deactivation**: One-time alerts deactivated after triggering

### **📧 Email Notifications**
- Instant Gmail SMTP notifications
- Comprehensive alert details in emails
- Error tracking and notification status

### **🔐 Security & Authentication**
- JWT-based user registration and login
- Protected API endpoints
- User-specific alert management

### **⚡ Background Processing**
- Celery + Redis for scalable task processing
- Market-aware scheduling (9:30-16:00 ET, Mon-Fri)
- Rate limiting and error handling


## 🛠️ Tech Stack

**Backend:**
- Django 4.2.7 + Django REST Framework
- PostgreSQL database
- JWT authentication
- Celery + Redis for background tasks
- drf-spectacular for API documentation

---

## 🚀 **Quick Setup & Run Instructions**

### **Prerequisites**
- Python 3.8+ and Node.js 16+
- PostgreSQL and Redis
- Git and code editor

### **1. Clone Repository**
```bash
git clone https://github.com/mohammedhisham1/Stock-Price-Alerting.git
cd Stock-Price-Alerting
```

### **2. Backend Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys and database settings
```

### **3. Environment Variables (.env)**
```bash
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/stock_alerting
TWELVE_DATA_API_KEY=your-twelve-data-key
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
CELERY_BROKER_URL=redis://localhost:6379/0
```

### **4. Database Setup**
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data
python manage.py loaddata sample_data.json
```

### **5. Run the Application**
```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Celery worker
celery -A stock_alerting worker -l info

# Terminal 3: Celery beat scheduler
celery -A stock_alerting beat -l info
```

### **6. Frontend Setup (Optional - for development)**
```bash
cd frontend
npm install
npm start
```

### **7. Access the Application**
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/
- **Frontend**: http://localhost:3000 (if running locally)

---

## 📊 **Sample Seed Data**

The system comes with pre-configured sample data for immediate testing:

### **Monitored Stocks**
```json
[
  {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
  {"symbol": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ"},
  {"symbol": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ"},
  {"symbol": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ"},
  {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ"},
  {"symbol": "META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ"},
  {"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ"},
  {"symbol": "NFLX", "name": "Netflix Inc.", "exchange": "NASDAQ"},
  {"symbol": "UBER", "name": "Uber Technologies Inc.", "exchange": "NYSE"},
  {"symbol": "SPOT", "name": "Spotify Technology S.A.", "exchange": "NYSE"}
]
```

### **Sample Alert Examples**
```json
[
  {
    "alert_type": "threshold",
    "stock_symbol": "AAPL",
    "condition": "above",
    "threshold_price": 200.00,
    "description": "Notify when Apple hits $200"
  },
  {
    "alert_type": "duration", 
    "stock_symbol": "TSLA",
    "condition": "below",
    "threshold_price": 600.00,
    "duration_minutes": 120,
    "description": "Alert if Tesla stays below $600 for 2 hours"
  }
]
```

### **Test User Accounts**
```json
[
  {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }
]
```
**Manual EC2 setup:**
```bash
git clone https://github.com/yourusername/Stock-Price-Alerting.git
cd Stock-Price-Alerting
# Follow the AWS_DEPLOYMENT_GUIDE.md for detailed setup instructions
```

## 🔗 Live Access Points

After deployment, access your application at:

- 🌐 **Frontend**: `http://localhost:3000`
- 🖥️ **API**: `http://your-ec2-ip:8000/api/`  
- 📚 **API Docs**: `http://your-ec2-ip:8000/api/docs/`
- ⚙️ **Admin**: `http://your-ec2-ip:8000/admin/`
```

**Access the application:**
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin (admin/admin123)
- **API Documentation**: 
  - Swagger UI: http://localhost:8000/api/docs/
  - ReDoc: http://localhost:8000/api/redoc/



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
python manage.py loaddata sample_data.json
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
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

5. **Database Setup**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
python manage.py loaddata sample_data.json
```

6. **Start Redis (required for Celery)**
```bash
redis-server
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

---

## 📚 **Complete API Endpoint List**

### **🔐 Authentication Endpoints**
```http
POST   /api/auth/register/           # User registration
POST   /api/auth/login/              # User login  
GET    /api/auth/profile/            # Get user profile
PUT    /api/auth/profile/            # Update user profile
POST   /api/auth/token/refresh/      # Refresh JWT token
```

### **📈 Stock Data Endpoints**
```http
GET    /api/stocks/                  # List all monitored stocks
GET    /api/stocks/{id}/             # Get specific stock details
GET    /api/stocks/{id}/price_history/  # Get stock price history
GET    /api/stocks/current_prices/   # Get current prices for all stocks
POST   /api/stocks/refresh_prices/   # Manually refresh prices (admin)
```

### **🚨 Alert Management Endpoints**
```http
GET    /api/alerts/                  # List user's alerts
POST   /api/alerts/                  # Create new alert
GET    /api/alerts/{id}/             # Get specific alert
PUT    /api/alerts/{id}/             # Update alert
DELETE /api/alerts/{id}/             # Delete alert
GET    /api/alerts/statistics/       # Get user's alert statistics
```

### **📧 Notification History Endpoints**
```http
GET    /api/triggered-alerts/        # List triggered alerts
GET    /api/triggered-alerts/{id}/   # Get specific triggered alert
GET    /api/triggered-alerts/?days=7 # Filter by date range
```

### **📋 System Documentation**
```http
GET    /api/docs/                    # Swagger UI documentation
GET    /api/redoc/                   # ReDoc documentation  
GET    /api/schema/                  # OpenAPI schema
GET    /admin/                       # Django admin interface
```

### **API Response Format**
All API responses follow this consistent structure:
```json
{
  "success": true,
  "data": {...},          // Response data
  "count": 10,            // For list endpoints
  "next": "...",          // Pagination
  "previous": "...",      // Pagination
  "message": "..."        // Success/error message
}
```

### **Authentication Required**
All endpoints except registration and login require JWT authentication:
```http
Authorization: Bearer <your-jwt-token>
```

---

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
    "password": "securepassword123",
    "password2": "securepassword123"
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

#### Get All Stocks
```http
GET /api/stocks/
```
Returns list of all active stocks with metadata and latest price information.

#### Get Individual Stock
```http
GET /api/stocks/{stock_id}/
```
Returns detailed information for a specific stock.

#### Get Current Prices (All Stocks)
```http
GET /api/stocks/current_prices/
```
Returns current price snapshot for all active stocks - lightweight endpoint for dashboards.

#### Get Price History
```http
GET /api/stocks/{stock_id}/price_history/?hours=24
```
Returns historical price data for a specific stock. Optional `hours` parameter (default: 24).

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

The system runs optimized automated tasks:

- **Stock Price Fetching**: Every 30 minutes during market hours (9:30-16:00 ET, Mon-Fri) - optimized for API rate limits
- **Alert Evaluation**: Every 5 minutes to check for triggered conditions
- **Data Cleanup**: Daily cleanup of old price data (30+ days) and triggered alerts (7+ days)

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

## Management Commands

The system includes useful management commands for administration:

```bash
# Manual stock price fetch (bypasses market hours check)
python manage.py fetch_prices

# Load initial stock data
python manage.py loaddata sample_data.json

# Create admin user
python manage.py createsuperuser
```

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

