# Stock Price Alerting System - API Documentation

## Base URL
```
Production: https://your-domain.com/api/
Development: http://localhost:8000/api/
```

## Authentication

All API endpoints (except registration and login) require JWT authentication.

### Headers
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Endpoints

### Authentication

#### Register User
```http
POST /api/auth/register/
```

**Request Body:**
```json
{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response:**
```json
{
    "success": true,
    "message": "User registered successfully",
    "data": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "user": {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "date_joined": "2025-01-01T00:00:00Z"
        }
    }
}
```

#### Login
```http
POST /api/auth/login/
```

**Request Body:**
```json
{
    "username": "testuser",
    "password": "securepassword123"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Login successful",
    "data": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "user": {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "date_joined": "2025-01-01T00:00:00Z"
        }
    }
}
```

#### Get Profile
```http
GET /api/auth/profile/
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "date_joined": "2025-01-01T00:00:00Z"
    }
}
```

#### Refresh Token
```http
POST /api/auth/token/refresh/
```

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Stocks

#### List All Stocks
```http
GET /api/stocks/
```

**Query Parameters:**
- `symbol` (optional): Filter by stock symbol

**Response:**
```json
{
    "success": true,
    "count": 10,
    "data": [
        {
            "id": 1,
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "exchange": "NASDAQ",
            "is_active": true,
            "latest_price": 150.25,
            "price_change_24h": {
                "amount": 2.50,
                "percentage": 1.69
            },
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }
    ]
}
```

#### Get Current Prices
```http
GET /api/stocks/current_prices/
```

**Response:**
```json
{
    "success": true,
    "count": 10,
    "data": [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "price": 150.25,
            "timestamp": "2025-01-01T12:00:00Z",
            "exchange": "NASDAQ"
        }
    ],
    "timestamp": "2025-01-01T12:00:00Z"
}
```

#### Get Price History
```http
GET /api/stocks/{id}/price_history/
```

**Query Parameters:**
- `hours` (optional): Number of hours to look back (default: 24)

**Response:**
```json
{
    "success": true,
    "symbol": "AAPL",
    "period": "24 hours",
    "count": 288,
    "data": [
        {
            "id": 1,
            "stock": 1,
            "stock_symbol": "AAPL",
            "price": "150.25",
            "open_price": "149.50",
            "high_price": "151.00",
            "low_price": "148.75",
            "close_price": "150.25",
            "volume": 1000000,
            "timestamp": "2025-01-01T12:00:00Z",
            "created_at": "2025-01-01T12:00:00Z"
        }
    ]
}
```

#### Refresh All Prices
```http
POST /api/stocks/refresh_prices/
```

**Response:**
```json
{
    "success": true,
    "message": "Price refresh initiated",
    "task_id": "12345-abcde-67890"
}
```

### Alerts

#### Create Alert
```http
POST /api/alerts/
```

**Request Body (Threshold Alert):**
```json
{
    "stock_symbol": "AAPL",
    "alert_type": "threshold",
    "condition": "above",
    "threshold_price": 200.00
}
```

**Request Body (Duration Alert):**
```json
{
    "stock_symbol": "TSLA",
    "alert_type": "duration",
    "condition": "below",
    "threshold_price": 600.00,
    "duration_minutes": 120
}
```

**Response:**
```json
{
    "success": true,
    "message": "Alert created successfully",
    "data": {
        "id": 1,
        "stock": 1,
        "stock_symbol": "AAPL",
        "stock_name": "Apple Inc.",
        "alert_type": "threshold",
        "condition": "above",
        "threshold_price": "200.00",
        "duration_minutes": null,
        "is_active": true,
        "condition_first_met": null,
        "condition_currently_met": false,
        "created_at": "2025-01-01T12:00:00Z",
        "updated_at": "2025-01-01T12:00:00Z"
    }
}
```

#### List User Alerts
```http
GET /api/alerts/
```

**Query Parameters:**
- `is_active` (optional): Filter by active status (true/false)
- `stock_symbol` (optional): Filter by stock symbol

**Response:**
```json
{
    "success": true,
    "count": 5,
    "data": [
        {
            "id": 1,
            "stock": 1,
            "stock_symbol": "AAPL",
            "stock_name": "Apple Inc.",
            "alert_type": "threshold",
            "condition": "above",
            "threshold_price": "200.00",
            "duration_minutes": null,
            "is_active": true,
            "condition_first_met": null,
            "condition_currently_met": false,
            "created_at": "2025-01-01T12:00:00Z",
            "updated_at": "2025-01-01T12:00:00Z"
        }
    ]
}
```

#### Get Single Alert
```http
GET /api/alerts/{id}/
```

#### Update Alert
```http
PUT /api/alerts/{id}/
```

#### Delete Alert
```http
DELETE /api/alerts/{id}/
```

**Response:**
```json
{
    "success": true,
    "message": "Alert deleted successfully"
}
```

#### Get Triggered Alerts
```http
GET /api/alerts/triggered/
```

**Query Parameters:**
- `days` (optional): Number of days to look back

**Response:**
```json
{
    "success": true,
    "count": 3,
    "data": [
        {
            "id": 1,
            "alert": {
                "id": 1,
                "stock_symbol": "AAPL",
                "alert_type": "threshold",
                "condition": "above",
                "threshold_price": "200.00"
            },
            "stock_symbol": "AAPL",
            "stock_name": "Apple Inc.",
            "alert_type": "threshold",
            "condition": "above",
            "threshold_price": "200.00",
            "trigger_price": "205.50",
            "triggered_at": "2025-01-01T15:30:00Z",
            "email_sent": true,
            "email_sent_at": "2025-01-01T15:30:15Z",
            "notification_error": ""
        }
    ]
}
```

#### Test Alert
```http
POST /api/alerts/{id}/test_alert/
```

**Response:**
```json
{
    "success": true,
    "message": "Alert tested successfully",
    "result": {
        "alert_id": 1,
        "success": true,
        "triggered": false,
        "current_price": 195.50
    }
}
```

#### Get Alert Statistics
```http
GET /api/alerts/statistics/
```

**Response:**
```json
{
    "success": true,
    "data": {
        "total_alerts": 10,
        "active_alerts": 7,
        "inactive_alerts": 3,
        "total_triggered": 5,
        "triggered_this_week": 2,
        "triggered_this_month": 4,
        "alert_types": {
            "threshold": 6,
            "duration": 4
        }
    }
}
```

### Health Check

#### System Health
```http
GET /health/
```

**Response:**
```json
{
    "status": "OK",
    "timestamp": "2025-01-01T12:00:00Z",
    "database": "OK",
    "redis": "OK",
    "version": "1.0.0"
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
    "success": false,
    "error": "Error message here",
    "errors": {
        "field_name": ["Field-specific error message"]
    }
}
```

## Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Rate Limiting

API requests are limited to prevent abuse:
- 1000 requests per hour per user for authenticated endpoints
- 100 requests per hour per IP for unauthenticated endpoints

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Paginated Response:**
```json
{
    "success": true,
    "count": 100,
    "next": "http://api.example.com/endpoint/?page=3",
    "previous": "http://api.example.com/endpoint/?page=1",
    "results": [...]
}
```
