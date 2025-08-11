# 📊 Stock Price Alerting System - Complete Project Walkthrough

## 🎯 **What Is This Project?**

Think of this as your **personal stock market assistant** that:
- 📈 **Watches stock prices** 24/7 for companies like Apple, Tesla, Google
- 🚨 **Alerts you instantly** when prices hit your target levels  
- 📧 **Sends email notifications** so you never miss opportunities
- 🌐 **Provides a beautiful web interface** to manage everything
- 📊 **Tracks price history** and shows trends

---

## 🏗️ **High-Level Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   🌐 FRONTEND   │◄──►│   🖥️ BACKEND    │◄──►│  📊 STOCK API   │
│   (React App)   │    │  (Django API)   │    │  (TwelveData)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       
         │              ┌─────────────────┐              
         │              │  🗄️ DATABASE   │              
         └──────────────┤  (PostgreSQL)   │              
                        └─────────────────┘              

┌─────────────────┐    ┌─────────────────┐
│  ⚡ BACKGROUND  │    │   📧 EMAIL      │
│   TASKS         │    │   NOTIFICATIONS │
│  (Celery+Redis) │    │   (Gmail SMTP)  │
└─────────────────┘    └─────────────────┘
```

---

## 📂 **Project Structure Explained**

### **🖥️ Backend Components:**
```
stocks/              # 📊 Stock data management
├── models.py        # Database tables (Stock, StockPrice, APIRequestLog)
├── services.py      # External API integration (TwelveData)
├── tasks.py         # Background jobs (price fetching, alerts)
├── views.py         # REST API endpoints
└── serializers.py   # Data transformation for API

alerts/              # 🚨 Alert system
├── models.py        # Alert & TriggeredAlert tables
├── views.py         # Alert management API
├── tasks.py         # Alert evaluation logic
└── serializers.py   # Alert data formatting

authentication/      # 🔐 User management
├── models.py        # User profiles
├── views.py         # Login/register endpoints
└── serializers.py   # User data handling

stock_alerting/      # ⚙️ Main project settings
├── settings.py      # Django configuration
├── urls.py          # API routing
├── celery.py        # Background task scheduling
└── wsgi.py          # Production server
```

### **🌐 Frontend Components:**
```
frontend/
├── src/
│   ├── pages/           # Main application screens
│   │   ├── Dashboard.js     # Overview & statistics
│   │   ├── StockList.js     # Browse available stocks
│   │   ├── AlertList.js     # Manage your alerts
│   │   └── CreateAlert.js   # Set up new alerts
│   ├── services/        # API communication
│   │   └── api.js           # HTTP requests to backend
│   ├── components/      # Reusable UI elements
│   └── contexts/        # Global state management
└── package.json         # Dependencies & scripts
```

---

## 🎭 **How The System Works - User Journey**

Let me walk you through what happens when someone uses this system:

### **👤 Step 1: User Registration**
```javascript
// Frontend: User fills registration form
POST /api/auth/register/
{
  "username": "john_trader",
  "email": "john@example.com", 
  "password": "securepass123"
}

// Backend: Creates user account in database
// Returns: JWT tokens for authentication
```

### **🔐 Step 2: Login & Authentication**
```javascript
// Frontend: Login form
POST /api/auth/login/
{
  "username": "john_trader",
  "password": "securepass123"
}

// Backend: Validates credentials
// Returns: JWT access & refresh tokens
```

### **📊 Step 3: Stock Data Display**
```javascript
// Frontend: Dashboard loads
GET /api/stocks/

// Backend: Returns monitored stocks
[
  {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "current_price": "227.25",
    "exchange": "NASDAQ"
  }
]
```

### **🚨 Step 4: Creating Alerts**
```javascript
// Frontend: User creates alert
POST /api/alerts/
{
  "stock_symbol": "AAPL",
  "alert_type": "threshold", 
  "condition": "above",
  "threshold_price": 230.00
}

// Backend: Saves alert to database
// Background: Alert evaluation starts
```

### **⚡ Step 5: Background Processing**
```python
# Celery task runs every 30 minutes
@shared_task
def fetch_all_stock_prices():
    # 1. Call TwelveData API for each stock
    # 2. Save price data to database  
    # 3. Update current_price field
    # 4. Trigger alert evaluation

@shared_task  
def evaluate_price_alerts():
    # 1. Check all active alerts
    # 2. Compare current prices to thresholds
    # 3. Send email notifications for triggered alerts
    # 4. Deactivate one-time alerts
