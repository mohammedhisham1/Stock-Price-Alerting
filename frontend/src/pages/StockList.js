import React, { useState, useEffect } from 'react';
import { stockAPI } from '../services/api';

const StockList = () => {
    const [stocks, setStocks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedStock, setSelectedStock] = useState(null);
    const [priceHistory, setPriceHistory] = useState([]);
    const [loadingPrices, setLoadingPrices] = useState(false);

    useEffect(() => {
        const fetchStocks = async () => {
            try {
                const response = await stockAPI.getStocks();
                setStocks(response.data.results || response.data);
            } catch (error) {
                console.error('Error fetching stocks:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchStocks();
    }, []);

    const handleStockClick = async (stock) => {
        if (selectedStock?.id === stock.id) {
            setSelectedStock(null);
            setPriceHistory([]);
            return;
        }

        setSelectedStock(stock);
        setLoadingPrices(true);

        try {
            const response = await stockAPI.getStockPrices(stock.id);
            setPriceHistory(response.data.data || response.data.results || response.data);
        } catch (error) {
            console.error('Error fetching price history:', error);
            setPriceHistory([]);
        } finally {
            setLoadingPrices(false);
        }
    };

    const formatPrice = (price) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(price);
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleString();
    };

    const getPriceChangeClass = (current, previous) => {
        if (!previous) return 'price-neutral';
        if (current > previous) return 'price-up';
        if (current < previous) return 'price-down';
        return 'price-neutral';
    };

    const getPriceChangeIcon = (current, previous) => {
        if (!previous) return '➡️';
        if (current > previous) return '📈';
        if (current < previous) return '📉';
        return '➡️';
    };

    if (loading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
                <div className="loading-spinner"></div>
            </div>
        );
    }

    return (
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
            <div style={{ marginBottom: '2rem' }}>
                <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
                    📈 Stock Monitor
                </h1>
                <p style={{ color: '#6b7280', fontSize: '1.1rem' }}>
                    Click on any stock to view its price history and current data.
                </p>
            </div>

            {stocks.length === 0 ? (
                <div className="card-shadow" style={{
                    backgroundColor: 'white',
                    padding: '3rem',
                    borderRadius: '8px',
                    textAlign: 'center'
                }}>
                    <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>📊</div>
                    <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>No Stocks Available</h2>
                    <p style={{ color: '#6b7280' }}>
                        Stock data will appear here once the system starts monitoring stocks.
                    </p>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
                    {stocks.map((stock) => (
                        <div
                            key={stock.id}
                            className="stock-card card-shadow"
                            onClick={() => handleStockClick(stock)}
                            style={{
                                backgroundColor: 'white',
                                padding: '1.5rem',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                border: selectedStock?.id === stock.id ? '2px solid #2563eb' : '1px solid #e2e8f0'
                            }}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                                <div>
                                    <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: '0 0 0.25rem 0' }}>
                                        {stock.symbol}
                                    </h3>
                                    <p style={{ color: '#6b7280', margin: '0 0 0.5rem 0' }}>{stock.name}</p>
                                    <span style={{
                                        display: 'inline-block',
                                        padding: '0.25rem 0.75rem',
                                        backgroundColor: '#dbeafe',
                                        color: '#1e40af',
                                        borderRadius: '9999px',
                                        fontSize: '0.75rem',
                                        fontWeight: '500'
                                    }}>
                                        {stock.exchange}
                                    </span>
                                </div>
                                <div style={{
                                    padding: '0.5rem',
                                    backgroundColor: stock.is_active ? '#dcfce7' : '#fee2e2',
                                    borderRadius: '50%'
                                }}>
                                    <div style={{ fontSize: '1.5rem' }}>
                                        {stock.is_active ? '✅' : '❌'}
                                    </div>
                                </div>
                            </div>

                            <div style={{
                                padding: '0.75rem',
                                backgroundColor: '#f8fafc',
                                borderRadius: '0.5rem',
                                marginTop: '1rem'
                            }}>
                                <p style={{ fontSize: '0.875rem', color: '#6b7280', margin: '0 0 0.5rem 0' }}>
                                    Status: {stock.is_active ? 'Active' : 'Inactive'}
                                </p>
                                <p style={{ fontSize: '0.875rem', color: '#6b7280', margin: 0 }}>
                                    Click to view price history
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Price History Modal/Panel */}
            {selectedStock && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: 'rgba(0, 0, 0, 0.5)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000,
                    padding: '1rem'
                }} onClick={() => setSelectedStock(null)}>
                    <div
                        className="card-shadow"
                        style={{
                            backgroundColor: 'white',
                            borderRadius: '8px',
                            padding: '2rem',
                            maxWidth: '800px',
                            width: '100%',
                            maxHeight: '80vh',
                            overflow: 'auto'
                        }}
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1.5rem' }}>
                            <div>
                                <h2 style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0 0 0.5rem 0' }}>
                                    {selectedStock.symbol} - {selectedStock.name}
                                </h2>
                                <p style={{ color: '#6b7280' }}>{selectedStock.exchange}</p>
                            </div>
                            <button
                                onClick={() => setSelectedStock(null)}
                                style={{
                                    background: 'none',
                                    border: 'none',
                                    fontSize: '1.5rem',
                                    cursor: 'pointer',
                                    padding: '0.5rem',
                                    borderRadius: '0.25rem'
                                }}
                            >
                                ✕
                            </button>
                        </div>

                        <div style={{ marginBottom: '1.5rem' }}>
                            <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem' }}>
                                Price History
                            </h3>

                            {loadingPrices ? (
                                <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
                                    <div className="loading-spinner"></div>
                                </div>
                            ) : priceHistory.length > 0 ? (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '400px', overflow: 'auto' }}>
                                    {priceHistory.map((price, index) => {
                                        const previousPrice = priceHistory[index + 1];
                                        return (
                                            <div
                                                key={price.id}
                                                style={{
                                                    display: 'flex',
                                                    justifyContent: 'space-between',
                                                    alignItems: 'center',
                                                    padding: '1rem',
                                                    backgroundColor: '#f8fafc',
                                                    borderRadius: '0.5rem',
                                                    border: '1px solid #e2e8f0'
                                                }}
                                            >
                                                <div>
                                                    <p style={{ fontWeight: '500', margin: '0 0 0.25rem 0' }}>
                                                        {formatDate(price.timestamp)}
                                                    </p>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                        <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                                                            Open: {formatPrice(price.open_price)}
                                                        </span>
                                                        <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                                                            Close: {formatPrice(price.close_price)}
                                                        </span>
                                                    </div>
                                                </div>
                                                <div style={{ textAlign: 'right' }}>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                        <span className={getPriceChangeClass(price.close_price, previousPrice?.close_price)} style={{ fontWeight: 'bold' }}>
                                                            {formatPrice(price.close_price)}
                                                        </span>
                                                        <span style={{ fontSize: '1.25rem' }}>
                                                            {getPriceChangeIcon(price.close_price, previousPrice?.close_price)}
                                                        </span>
                                                    </div>
                                                    <p style={{ fontSize: '0.75rem', color: '#6b7280', margin: '0.25rem 0 0 0' }}>
                                                        Vol: {price.volume?.toLocaleString() || 'N/A'}
                                                    </p>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            ) : (
                                <div style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>
                                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📊</div>
                                    <p>No price history available for this stock yet.</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default StockList;
