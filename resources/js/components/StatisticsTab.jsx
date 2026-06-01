import React from 'react';

function fmtK(n) {
    if (!n && n !== 0) return '—';
    if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M';
    if (n >= 1e3) return (n / 1e3).toFixed(1) + 'k';
    return String(n);
}

export default function StatisticsTab({ statistics }) {
    if (!statistics) {
        return (
            <div className="panel on">
                <div className="empty-state">
                    Statistik akan ditampilkan di sini
                </div>
            </div>
        );
    }

    return (
        <div className="panel on">
            <div className="stat-layout">
                {/* Engagement Summary */}
                <div>
                    <p className="srule">ringkasan engagement</p>
                    <div className="stat-row">
                        <div className="stat-cell">
                            <div className="stat-n">{fmtK(statistics.totalLikes)}</div>
                            <div className="stat-lbl">total likes</div>
                        </div>
                        <div className="stat-cell">
                            <div className="stat-n">{fmtK(statistics.totalComments)}</div>
                            <div className="stat-lbl">total komentar</div>
                        </div>
                        <div className="stat-cell">
                            <div className="stat-n">{fmtK(statistics.totalShares)}</div>
                            <div className="stat-lbl">total shares</div>
                        </div>
                    </div>
                </div>

                {/* Averages */}
                <div>
                    <p className="srule">rata-rata per post</p>
                    <div className="stat-row">
                        <div className="stat-cell">
                            <div className="stat-n">{statistics.avgLikes}</div>
                            <div className="stat-lbl">rata-rata likes</div>
                        </div>
                        <div className="stat-cell">
                            <div className="stat-n">{statistics.avgComments}</div>
                            <div className="stat-lbl">rata-rata komentar</div>
                        </div>
                        <div className="stat-cell">
                            <div className="stat-n">{statistics.avgShares}</div>
                            <div className="stat-lbl">rata-rata shares</div>
                        </div>
                    </div>
                </div>

                {/* Total */}
                <div>
                    <p className="srule">total</p>
                    <div className="stat-row">
                        <div className="stat-cell">
                            <div className="stat-n">{fmtK(statistics.totalLikes + statistics.totalComments + statistics.totalShares)}</div>
                            <div className="stat-lbl">total engagement</div>
                        </div>
                        <div className="stat-cell">
                            <div className="stat-n">{statistics.total}</div>
                            <div className="stat-lbl">total post</div>
                        </div>
                        <div className="stat-cell">
                            <div className="stat-n">—</div>
                            <div className="stat-lbl">platform</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
