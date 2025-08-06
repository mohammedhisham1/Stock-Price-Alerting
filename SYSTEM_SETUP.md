# 🚀 Complete System Setup Guide

## Quick Start (Recommended)

### For Windows Users:
```bash
# Double-click or run in command prompt
start_development.bat
```

### For Linux/Mac Users:
```bash
# Make executable and run
chmod +x start_development.sh
./start_development.sh
```

The startup scripts will automatically:
- ✅ Check prerequisites (Python, Node.js, npm)
- ✅ Install dependencies (pip + npm)
- ✅ Run database migrations
- ✅ Load initial stock data
- ✅ Start Django backend (port 8000)
- ✅ Start Celery workers
- ✅ Start React frontend (port 3000)

## Manual Setup

### 1. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate
python manage.py loaddata seed_data.json

# Create environment file
cp .env.example .env
# Edit .env with your API keys and settings

# Start Django server
python manage.py runserver 8000

# In separate terminals:
# Start Celery worker
celery -A stock_alerting worker --loglevel=info

# Start Celery beat scheduler
celery -A stock_alerting beat --loglevel=info
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## Access Points

Once running, you can access:

- **Frontend Interface:** http://localhost:3000
- **Django API:** http://localhost:8000/api
- **Django Admin:** http://localhost:8000/admin

## Testing the System

### 1. Create User Account
- Go to http://localhost:3000
- Click "Register" and create an account
- Login with your credentials

### 2. Explore the Dashboard
- View system statistics
- See available stocks
- Check alert overview

### 3. Create Stock Alerts
- Click "Create New Alert"
- Select a stock (e.g., AAPL)
- Set threshold alert: "Above $150"
- Or duration alert: "Above $150 for 30 minutes"
- Activate the alert

### 4. Test API Endpoints

**Authentication:**
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123","password2":"testpass123","first_name":"Test","last_name":"User"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

**Stock Data:**
```bash
# Get all stocks
curl -X GET http://localhost:8000/api/stocks/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get stock prices
curl -X GET http://localhost:8000/api/stocks/1/prices/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Alerts:**
```bash
# Create alert
curl -X POST http://localhost:8000/api/alerts/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"stock":1,"alert_type":"threshold","condition":"above","target_price":"150.00","is_active":true}'

# Get alerts
curl -X GET http://localhost:8000/api/alerts/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## System Features to Test

### ✅ Frontend Features
- [x] **Authentication:** Register, login, logout
- [x] **Dashboard:** Overview stats and metrics
- [x] **Stock List:** View available stocks and price history
- [x] **Alert Management:** Create, edit, delete, activate/deactivate alerts
- [x] **Responsive Design:** Works on desktop and mobile

### ✅ Backend Features
- [x] **REST API:** All CRUD operations
- [x] **JWT Authentication:** Secure token-based auth
- [x] **Stock Data Fetching:** Real-time price updates
- [x] **Alert Evaluation:** Threshold and duration logic
- [x] **Email Notifications:** Gmail SMTP integration
- [x] **Background Tasks:** Celery workers and scheduling

### ✅ System Integration
- [x] **API Communication:** Frontend ↔ Backend
- [x] **Real-time Updates:** Automatic data refresh
- [x] **Error Handling:** Graceful error management
- [x] **Authentication Flow:** Token refresh and validation

## Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Kill processes on ports 3000 and 8000
# Windows:
netstat -ano | findstr :3000
taskkill /F /PID <PID>

# Linux/Mac:
lsof -ti:3000 | xargs kill
lsof -ti:8000 | xargs kill
```

**Database Issues:**
```bash
# Reset database
python manage.py flush
python manage.py migrate
python manage.py loaddata seed_data.json
```

**Frontend Build Issues:**
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**API Connection Issues:**
- Verify Django server is running on port 8000
- Check CORS settings in Django settings
- Ensure proxy configuration in React package.json

### Configuration

**Environment Variables:**
```env
# Backend (.env)
TWELVE_DATA_API_KEY=your_twelve_data_api_key
EMAIL_HOST_USER=your_gmail_address
EMAIL_HOST_PASSWORD=your_gmail_app_password
SECRET_KEY=your_django_secret_key

# Frontend (.env)
REACT_APP_API_URL=http://localhost:8000/api
```

## Next Steps

1. **Production Deployment:** Use the deployment scripts in `/deployment/`
2. **API Key Setup:** Get free API key from Twelve Data
3. **Email Configuration:** Setup Gmail app password for notifications
4. **Monitoring:** Set up logging and monitoring for production

## Support

If you encounter any issues:
1. Check the console logs (browser dev tools + terminal)
2. Verify all services are running
3. Check network connectivity between frontend and backend
4. Review Django logs for API errors

---

🎉 **Enjoy your complete Stock Price Alerting System!**

The system is now ready for development and testing. The frontend provides an intuitive interface to interact with all the backend functionality, making it easy to manage your stock alerts and monitor price changes.