```

---

## 🔧 **Technical Deep Dive**

### **📊 Database Schema**
```sql
-- Core stock data
Stock: id, symbol, name, exchange, current_price, is_active

-- Historical prices (OHLCV data)  
StockPrice: id, stock_id, price, open_price, high_price, 
           low_price, close_price, volume, timestamp

-- User alerts
Alert: id, user_id, stock_id, alert_type, condition,
       threshold_price, duration_minutes, is_active

-- Triggered notifications
TriggeredAlert: id, alert_id, trigger_price, triggered_at,
                email_sent, email_sent_at
```

### **🌐 API Endpoints**
```http
# Authentication
POST /api/auth/register/     # Sign up
POST /api/auth/login/        # Sign in
GET  /api/auth/profile/      # User info

# Stock Data  
GET  /api/stocks/                    # List stocks
GET  /api/stocks/{id}/price_history/ # Price charts
POST /api/stocks/refresh_prices/    # Manual refresh

# Alert Management
GET  /api/alerts/            # User's alerts
POST /api/alerts/            # Create alert  
DELETE /api/alerts/{id}/     # Remove alert
GET /api/alerts/triggered/   # Notification history
```

### **⚙️ Background Tasks (Celery)**
```python
# Schedule configuration
CELERY_BEAT_SCHEDULE = {
    'fetch-stock-prices': {
        'task': 'stocks.tasks.fetch_all_stock_prices',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'evaluate-alerts': {
        'task': 'stocks.tasks.evaluate_price_alerts', 
        'schedule': crontab(minute='*/5'),   # Every 5 minutes
    }
}
```

---

## 🎨 **Frontend User Interface**

The React frontend provides these main screens:

### **🏠 Dashboard**
- Overview statistics (total alerts, monitored stocks)
- Recent triggered alerts
- Quick actions (create alert, view stocks)
- Stock price widgets

### **📈 Stock List** 
- Grid view of all monitored stocks
- Current prices with change indicators
- Click to view price history charts
- Price trend arrows (📈📉➡️)

### **🚨 Alert Management**
- Active alerts with edit/delete options
- Triggered alert history
- Create new alert form with validation
- Alert type selection (threshold/duration)

### **➕ Create Alert**
- Stock selection dropdown
- Alert type radio buttons
- Price threshold input
- Duration settings (for duration alerts)
- Form validation and error handling

---

## 🔐 **Security & Authentication**

### **JWT Token Flow**
```javascript
// Login stores tokens
localStorage.setItem('access_token', response.access);
localStorage.setItem('refresh_token', response.refresh);

// API requests include auth header
headers: { Authorization: `Bearer ${access_token}` }

// Automatic token refresh on 401 errors
if (error.status === 401) {
  // Try to refresh token
  // Retry original request
  // Redirect to login if refresh fails
}
```

### **Data Protection**
- User-specific data isolation
- Input validation and sanitization  
- Rate limiting on API endpoints
- Secure password hashing
- HTTPS in production

---

## 📧 **Email Notification System**

```python
# Gmail SMTP configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-gmail@gmail.com'
EMAIL_HOST_PASSWORD = 'app-specific-password'

# Alert email template
def send_alert_email(user, alert, current_price):
    subject = f"🚨 Stock Alert: {alert.stock.symbol}"
    message = f"""
    Your alert for {alert.stock.name} has been triggered!
    
    Current Price: ${current_price}
    Alert Condition: {alert.condition} ${alert.threshold_price}
    """
    send_mail(subject, message, from_email, [user.email])
```

---

## ⚡ **Performance Optimizations**

### **API Rate Limiting**
```python
# TwelveData free tier: 8 calls/minute, 800/day
# Our usage: ~48 calls/day (6% utilization)

def fetch_quote(self, symbol):
    # 10-second delays between API calls
    # Error handling for rate limit responses
    # Comprehensive logging for monitoring
```

### **Database Efficiency**
```python
# Optimized queries with select_related
alerts = Alert.objects.filter(
    is_active=True
).select_related('stock', 'user')

# Proper indexing on frequently queried fields
# Cleanup tasks for old data (>30 days)
```

### **Frontend Performance**
```javascript
// Lazy loading of components
const Dashboard = React.lazy(() => import('./pages/Dashboard'));

// Efficient API response handling
const data = response.data.results || response.data.data || response.data;

// Toast notifications for user feedback
toast.success('Alert created successfully!');
```

---

This system elegantly combines real-time data processing, intelligent alerting, and a modern web interface to create a professional-grade stock monitoring solution! 

Would you like me to dive deeper into any specific component or walk through the deployment process? 🚀
