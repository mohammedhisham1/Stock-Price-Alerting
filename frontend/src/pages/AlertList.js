import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { alertAPI } from '../services/api';
import toast from 'react-hot-toast';

const AlertList = () => {
    const [alerts, setAlerts] = useState([]);
    const [triggeredAlerts, setTriggeredAlerts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('active');
    const [deletingAlert, setDeletingAlert] = useState(null);

    useEffect(() => {
        fetchAlerts();
    }, []);

    const fetchAlerts = async () => {
        try {
            const [alertsResponse, triggeredResponse] = await Promise.all([
                alertAPI.getAlerts(),
                alertAPI.getTriggeredAlerts()
            ]);

            // Handle nested response structure
            const alertsData = alertsResponse.data.results?.data || alertsResponse.data.data || alertsResponse.data.results || alertsResponse.data;
            const triggeredData = triggeredResponse.data.results?.data || triggeredResponse.data.data || triggeredResponse.data.results || triggeredResponse.data;

            setAlerts(Array.isArray(alertsData) ? alertsData : []);
            setTriggeredAlerts(Array.isArray(triggeredData) ? triggeredData : []);
        } catch (error) {
            console.error('Error fetching alerts:', error);
            toast.error('Failed to fetch alerts');
            // Set empty arrays on error to prevent filter errors
            setAlerts([]);
            setTriggeredAlerts([]);
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteAlert = async (alertId) => {
        if (!window.confirm('Are you sure you want to delete this alert?')) {
            return;
        }

        setDeletingAlert(alertId);
        try {
            await alertAPI.deleteAlert(alertId);
            setAlerts(Array.isArray(alerts) ? alerts.filter(alert => alert.id !== alertId) : []);
            toast.success('Alert deleted successfully');
        } catch (error) {
            console.error('Error deleting alert:', error);
            toast.error('Failed to delete alert');
        } finally {
            setDeletingAlert(null);
        }
    };

    const handleToggleAlert = async (alert) => {
        try {
            const updatedAlert = { ...alert, is_active: !alert.is_active };
            await alertAPI.updateAlert(alert.id, updatedAlert);
            setAlerts(alerts.map(a => a.id === alert.id ? updatedAlert : a));
            toast.success(`Alert ${updatedAlert.is_active ? 'activated' : 'deactivated'} successfully`);
        } catch (error) {
            console.error('Error updating alert:', error);
            toast.error('Failed to update alert');
        }
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleString();
    };

    const formatPrice = (price) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(price);
    };

    const getAlertTypeIcon = (type) => {
        switch (type) {
            case 'threshold': return '🎯';
            case 'duration': return '⏰';
            default: return '🔔';
        }
    };

    const getConditionIcon = (condition) => {
        switch (condition) {
            case 'above': return '📈';
            case 'below': return '📉';
            default: return '📊';
        }
    };

    if (loading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
                <div className="loading-spinner"></div>
            </div>
        );
    }

    const activeAlerts = Array.isArray(alerts) ? alerts.filter(alert => alert.is_active) : [];
    const inactiveAlerts = Array.isArray(alerts) ? alerts.filter(alert => !alert.is_active) : [];

    return (
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
            <div style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>
                        🔔 My Alerts
                    </h1>
                    <Link to="/alerts/create" style={{ textDecoration: 'none' }}>
                        <button className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span style={{ fontSize: '1.25rem' }}>➕</span>
                            Create New Alert
                        </button>
                    </Link>
                </div>
                <p style={{ color: '#6b7280', fontSize: '1.1rem' }}>
                    Manage your stock price alerts and view triggered notifications.
                </p>
            </div>

            {/* Tab Navigation */}
            <div style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '2px solid #e5e7eb' }}>
                    <button
                        onClick={() => setActiveTab('active')}
                        style={{
                            padding: '0.75rem 1.5rem',
                            border: 'none',
                            backgroundColor: 'transparent',
                            cursor: 'pointer',
                            fontWeight: '500',
                            borderBottom: activeTab === 'active' ? '2px solid #2563eb' : '2px solid transparent',
                            color: activeTab === 'active' ? '#2563eb' : '#6b7280'
                        }}
                    >
                        Active Alerts ({activeAlerts.length})
                    </button>
                    <button
                        onClick={() => setActiveTab('inactive')}
                        style={{
                            padding: '0.75rem 1.5rem',
                            border: 'none',
                            backgroundColor: 'transparent',
                            cursor: 'pointer',
                            fontWeight: '500',
                            borderBottom: activeTab === 'inactive' ? '2px solid #2563eb' : '2px solid transparent',
                            color: activeTab === 'inactive' ? '#2563eb' : '#6b7280'
                        }}
                    >
                        Inactive Alerts ({inactiveAlerts.length})
                    </button>
                    <button
                        onClick={() => setActiveTab('triggered')}
                        style={{
                            padding: '0.75rem 1.5rem',
                            border: 'none',
                            backgroundColor: 'transparent',
                            cursor: 'pointer',
                            fontWeight: '500',
                            borderBottom: activeTab === 'triggered' ? '2px solid #2563eb' : '2px solid transparent',
                            color: activeTab === 'triggered' ? '#2563eb' : '#6b7280'
                        }}
                    >
                        Triggered Alerts ({triggeredAlerts.length})
                    </button>
                </div>
            </div>

            {/* Alert Content */}
            {activeTab === 'active' && (
                <div>
                    {activeAlerts.length === 0 ? (
                        <div className="card-shadow" style={{
                            backgroundColor: 'white',
                            padding: '3rem',
                            borderRadius: '8px',
                            textAlign: 'center'
                        }}>
                            <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🔔</div>
                            <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>No Active Alerts</h2>
                            <p style={{ color: '#6b7280', marginBottom: '2rem' }}>
                                Create your first alert to start monitoring stock prices.
                            </p>
                            <Link to="/alerts/create" style={{ textDecoration: 'none' }}>
                                <button className="btn-primary">Create Alert</button>
                            </Link>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {activeAlerts.map((alert) => (
                                <div
                                    key={alert.id}
                                    className="alert-card card-shadow active"
                                    style={{
                                        backgroundColor: 'white',
                                        padding: '1.5rem',
                                        borderRadius: '8px'
                                    }}
                                >
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                                        <div style={{ flex: 1 }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                                                <span style={{ fontSize: '1.5rem' }}>
                                                    {getAlertTypeIcon(alert.alert_type)}
                                                </span>
                                                <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', margin: 0 }}>
                                                    {alert.stock_symbol} - {alert.alert_type.charAt(0).toUpperCase() + alert.alert_type.slice(1)} Alert
                                                </h3>
                                                <span style={{
                                                    padding: '0.25rem 0.75rem',
                                                    backgroundColor: '#dcfce7',
                                                    color: '#16a34a',
                                                    borderRadius: '9999px',
                                                    fontSize: '0.75rem',
                                                    fontWeight: '500'
                                                }}>
                                                    Active
                                                </span>
                                            </div>

                                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
                                                <div>
                                                    <p style={{ fontSize: '0.875rem', color: '#6b7280', margin: '0 0 0.25rem 0' }}>Condition</p>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                        <span>{getConditionIcon(alert.condition)}</span>
                                                        <span style={{ fontWeight: '500' }}>
                                                            {alert.condition} {formatPrice(alert.threshold_price)}
                                                        </span>
                                                    </div>
                                                </div>

                                                {alert.alert_type === 'duration' && (
                                                    <div>
                                                        <p style={{ fontSize: '0.875rem', color: '#6b7280', margin: '0 0 0.25rem 0' }}>Duration</p>
                                                        <p style={{ fontWeight: '500' }}>{alert.duration_minutes} minutes</p>
                                                    </div>
                                                )}

                                                <div>
                                                    <p style={{ fontSize: '0.875rem', color: '#6b7280', margin: '0 0 0.25rem 0' }}>Created</p>
                                                    <p style={{ fontWeight: '500' }}>{formatDate(alert.created_at)}</p>
                                                </div>
                                            </div>

                                            {alert.description && (
                                                <div style={{ marginBottom: '1rem' }}>
                                                    <p style={{ fontSize: '0.875rem', color: '#6b7280', margin: '0 0 0.25rem 0' }}>Description</p>
                                                    <p style={{ fontStyle: 'italic' }}>{alert.description}</p>
                                                </div>
                                            )}
                                        </div>

                                        <div style={{ display: 'flex', gap: '0.5rem', marginLeft: '1rem' }}>
                                            <button
                                                onClick={() => handleToggleAlert(alert)}
                                                className="btn-secondary"
                                                style={{ fontSize: '0.875rem' }}
                                            >
                                                Deactivate
                                            </button>
                                            <button
                                                onClick={() => handleDeleteAlert(alert.id)}
                                                disabled={deletingAlert === alert.id}
                                                className="btn-danger"
                                                style={{ fontSize: '0.875rem' }}
                                            >
                                                {deletingAlert === alert.id ? '...' : 'Delete'}
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'inactive' && (
                <div>
                    {inactiveAlerts.length === 0 ? (
                        <div className="card-shadow" style={{
                            backgroundColor: 'white',
                            padding: '3rem',
                            borderRadius: '8px',
                            textAlign: 'center'
                        }}>
                            <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>😴</div>
                            <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>No Inactive Alerts</h2>
                            <p style={{ color: '#6b7280' }}>
                                All your alerts are currently active and monitoring.
                            </p>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {inactiveAlerts.map((alert) => (
                                <div
                                    key={alert.id}
                                    className="alert-card card-shadow"
                                    style={{
                                        backgroundColor: 'white',
                                        padding: '1.5rem',
                                        borderRadius: '8px',
                                        opacity: 0.7
                                    }}
                                >
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                                        <div style={{ flex: 1 }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                                                <span style={{ fontSize: '1.5rem' }}>
                                                    {getAlertTypeIcon(alert.alert_type)}
                                                </span>
                                                <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', margin: 0 }}>
                                                    {alert.stock_symbol} - {alert.alert_type.charAt(0).toUpperCase() + alert.alert_type.slice(1)} Alert
                                                </h3>
                                                <span style={{
                                                    padding: '0.25rem 0.75rem',
                                                    backgroundColor: '#fee2e2',
                                                    color: '#dc2626',
                                                    borderRadius: '9999px',
                                                    fontSize: '0.75rem',
                                                    fontWeight: '500'
                                                }}>
                                                    Inactive
                                                </span>
                                            </div>

                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                                                <span>{getConditionIcon(alert.condition)}</span>
                                                <span style={{ fontWeight: '500' }}>
                                                    {alert.condition} {formatPrice(alert.threshold_price)}
                                                </span>
                                            </div>
                                        </div>

                                        <div style={{ display: 'flex', gap: '0.5rem', marginLeft: '1rem' }}>
                                            <button
                                                onClick={() => handleToggleAlert(alert)}
                                                className="btn-success"
                                                style={{ fontSize: '0.875rem' }}
                                            >
                                                Activate
                                            </button>
                                            <button
                                                onClick={() => handleDeleteAlert(alert.id)}
                                                disabled={deletingAlert === alert.id}
                                                className="btn-danger"
                                                style={{ fontSize: '0.875rem' }}
                                            >
                                                {deletingAlert === alert.id ? '...' : 'Delete'}
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'triggered' && (
                <div>
                    {triggeredAlerts.length === 0 ? (
                        <div className="card-shadow" style={{
                            backgroundColor: 'white',
                            padding: '3rem',
                            borderRadius: '8px',
                            textAlign: 'center'
                        }}>
                            <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🔕</div>
                            <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>No Triggered Alerts</h2>
                            <p style={{ color: '#6b7280' }}>
                                Your alerts haven't been triggered yet. They're monitoring quietly!
                            </p>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {triggeredAlerts.map((triggered, index) => (
                                <div
                                    key={index}
                                    className="alert-card card-shadow triggered"
                                    style={{
                                        backgroundColor: 'white',
                                        padding: '1.5rem',
                                        borderRadius: '8px'
                                    }}
                                >
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                                        <div>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                                                <span style={{ fontSize: '1.5rem' }}>🚨</span>
                                                <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', margin: 0 }}>
                                                    Alert Triggered
                                                </h3>
                                                <span style={{
                                                    padding: '0.25rem 0.75rem',
                                                    backgroundColor: '#fef3c7',
                                                    color: '#92400e',
                                                    borderRadius: '9999px',
                                                    fontSize: '0.75rem',
                                                    fontWeight: '500'
                                                }}>
                                                    Triggered
                                                </span>
                                            </div>

                                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                                                <div>
                                                    <p style={{ fontSize: '0.875rem', color: '#6b7280', margin: '0 0 0.25rem 0' }}>Alert Type</p>
                                                    <p style={{ fontWeight: '500' }}>{triggered.alert_type}</p>
                                                </div>

                                                <div>
                                                    <p style={{ fontSize: '0.875rem', color: '#6b7280', margin: '0 0 0.25rem 0' }}>Triggered At</p>
                                                    <p style={{ fontWeight: '500' }}>{formatDate(triggered.triggered_at)}</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default AlertList;

