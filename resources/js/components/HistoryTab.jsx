import React, { useState, useEffect } from 'react';

export default function HistoryTab({ onLoadHistory, onRefresh }) {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [currentPage, setCurrentPage] = useState(1);
    const [lastPage, setLastPage] = useState(1);

    const fetchHistory = async (page = 1) => {
        setLoading(true);
        try {
            const response = await fetch(`/api/scrape-history?page=${page}`);
            const result = await response.json();
            if (result.success) {
                setHistory(result.history.data || []);
                setCurrentPage(result.history.current_page);
                setLastPage(result.history.last_page);
            }
        } catch (error) {
            console.error('Error fetching history:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHistory();
    }, []);

    const handleDelete = async (id) => {
        if (!confirm('Hapus history ini?')) return;
        try {
            const response = await fetch(`/api/scrape-history/${id}`, {
                method: 'DELETE',
                headers: { 'Accept': 'application/json' },
            });
            const result = await response.json();
            if (result.success) {
                fetchHistory(currentPage);
            }
        } catch (error) {
            console.error('Error deleting history:', error);
        }
    };

    const handleLoad = (item) => {
        if (onLoadHistory) {
            onLoadHistory(item);
        }
    };

    const formatDate = (dateStr) => {
        return new Date(dateStr).toLocaleString('id-ID', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    if (loading) {
        return (
            <div className="tab-content active">
                <p className="info-text">Memuat history...</p>
            </div>
        );
    }

    if (!history || history.length === 0) {
        return (
            <div className="tab-content active">
                <p className="info-text">Belum ada history scraping</p>
            </div>
        );
    }

    return (
        <div className="tab-content active">
            <div className="history-list">
                {history.map((item) => (
                    <div key={item.id} className="history-item">
                        <div className="history-item-info">
                            <div className="history-item-keyword">
                                <span className="data-item-platform">{item.platform}</span>
                                {' '}{item.keyword}
                            </div>
                            <div className="history-item-meta">
                                <span><i className="fas fa-database"></i> {item.results_count} data</span>
                                <span><i className="fas fa-clock"></i> {formatDate(item.created_at)}</span>
                                {item.sentiment_summary && (
                                    <span className="sentiment-mini">
                                        <span className="sentiment-dot positive" title="Positif"></span>
                                        <span className="sentiment-dot neutral" title="Netral"></span>
                                        <span className="sentiment-dot negative" title="Negatif"></span>
                                    </span>
                                )}
                            </div>
                        </div>
                        <div className="history-item-actions">
                            <button
                                className="btn-load"
                                onClick={() => handleLoad(item)}
                                disabled={!item.raw_data || item.raw_data.length === 0}
                                title={!item.raw_data ? 'Data tidak tersedia' : 'Muat data'}
                            >
                                Muat
                            </button>
                            <button
                                className="btn-delete-history"
                                onClick={() => handleDelete(item.id)}
                            >
                                Hapus
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {lastPage > 1 && (
                <div className="pagination">
                    <button
                        className="btn-pagination"
                        disabled={currentPage <= 1}
                        onClick={() => fetchHistory(currentPage - 1)}
                    >
                        Sebelumnya
                    </button>
                    <span className="page-info">Halaman {currentPage} dari {lastPage}</span>
                    <button
                        className="btn-pagination"
                        disabled={currentPage >= lastPage}
                        onClick={() => fetchHistory(currentPage + 1)}
                    >
                        Selanjutnya
                    </button>
                </div>
            )}
        </div>
    );
}
