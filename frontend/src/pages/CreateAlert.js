import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { alertAPI, stockAPI } from '../services/api';
import toast from 'react-hot-toast';

const CreateAlert = () => {
    const navigate = useNavigate();
    const [stocks, setStocks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [formData, setFormData] = useState({
        stock: '',
        alert_type: 'threshold',
        condition: 'above',
        target_price: '',
        duration_minutes: '',
        description: '',
        is_active: true
    });

    useEffect(() => {
        const fetchStocks = async () => {
            try {
                const response = await stockAPI.getStocks();
                setStocks(response.data.results || response.data);
            } catch (error) {
                console.error('Error fetching stocks:', error);
                toast.error('Failed to fetch stocks');
            } finally {
                setLoading(false);
            }
        };

        fetchStocks();
    }, []);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData({
            ...formData,
            [name]: type === 'checkbox' ? checked : value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!formData.stock) {
            toast.error('Please select a stock');
            return;
        }

        if (!formData.target_price || parseFloat(formData.target_price) <= 0) {
            toast.error('Please enter a valid target price');
            return;
        }

        if (formData.alert_type === 'duration' && (!formData.duration_minutes || parseInt(formData.duration_minutes) <= 0)) {
            toast.error('Please enter a valid duration in minutes');
            return;
        }

        setSubmitting(true);

        try {
            const alertData = {
                ...formData,
                target_price: parseFloat(formData.target_price),
                duration_minutes: formData.alert_type === 'duration' ? parseInt(formData.duration_minutes) : null
            };

            await alertAPI.createAlert(alertData);
            toast.success('Alert created successfully!');
            navigate('/alerts');
        } catch (error) {
            console.error('Error creating alert:', error);
            const message = error.response?.data?.message || 'Failed to create alert';
            toast.error(message);
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
                <div className="loading-spinner"></div>
            </div>
        );
    }

    return (
        <div style={{ maxWidth: '600px', margin: '0 auto' }}>
            <div style={{ marginBottom: '2rem' }}>
                <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
                    ➕ Create New Alert
                </h1>
                <p style={{ color: '#6b7280', fontSize: '1.1rem' }}>
                    Set up a new alert to monitor stock price changes and get notified when conditions are met.
                </p>
            </div>

            <div className="card-shadow" style={{
                backgroundColor: 'white',
                padding: '2rem',
                borderRadius: '8px'
            }}>
                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    {/* Stock Selection */}
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', fontSize: '1rem' }}>
                            📈 Select Stock *
                        </label>
                        <select
                            name="stock"
                            value={formData.stock}
                            onChange={handleChange}
                            required
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                border: '1px solid #d1d5db',
                                borderRadius: '0.5rem',
                                fontSize: '1rem',
                                outline: 'none',
                                transition: 'border-color 0.2s',
                                boxSizing: 'border-box'
                            }}
                            onFocus={(e) => e.target.style.borderColor = '#2563eb'}
                            onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
                        >
                            <option value="">Choose a stock to monitor</option>
                            {stocks.filter(stock => stock.is_active).map((stock) => (
                                <option key={stock.id} value={stock.id}>
                                    {stock.symbol} - {stock.name} ({stock.exchange})
                                </option>
                            ))}
                        </select>
                        {stocks.filter(stock => stock.is_active).length === 0 && (
                            <p style={{ color: '#dc2626', fontSize: '0.875rem', marginTop: '0.5rem' }}>
                                No active stocks available for monitoring.
                            </p>
                        )}
                    </div>

                    {/* Alert Type */}
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', fontSize: '1rem' }}>
                            🎯 Alert Type *
                        </label>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                            <label style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                padding: '1rem',
                                border: formData.alert_type === 'threshold' ? '2px solid #2563eb' : '1px solid #d1d5db',
                                borderRadius: '0.5rem',
                                cursor: 'pointer',
                                backgroundColor: formData.alert_type === 'threshold' ? '#eff6ff' : 'white'
                            }}>
                                <input
                                    type="radio"
                                    name="alert_type"
                                    value="threshold"
                                    checked={formData.alert_type === 'threshold'}
                                    onChange={handleChange}
                                    style={{ margin: 0 }}
                                />
                                <div>
                                    <div style={{ fontWeight: '500' }}>🎯 Threshold Alert</div>
                                    <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                                        Trigger when price crosses a specific value
                                    </div>
                                </div>
                            </label>

                            <label style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                padding: '1rem',
                                border: formData.alert_type === 'duration' ? '2px solid #2563eb' : '1px solid #d1d5db',
                                borderRadius: '0.5rem',
                                cursor: 'pointer',
                                backgroundColor: formData.alert_type === 'duration' ? '#eff6ff' : 'white'
                            }}>
                                <input
                                    type="radio"
                                    name="alert_type"
                                    value="duration"
                                    checked={formData.alert_type === 'duration'}
                                    onChange={handleChange}
                                    style={{ margin: 0 }}
                                />
                                <div>
                                    <div style={{ fontWeight: '500' }}>⏰ Duration Alert</div>
                                    <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                                        Trigger when price stays at level for a duration
                                    </div>
                                </div>
                            </label>
                        </div>
                    </div>

                    {/* Condition and Target Price */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1rem', alignItems: 'end' }}>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', fontSize: '1rem' }}>
                                📊 Condition *
                            </label>
                            <select
                                name="condition"
                                value={formData.condition}
                                onChange={handleChange}
                                required
                                style={{
                                    width: '100%',
                                    padding: '0.75rem',
                                    border: '1px solid #d1d5db',
                                    borderRadius: '0.5rem',
                                    fontSize: '1rem',
                                    outline: 'none',
                                    transition: 'border-color 0.2s',
                                    boxSizing: 'border-box'
                                }}
                                onFocus={(e) => e.target.style.borderColor = '#2563eb'}
                                onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
                            >
                                <option value="above">📈 Above</option>
                                <option value="below">📉 Below</option>
                            </select>
                        </div>

                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', fontSize: '1rem' }}>
                                💰 Target Price (USD) *
                            </label>
                            <input
                                type="number"
                                name="target_price"
                                value={formData.target_price}
                                onChange={handleChange}
                                required
                                min="0"
                                step="0.01"
                                placeholder="e.g. 150.00"
                                style={{
                                    width: '100%',
                                    padding: '0.75rem',
                                    border: '1px solid #d1d5db',
                                    borderRadius: '0.5rem',
                                    fontSize: '1rem',
                                    outline: 'none',
                                    transition: 'border-color 0.2s',
                                    boxSizing: 'border-box'
                                }}
                                onFocus={(e) => e.target.style.borderColor = '#2563eb'}
                                onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
                            />
                        </div>
                    </div>

                    {/* Duration (only for duration alerts) */}
                    {formData.alert_type === 'duration' && (
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', fontSize: '1rem' }}>
                                ⏰ Duration (minutes) *
                            </label>
                            <input
                                type="number"
                                name="duration_minutes"
                                value={formData.duration_minutes}
                                onChange={handleChange}
                                required={formData.alert_type === 'duration'}
                                min="1"
                                placeholder="e.g. 30"
                                style={{
                                    width: '100%',
                                    padding: '0.75rem',
                                    border: '1px solid #d1d5db',
                                    borderRadius: '0.5rem',
                                    fontSize: '1rem',
                                    outline: 'none',
                                    transition: 'border-color 0.2s',
                                    boxSizing: 'border-box'
                                }}
                                onFocus={(e) => e.target.style.borderColor = '#2563eb'}
                                onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
                            />
                            <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '0.5rem' }}>
                                Alert will trigger if the price stays {formData.condition} ${formData.target_price || 'X'} for this duration.
                            </p>
                        </div>
                    )}

                    {/* Description */}
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', fontSize: '1rem' }}>
                            📝 Description (optional)
                        </label>
                        <textarea
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            rows="3"
                            placeholder="Add a note about this alert (optional)"
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                border: '1px solid #d1d5db',
                                borderRadius: '0.5rem',
                                fontSize: '1rem',
                                outline: 'none',
                                transition: 'border-color 0.2s',
                                boxSizing: 'border-box',
                                resize: 'vertical'
                            }}
                            onFocus={(e) => e.target.style.borderColor = '#2563eb'}
                            onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
                        />
                    </div>

                    {/* Active Toggle */}
                    <div>
                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                            <input
                                type="checkbox"
                                name="is_active"
                                checked={formData.is_active}
                                onChange={handleChange}
                                style={{ width: '18px', height: '18px' }}
                            />
                            <span style={{ fontWeight: '500', fontSize: '1rem' }}>
                                ✅ Activate alert immediately
                            </span>
                        </label>
                        <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '0.5rem', marginLeft: '1.5rem' }}>
                            Uncheck to create the alert in inactive state. You can activate it later.
                        </p>
                    </div>

                    {/* Alert Preview */}
                    {formData.stock && formData.target_price && (
                        <div style={{
                            padding: '1rem',
                            backgroundColor: '#eff6ff',
                            borderRadius: '0.5rem',
                            border: '1px solid #bfdbfe'
                        }}>
                            <h4 style={{ fontSize: '1rem', fontWeight: '500', marginBottom: '0.5rem', color: '#1e40af' }}>
                                📋 Alert Preview
                            </h4>
                            <p style={{ margin: 0, color: '#1e40af' }}>
                                {formData.alert_type === 'threshold' ? (
                                    <>
                                        Notify me when {stocks.find(s => s.id === parseInt(formData.stock))?.symbol || 'selected stock'}
                                        goes {formData.condition} ${formData.target_price}
                                    </>
                                ) : (
                                    <>
                                        Notify me when {stocks.find(s => s.id === parseInt(formData.stock))?.symbol || 'selected stock'}
                                        stays {formData.condition} ${formData.target_price} for {formData.duration_minutes || 'X'} minutes
                                    </>
                                )}
                            </p>
                        </div>
                    )}

                    {/* Form Actions */}
                    <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                        <button
                            type="button"
                            onClick={() => navigate('/alerts')}
                            className="btn-secondary"
                            style={{ flex: 1 }}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={submitting}
                            className="btn-primary"
                            style={{
                                flex: 2,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '0.5rem'
                            }}
                        >
                            {submitting && <div className="loading-spinner" style={{ width: '16px', height: '16px' }}></div>}
                            {submitting ? 'Creating Alert...' : 'Create Alert'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreateAlert;
