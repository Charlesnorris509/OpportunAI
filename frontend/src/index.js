import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <React.StrictMode>
        <BrowserRouter>
            <App />
        </BrowserRouter>
    </React.StrictMode>
);
// Extended functionality: Add service worker registration
import * as serviceWorkerRegistration from './serviceWorkerRegistration';
// Register the service worker for offline support and faster loading
if (process.env.NODE_ENV === 'production') {
    serviceWorkerRegistration.register();
} else {
    serviceWorkerRegistration.unregister();
}


// Optional: Enable web vitals reporting
import reportWebVitals from './reportWebVitals';

if (process.env.NODE_ENV === 'production') {
    reportWebVitals(console.log);
}
