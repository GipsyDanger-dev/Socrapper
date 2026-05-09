import React from 'react';

export default function LoadingIndicator({ show }) {
    if (!show) return null;

    return (
        <div className="loading-indicator">
            <div className="spinner"></div>
            <p>Sedang memproses...</p>
        </div>
    );
}
