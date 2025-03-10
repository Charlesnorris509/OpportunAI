import React from 'react';

const LoadingSpinner = () => (
    <div className="loading-spinner">
        <div className="spinner"></div>
        <style jsx>{`
            .loading-spinner {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .spinner {
                width: 50px;
                height: 50px;
                border: 5px solid #f3f3f3;
                border-top: 5px solid #3498db;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `}</style>
    </div>
);

export default LoadingSpinner;
