# 🎭 **Complete System Flow - Step by Step**

## **📱 User Journey: Creating a Stock Alert**

### **Step 1: User Logs In**
```
1. User visits React frontend (https://your-app.vercel.app)
2. Enters username/password on login form
3. Frontend sends POST to /api/auth/login/
4. Backend validates credentials, returns JWT tokens
5. Frontend stores tokens in localStorage
6. User is redirected to Dashboard
```

### **Step 2: User Views Stock Data**
```
1. Dashboard loads, calls GET /api/stocks/
2. Backend returns list of monitored stocks:
   [
     {
       "symbol": "AAPL",
       "name": "Apple Inc.", 
       "current_price": "227.25",
       "exchange": "NASDAQ"
     },
     // ... more stocks
   ]
3. Frontend displays stock cards with current prices
```

### **Step 3: User Creates Alert**
```
1. User clicks "Create New Alert"
2. Navigates to CreateAlert.js page
3. Selects stock: "AAPL"
4. Sets condition: "above $230"
5. Clicks Submit
6. Frontend sends POST /api/alerts/:
   {
     "stock_symbol": "AAPL",
     "alert_type": "threshold", 
     "condition": "above",
     "threshold_price": 230.00
   }
7. Backend creates Alert record in database
8. User sees success message
```

## **⚡ Background Processing Flow**

### **Every 30 Minutes - Price Fetching**
```
1. Celery scheduler wakes up fetch_all_stock_prices task
2. Task loops through all active stocks:
   FOR each stock in ["AAPL", "TSLA", "GOOGL", ...]:
     a. Call TwelveData API: https://api.twelvedata.com/quote?symbol=AAPL
     b. Parse response: {"close": "227.25", "open": "228.00", ...}
     c. Save StockPrice record to database
     d. Update Stock.current_price field
     e. Wait 10 seconds (rate limiting)
3. Log results: "✅ Updated AAPL: $227.25"
```

### **Every 5 Minutes - Alert Evaluation**
```
1. Celery runs evaluate_price_alerts task
2. Get all active alerts from database
3. FOR each alert:
   a. Get current stock price
   b. Check condition:
      IF alert.condition == "above" AND current_price >= alert.threshold_price:
        - Create TriggeredAlert record
        - Send email notification
        - Deactivate alert (one-time trigger)
        - Log: "🔔 Triggered alert for AAPL: $232.50"
4. Return summary: "Evaluated 15 alerts, triggered 2"
```

## **📧 Email Notification Process**
```
1. Alert triggers (price condition met)
2. Django calls send_mail() function:
   - TO: user.email
   - SUBJECT: "🚨 Stock Alert: AAPL"
   - BODY: "Apple Inc. is now $232.50 (above $230.00)"
   - SMTP: Gmail servers
3. Email delivered to user's inbox
4. TriggeredAlert.email_sent = True
```

## **🗄️ Database Relationships**
```
User (john_trader)
 │
 ├── Alert (AAPL above $230)
 │    └── TriggeredAlert (triggered at $232.50)
 │
 └── Alert (TSLA below $600)
      └── (not triggered yet)

Stock (AAPL)
 │
 ├── StockPrice ($227.25 at 2025-08-12 10:00)
 ├── StockPrice ($228.15 at 2025-08-12 10:30)
 └── StockPrice ($232.50 at 2025-08-12 11:00)  ← This triggered the alert
```

## **🔐 Security Flow**
```
Frontend Request:
┌─────────────────┐
│ GET /api/stocks │
│ Authorization:  │
│ Bearer eyJ0eXA.. │ ← JWT token from localStorage
└─────────────────┘
          │
          ▼
┌─────────────────┐
│ Django Backend  │
│ 1. Decode JWT   │ ← Verify token signature
│ 2. Extract user │ ← Get user_id from token
│ 3. Check perms  │ ← Ensure user can access data
│ 4. Return data  │ ← Only user's own alerts/data
└─────────────────┘
```

## **⚡ Performance Optimizations**

### **API Rate Limiting**
```python
# TwelveData Free Tier Limits:
# - 8 calls per minute
# - 800 calls per day

# Our Usage Pattern:
# - 10 stocks × 2 calls/hour × 24 hours = 480 calls/day
# - Well under the 800 daily limit
# - 10-second delays = 6 calls/minute (under 8/minute limit)
```

### **Database Queries**
```python
# Optimized with select_related to avoid N+1 queries
alerts = Alert.objects.filter(
    is_active=True
).select_related('stock', 'user')

# Instead of 100 separate database calls, this makes just 1
```

### **Frontend Performance**
```javascript
// Efficient API response handling for different formats
const data = response.data.results?.data || 
            response.data.data || 
            response.data.results || 
            response.data;

// Toast notifications for instant user feedback
toast.success('Alert created successfully!');
```

## **🚀 Deployment Architecture**

### **Production Setup:**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vercel CDN    │    │   AWS EC2       │    │   AWS RDS       │
│                 │    │                 │    │                 │
│ • React App     │◄──►│ • Django API    │◄──►│ • PostgreSQL    │
│ • Static Files  │    │ • Nginx         │    │ • Backups       │
│ • Global CDN    │    │ • Supervisor    │    │ • Monitoring    │
└─────────────────┘    │ • Redis/Celery  │    └─────────────────┘
                       └─────────────────┘              
                                │                       
                                ▼                       
                       ┌─────────────────┐              
                       │  TwelveData API │              
                       │ • Stock Prices  │              
                       │ • Rate Limits   │              
                       └─────────────────┘              
```

### **Local Development:**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ localhost:3000  │    │ localhost:8000  │    │   SQLite DB     │
│                 │    │                 │    │                 │
│ • React Dev     │◄──►│ • Django Dev    │◄──►│ • Local File    │
│ • Hot Reload    │    │ • Debug Mode    │    │ • No Setup      │
│ • Proxy API     │    │ • Auto Reload   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

This system elegantly handles everything from real-time data fetching to intelligent alerting, all wrapped in a modern, responsive web interface! 🎉
