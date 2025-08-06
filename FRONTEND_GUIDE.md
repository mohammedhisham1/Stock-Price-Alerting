# Stock Price Alerting System - Frontend

A modern React frontend for the Stock Price Alerting System that provides a clean, intuitive interface for managing stock alerts and monitoring price changes.

## 🚀 Quick Start

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Open http://localhost:3000 in your browser
```

## ✨ Features

### Authentication & Security
- 🔐 Secure user registration and login
- 🎫 JWT token-based authentication
- 🔄 Automatic token refresh
- 👤 User profile management

### Dashboard & Overview
- 📊 Real-time stats and metrics
- 🎯 Alert summary cards
- 🚨 Recent triggered alerts
- ⚡ Quick action buttons

### Stock Monitoring
- 📈 Interactive stock list
- 💰 Price history viewer
- 📊 Real-time price data
- 🔍 Stock search and filtering

### Alert Management
- ➕ Create threshold-based alerts
- ⏰ Set duration-based alerts
- ✅ Activate/deactivate alerts
- 🗑️ Delete unwanted alerts
- 📋 Alert preview and validation

## 🎨 User Interface

### Modern Design
- Clean, responsive layout
- Intuitive navigation
- Interactive components
- Visual feedback and animations

### User Experience
- Loading states and spinners
- Toast notifications
- Form validation
- Error handling

## 🔌 API Integration

The frontend seamlessly integrates with your Django REST API:

- **Authentication:** `/api/auth/` endpoints
- **Stocks:** `/api/stocks/` endpoints  
- **Alerts:** `/api/alerts/` endpoints
- **Automatic error handling** and retry logic
- **Real-time data** synchronization

## 📱 Responsive Design

Works perfectly on:
- 💻 Desktop computers
- 📱 Mobile devices
- 📟 Tablets
- 🖥️ Large screens

## 🛠️ Technology Stack

- **React 18:** Modern React with hooks
- **React Router:** Client-side routing
- **Axios:** HTTP client with interceptors
- **React Hot Toast:** Notification system
- **CSS3:** Modern styling and animations

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000/api
```

### Proxy Configuration
Development proxy is configured in `package.json`:

```json
{
  "proxy": "http://localhost:8000"
}
```

## 📋 Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run test suite
- `npm run eject` - Eject from Create React App

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Serve Static Files
The built files in the `build` directory can be served by:
- Nginx
- Apache
- Express.js
- Django (static files)

### Environment Setup
Update API URL for production in `.env`:

```env
REACT_APP_API_URL=https://your-api-domain.com/api
```

## 🔍 Testing the System

### Manual Testing Workflow

1. **Authentication Flow:**
   - Register a new account
   - Login with credentials
   - Verify JWT token handling

2. **Stock Monitoring:**
   - Browse available stocks
   - Click to view price history
   - Verify real-time data updates

3. **Alert Creation:**
   - Create threshold alerts
   - Create duration alerts
   - Test form validation

4. **Alert Management:**
   - Activate/deactivate alerts
   - Delete alerts
   - View triggered alerts

## 🐛 Troubleshooting

### Common Issues

**Cannot connect to API:**
- Verify Django backend is running
- Check CORS configuration
- Confirm API URL in environment

**Authentication errors:**
- Clear browser localStorage
- Check JWT secret key configuration
- Verify token expiration settings

**Missing data:**
- Run Django migrations
- Load initial stock data
- Check Celery tasks are running

## 🤝 Integration with Backend

This frontend is designed to work with the Django REST API:

- **Django:** Backend API server
- **Celery:** Background task processing
- **Redis:** Caching and message broker
- **PostgreSQL:** Database storage

Make sure your Django backend includes these CORS settings:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React development server
    "http://127.0.0.1:3000",
]
```

---

🎉 **Enjoy monitoring your stock alerts with a beautiful, modern interface!**
