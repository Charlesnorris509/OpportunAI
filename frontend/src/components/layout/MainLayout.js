import React from 'react';
import { useNavigate } from 'react-router-dom';

const MainLayout = ({ children }) => {
    const navigate = useNavigate();
    
    return (
        <div className="layout">
            <header className="header">
                <nav>
                    <button onClick={() => navigate('/dashboard')}>Dashboard</button>
                    <button onClick={() => navigate('/profile')}>Profile</button>
                    <button onClick={() => navigate('/')}>Logout</button>
                </nav>
            </header>
            <main className="main-content">
                {children}
            </main>
            <style jsx>{`
                .layout {
                    min-height: 100vh;
                }
                .header {
                    padding: 1rem;
                    background: #f8f9fa;
                    border-bottom: 1px solid #dee2e6;
                }
                .main-content {
                    padding: 2rem;
                }
            `}</style>
        </div>
    );
};

export default MainLayout;
