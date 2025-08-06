import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { stockAPI, alertAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Dashboard = () => {
    const { user } = useAuth();
    const [stats, setStats] = useState({
        totalAlerts: 0,
        activeAlerts: 0,
        triggeredAlerts: 0,
        monitoredStocks: 0
    });
    const [recentAlerts, setRecentAlerts] = useState([]);
    const [stocks, setStocks] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                const [alertsResponse, stocksResponse, triggeredResponse] = await Promise.all([
                    alertAPI.getAlerts(),
                    stockAPI.getStocks(),
                    alertAPI.getTriggeredAlerts()
                ]);

                // Handle different response formats
                const alerts = Array.isArray(alertsResponse.data.results)
                    ? alertsResponse.data.results
                    : (alertsResponse.data.results?.data || alertsResponse.data || []);

                const stocksData = Array.isArray(stocksResponse.data.results)
                    ? stocksResponse.data.results
                    : (stocksResponse.data.results?.data || stocksResponse.data || []);

                const triggered = Array.isArray(triggeredResponse.data.results)
                    ? triggeredResponse.data.results
                    : (triggeredResponse.data.results?.data || triggeredResponse.data || []);

                setStats({
                    totalAlerts: alerts.length,
                    activeAlerts: alerts.filter(alert => alert.is_active).length,
                    triggeredAlerts: triggered.length,
                    monitoredStocks: stocksData.length
                });

                setRecentAlerts(triggered.slice(0, 5));
                setStocks(stocksData.slice(0, 6));
            } catch (error) {
                console.error('Error fetching dashboard data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, []);

    if (loading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
                <div className="loading-spinner"></div>
            </div>
        );
    }

    return (
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
            {/* Welcome Section */}
            <div style={{ marginBottom: '2rem' }}>
                <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
                    Welcome back, {user.first_name || user.username}! 👋
                </h1>
                <p style={{ color: '#6b7280', fontSize: '1.1rem' }}>
                    Here's what's happening with your stock alerts today.
                </p>
            </div>

            {/* Stats Cards */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                gap: '1.5rem',
                marginBottom: '2rem'
            }}>
                <div className="card-shadow" style={{
                    backgroundColor: 'white',
                    padding: '1.5rem',
                    borderRadius: '8px',
                    borderLeft: '4px solid #2563eb'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                        <div>
                            <p style={{ color: '#6b7280', fontSize: '0.875rem', margin: '0 0 0.5rem 0' }}>Total Alerts</p>
                            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0 }}>{stats.totalAlerts}</p>
                        </div>
                        <div style={{ fontSize: '2rem' }}>🔔</div>
                    </div>
                </div>

                <div className="card-shadow" style={{
                    backgroundColor: 'white',
                    padding: '1.5rem',
                    borderRadius: '8px',
                    borderLeft: '4px solid #10b981'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                        <div>
                            <p style={{ color: '#6b7280', fontSize: '0.875rem', margin: '0 0 0.5rem 0' }}>Active Alerts</p>
                            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0 }}>{stats.activeAlerts}</p>
                        </div>
                        <div style={{ fontSize: '2rem' }}>✅</div>
                    </div>
                </div>

                <div className="card-shadow" style={{
                    backgroundColor: 'white',
                    padding: '1.5rem',
                    borderRadius: '8px',
                    borderLeft: '4px solid #f59e0b'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                        <div>
                            <p style={{ color: '#6b7280', fontSize: '0.875rem', margin: '0 0 0.5rem 0' }}>Triggered Today</p>
                            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0 }}>{stats.triggeredAlerts}</p>
                        </div>
                        <div style={{ fontSize: '2rem' }}>🚨</div>
                    </div>
                </div>

                <div className="card-shadow" style={{
                    backgroundColor: 'white',
                    padding: '1.5rem',
                    borderRadius: '8px',
                    borderLeft: '4px solid #8b5cf6'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                        <div>
                            <p style={{ color: '#6b7280', fontSize: '0.875rem', margin: '0 0 0.5rem 0' }}>Monitored Stocks</p>
                            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0 }}>{stats.monitoredStocks}</p>
                        </div>
                        <div style={{ fontSize: '2rem' }}>📈</div>
                    </div>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="card-shadow" style={{
                backgroundColor: 'white',
                padding: '2rem',
                borderRadius: '8px',
                marginBottom: '2rem'
            }}>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1rem' }}>
                    Quick Actions
                </h2>
                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                    <Link to="/alerts/create" style={{ textDecoration: 'none' }}>
                        <button className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span style={{ fontSize: '1.25rem' }}>➕</span>
                            Create New Alert
                        </button>
                    </Link>
                    <Link to="/stocks" style={{ textDecoration: 'none' }}>
                        <button className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span style={{ fontSize: '1.25rem' }}>📊</span>
                            View All Stocks
                        </button>
                    </Link>
                    <Link to="/alerts" style={{ textDecoration: 'none' }}>
                        <button className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span style={{ fontSize: '1.25rem' }}>🔔</span>
                            Manage Alerts
                        </button>
                    </Link>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', gap: '2rem' }}>
                {/* Recent Triggered Alerts */}
                <div className="card-shadow" style={{
                    backgroundColor: 'white',
                    padding: '1.5rem',
                    borderRadius: '8px'
                }}>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem' }}>
                        Recent Triggered Alerts
                    </h3>
                    {recentAlerts.length > 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                            {recentAlerts.map((alert, index) => (
                                <div key={index} style={{
                                    padding: '1rem',
                                    backgroundColor: '#fef3c7',
                                    borderRadius: '0.5rem',
                                    borderLeft: '4px solid #f59e0b'
                                }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                                        <div>
                                            <p style={{ fontWeight: '500', margin: '0 0 0.25rem 0' }}>
                                                {alert.alert_type} Alert Triggered
                                            </p>
                                            <p style={{ color: '#92400e', fontSize: '0.875rem', margin: 0 }}>
                                                {new Date(alert.triggered_at).toLocaleString()}
                                            </p>
                                        </div>
                                        <span style={{ fontSize: '1.25rem' }}>🚨</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p style={{ color: '#6b7280', textAlign: 'center', padding: '2rem' }}>
                            No alerts triggered recently. Your alerts are monitoring quietly! 😴
                        </p>
                    )}
                </div>

                {/* Quick Stock Overview */}
                <div className="card-shadow" style={{
                    backgroundColor: 'white',
                    padding: '1.5rem',
                    borderRadius: '8px'
                }}>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem' }}>
                        Stock Overview
                    </h3>
                    {stocks.length > 0 ? (
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '0.75rem' }}>
                            {stocks.map((stock) => (
                                <div key={stock.id} className="stock-card" style={{
                                    padding: '1rem',
                                    backgroundColor: '#f8fafc',
                                    borderRadius: '0.5rem',
                                    textAlign: 'center',
                                    border: '1px solid #e2e8f0'
                                }}>
                                    <p style={{ fontWeight: 'bold', margin: '0 0 0.25rem 0' }}>{stock.symbol}</p>
                                    <p style={{ fontSize: '0.75rem', color: '#6b7280', margin: 0 }}>
                                        {stock.exchange}
                                    </p>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p style={{ color: '#6b7280', textAlign: 'center', padding: '2rem' }}>
                            No stocks available for monitoring.
                        </p>
                    )}
                    <Link to="/stocks" style={{ textDecoration: 'none' }}>
                        <button className="btn-secondary" style={{ width: '100%', marginTop: '1rem' }}>
                            View All Stocks
                        </button>
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
