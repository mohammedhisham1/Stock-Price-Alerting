import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navbar = () => {
    const { user, logout } = useAuth();
    const location = useLocation();

    const isActive = (path) => location.pathname === path;

    if (!user) {
        return (
            <nav style={{
                backgroundColor: '#1f2937',
                padding: '1rem 0',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
            }}>
                <div style={{
                    maxWidth: '1200px',
                    margin: '0 auto',
                    padding: '0 1rem',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    <Link
                        to="/"
                        style={{
                            fontSize: '1.5rem',
                            fontWeight: 'bold',
                            color: 'white',
                            textDecoration: 'none'
                        }}
                    >
                        📈 Stock Alerts
                    </Link>
                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <Link
                            to="/login"
                            style={{
                                color: 'white',
                                textDecoration: 'none',
                                padding: '0.5rem 1rem',
                                borderRadius: '0.5rem',
                                transition: 'background-color 0.2s',
                                backgroundColor: isActive('/login') ? '#374151' : 'transparent'
                            }}
                        >
                            Login
                        </Link>
                        <Link
                            to="/register"
                            style={{
                                color: 'white',
                                textDecoration: 'none',
                                padding: '0.5rem 1rem',
                                borderRadius: '0.5rem',
                                backgroundColor: '#2563eb',
                                transition: 'background-color 0.2s'
                            }}
                        >
                            Register
                        </Link>
                    </div>
                </div>
            </nav>
        );
    }

    return (
        <nav style={{
            backgroundColor: '#1f2937',
            padding: '1rem 0',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
        }}>
            <div style={{
                maxWidth: '1200px',
                margin: '0 auto',
                padding: '0 1rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <Link
                    to="/dashboard"
                    style={{
                        fontSize: '1.5rem',
                        fontWeight: 'bold',
                        color: 'white',
                        textDecoration: 'none'
                    }}
                >
                    📈 Stock Alerts
                </Link>

                <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <Link
                            to="/dashboard"
                            style={{
                                color: 'white',
                                textDecoration: 'none',
                                padding: '0.5rem 1rem',
                                borderRadius: '0.5rem',
                                transition: 'background-color 0.2s',
                                backgroundColor: isActive('/dashboard') ? '#374151' : 'transparent'
                            }}
                        >
                            Dashboard
                        </Link>
                        <Link
                            to="/stocks"
                            style={{
                                color: 'white',
                                textDecoration: 'none',
                                padding: '0.5rem 1rem',
                                borderRadius: '0.5rem',
                                transition: 'background-color 0.2s',
                                backgroundColor: isActive('/stocks') ? '#374151' : 'transparent'
                            }}
                        >
                            Stocks
                        </Link>
                        <Link
                            to="/alerts"
                            style={{
                                color: 'white',
                                textDecoration: 'none',
                                padding: '0.5rem 1rem',
                                borderRadius: '0.5rem',
                                transition: 'background-color 0.2s',
                                backgroundColor: isActive('/alerts') ? '#374151' : 'transparent'
                            }}
                        >
                            My Alerts
                        </Link>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <span style={{ color: '#9ca3af' }}>
                            Welcome, {user.first_name || user.username}
                        </span>
                        <button
                            onClick={logout}
                            style={{
                                backgroundColor: '#dc2626',
                                color: 'white',
                                border: 'none',
                                padding: '0.5rem 1rem',
                                borderRadius: '0.5rem',
                                cursor: 'pointer',
                                transition: 'background-color 0.2s'
                            }}
                        >
                            Logout
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
