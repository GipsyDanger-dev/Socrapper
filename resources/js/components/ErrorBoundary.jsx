import React from 'react';

export default class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error('ErrorBoundary caught:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minHeight: '100vh',
                    padding: '40px',
                    fontFamily: "'Playfair Display', serif",
                    background: 'var(--color-bg, #faf9f6)',
                    color: 'var(--color-text, #1a1a1a)',
                }}>
                    <h1 style={{ fontSize: '24px', marginBottom: '12px' }}>Terjadi Kesalahan</h1>
                    <p style={{ fontSize: '14px', color: 'var(--color-text-secondary, #666)', marginBottom: '24px', textAlign: 'center', maxWidth: '480px' }}>
                        Aplikasi mengalami error tak terduga. Silakan refresh halaman atau hubungi admin.
                    </p>
                    <pre style={{
                        fontSize: '11px',
                        padding: '12px 16px',
                        background: 'var(--color-surface, #f0f0f0)',
                        border: '0.5px solid var(--color-border-secondary, #ddd)',
                        maxWidth: '600px',
                        overflow: 'auto',
                        whiteSpace: 'pre-wrap',
                        marginBottom: '24px',
                    }}>
                        {this.state.error?.message || 'Unknown error'}
                    </pre>
                    <button
                        onClick={() => window.location.reload()}
                        style={{
                            padding: '10px 24px',
                            fontSize: '13px',
                            fontFamily: "'Playfair Display', serif",
                            background: 'var(--color-text, #1a1a1a)',
                            color: 'var(--color-bg, #faf9f6)',
                            border: 'none',
                            cursor: 'pointer',
                        }}
                    >
                        Refresh Halaman
                    </button>
                </div>
            );
        }
        return this.props.children;
    }
}
