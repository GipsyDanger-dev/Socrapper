import React, { useState } from 'react';

const PAGE_SIZE = 5;

function fmtK(n) {
    if (!n) return '—';
    if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M';
    if (n >= 1e3) return (n / 1e3).toFixed(1) + 'k';
    return String(n);
}

const cleanHtml = (t) => {
    if (!t) return '';
    return String(t)
        .replace(/<[^>]*>/g, ' ')
        .replace(/&nbsp;/g, ' ')
        .replace(/&amp;/g, '&')
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&quot;/g, '"')
        .replace(/&#39;/g, "'")
        .replace(/\s+/g, ' ')
        .trim();
};

export default function RawDataTab({ data, onExport }) {
    const [page, setPage] = useState(0);

    if (!data || data.length === 0) {
        return (
            <div className="panel on">
                <div className="empty-state">
                    Hasil scraping akan ditampilkan di sini
                </div>
            </div>
        );
    }

    const totalPages = Math.ceil(data.length / PAGE_SIZE);
    const slice = data.slice(page * PAGE_SIZE, page * PAGE_SIZE + PAGE_SIZE);

    const getSentimentClass = (item) => {
        const s = item.sentiment || '';
        if (s === 'positive' || s === 'positif') return 'positif';
        if (s === 'negative' || s === 'negatif') return 'negatif';
        return 'netral';
    };

    return (
        <div className="panel on">
            <table className="raw-table">
                <thead>
                    <tr>
                        <th>Konten</th>
                        <th>Platform</th>
                        <th>Sentimen</th>
                        <th>Skor</th>
                        <th>Engagement</th>
                    </tr>
                </thead>
                <tbody>
                    {slice.map((item, index) => {
                        const sentClass = getSentimentClass(item);
                        const score = item.sentiment_score || item.score || 0;
                        return (
                            <tr key={index}>
                                <td>
                                    <div className="raw-content" style={{ whiteSpace: 'pre-line' }}>{cleanHtml(item.text)}</div>
                                    <div className="raw-date">
                                        {item.timestamp
                                            ? new Date(item.timestamp).toLocaleString('id-ID')
                                            : item.date || ''
                                        }
                                    </div>
                                    {item.url && (
                                        <a
                                            href={item.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="raw-source-link"
                                        >
                                            buka sumber →
                                        </a>
                                    )}
                                </td>
                                <td><span className="plat-tag">{item.platform}</span></td>
                                <td>
                                    <span className={`sent-badge ${sentClass}`}>
                                        {item.sentiment || 'netral'}
                                    </span>
                                </td>
                                <td>
                                    <div className="score-wrap">
                                        <div className="score-bar">
                                            <div
                                                className={`score-fill ${sentClass}`}
                                                style={{ width: `${Math.round(score * 100)}%` }}
                                            ></div>
                                        </div>
                                        <span className="score-val">{typeof score === 'number' ? score.toFixed(2) : score}</span>
                                    </div>
                                </td>
                                <td>
                                    <span className="eng-val">
                                        ♥ {fmtK(item.likes)} · ✎ {fmtK(item.comments)}
                                    </span>
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>

            <div className="raw-footer">
                <span className="page-info">
                    hal. {page + 1} / {totalPages} · {data.length} total
                </span>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <div className="page-btns">
                        <button
                            className="page-btn"
                            disabled={page === 0}
                            onClick={() => setPage(p => p - 1)}
                        >
                            ←
                        </button>
                        <button
                            className="page-btn"
                            disabled={page >= totalPages - 1}
                            onClick={() => setPage(p => p + 1)}
                        >
                            →
                        </button>
                    </div>
                    <button className="exp-btn" onClick={onExport}>↓ CSV</button>
                </div>
            </div>
        </div>
    );
}
