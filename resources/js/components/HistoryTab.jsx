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
            <div className="panel on">
                <div className="empty-state">Memuat history...</div>
            </div>
        );
    }

    if (!history || history.length === 0) {
        return (
            <div className="panel on">
                <div className="empty-state">Belum ada history scraping</div>
            </div>
        );
    }

    return (
        <div className="panel on">
            <div>
                {history.map((item) => (
                    <div key={item.id} className="history-item">
                        <div className="history-info">
                            <div className="history-keyword">
                                <span className="plat-tag" style={{ marginRight: '6px' }}>{item.platform}</span>
                                {item.keyword}
                            </div>
                            <div className="history-meta">
                                {item.results_count} data · {formatDate(item.created_at)}
                            </div>
                        </div>
                        <div className="history-actions">
                            <button
                                className="btn-sm"
                                onClick={() => handleLoad(item)}
                                disabled={!item.raw_data || item.raw_data.length === 0}
                            >
                                Muat
                            </button>
                            <button
                                className="btn-sm danger"
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
                        className="btn-sm"
                        disabled={currentPage <= 1}
                        onClick={() => fetchHistory(currentPage - 1)}
                    >
                        ←
                    </button>
                    <span className="page-info">Halaman {currentPage} dari {lastPage}</span>
                    <button
                        className="btn-sm"
                        disabled={currentPage >= lastPage}
                        onClick={() => fetchHistory(currentPage + 1)}
                    >
                        →
                    </button>
                </div>
            )}
        </div>
    );
}
