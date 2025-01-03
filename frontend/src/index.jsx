import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';

ReactDOM.render(
    <React.StrictMode>
        <BrowserRouter>
            <App />
        </BrowserRouter>
    </React.StrictMode>,
    document.getElementById('root')
);

// Extended functionality: Add service worker registration
import * as serviceWorkerRegistration from './serviceWorkerRegistration';

// Register the service worker for offline support and faster loading
serviceWorkerRegistration.register();

// Optional: Enable web vitals reporting
import reportWebVitals from './reportWebVitals';

reportWebVitals(console.log);
