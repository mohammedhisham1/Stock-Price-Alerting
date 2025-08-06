# Frontend Setup Instructions

## Prerequisites
- Node.js (v16 or higher)
- npm or yarn

## Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

4. **Open your browser and navigate to:**
   ```
   http://localhost:3000
   ```

## Environment Configuration

The frontend is configured to proxy API requests to `http://localhost:8000` during development.

If your Django backend is running on a different port, update the `proxy` field in `package.json`:

```json
{
  "proxy": "http://localhost:YOUR_BACKEND_PORT"
}
```

## Features

### 🔐 Authentication
- User registration and login
- JWT token-based authentication
- Secure API communication

### 📊 Dashboard
- Overview of alerts and stocks
- Quick stats and metrics
- Recent triggered alerts

### 📈 Stock Monitoring
- View all available stocks
- Click stocks to see price history
- Real-time price data display

### 🔔 Alert Management
- Create threshold and duration-based alerts
- Manage active/inactive alerts
- View triggered alert history

## API Integration

The frontend communicates with your Django REST API using:
- **Base URL:** `http://localhost:8000/api`
- **Authentication:** JWT Bearer tokens
- **Automatic token refresh:** Handles token expiration seamlessly

## Usage Guide

1. **Register/Login:** Create an account or sign in
2. **View Dashboard:** See overview of your alerts and stocks
3. **Browse Stocks:** Explore available stocks and their price history
4. **Create Alerts:** Set up price monitoring with conditions
5. **Manage Alerts:** Activate/deactivate and delete alerts
6. **Monitor Results:** Check triggered alerts and notifications

## Development

To build for production:
```bash
npm run build
```

The optimized files will be created in the `build` directory.

## Troubleshooting

**CORS Issues:** Ensure your Django backend includes the frontend URL in `CORS_ALLOWED_ORIGINS`

**API Connection:** Verify the Django backend is running on port 8000

**Authentication:** Check that JWT tokens are properly configured in Django settings
