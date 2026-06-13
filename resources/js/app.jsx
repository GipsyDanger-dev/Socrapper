import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './pages/App';
import ErrorBoundary from './components/ErrorBoundary';
import './css/newspaper.css';

const root = ReactDOM.createRoot(document.getElementById('app'));
root.render(
    <React.StrictMode>
        <ErrorBoundary>
            <App />
        </ErrorBoundary>
    </React.StrictMode>
);
