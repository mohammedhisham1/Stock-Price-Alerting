import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token');
                if (refreshToken) {
                    const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
                        refresh: refreshToken,
                    });

                    const { access } = response.data;
                    localStorage.setItem('access_token', access);

                    // Retry the original request
                    originalRequest.headers.Authorization = `Bearer ${access}`;
                    return api(originalRequest);
                }
            } catch (refreshError) {
                // Refresh failed, redirect to login
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/login';
            }
        }

        return Promise.reject(error);
    }
);

// Auth API calls
export const authAPI = {
    register: (userData) => api.post('/auth/register/', userData),
    login: (credentials) => api.post('/auth/login/', credentials),
    profile: () => api.get('/auth/profile/'),
    updateProfile: (userData) => api.put('/auth/profile/', userData),
};

// Stock API calls
export const stockAPI = {
    getStocks: () => api.get('/stocks/'),
    getStock: (id) => api.get(`/stocks/${id}/`),
    getStockPrices: (id) => api.get(`/stocks/${id}/prices/`),
};

// Alert API calls
export const alertAPI = {
    getAlerts: () => api.get('/alerts/'),
    createAlert: (alertData) => api.post('/alerts/', alertData),
    updateAlert: (id, alertData) => api.put(`/alerts/${id}/`, alertData),
    deleteAlert: (id) => api.delete(`/alerts/${id}/`),
    getTriggeredAlerts: () => api.get('/alerts/triggered/'),
};

export default api;
