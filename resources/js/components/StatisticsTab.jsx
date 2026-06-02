import React from 'react';

function fmtK(n) {
    if (!n && n !== 0) return '—';
    if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M';
    if (n >= 1e3) return (n / 1e3).toFixed(1) + 'k';
    return String(n);
}

export default function StatisticsTab({ statistics, platform }) {
    if (!statistics) {
        return (
            <div className="panel on">
                <div className="empty-state">
                    Statistik akan ditampilkan di sini
                </div>
            </div>
        );
    }

    const hasEngagement = statistics.totalLikes > 0 || statistics.totalComments > 0 || statistics.totalShares > 0;
    const platformName = platform || Object.keys(statistics.platforms || {}).join(', ') || '—';
    const platformBreakdown = statistics.platforms || {};

    return (
        <div className="panel on">
            <div className="stat-layout">
                {/* Overview */}
                <div>
                    <p className="srule">ringkasan</p>
                    <div className="stat-row">
                        <div className="stat-cell">
                            <div className="stat-n">{statistics.total}</div>
                            <div className="stat-lbl">total post</div>
                        </div>
                        <div className="stat-cell">
                            <div className="stat-n">{fmtK(statistics.uniqueSources)}</div>
                            <div className="stat-lbl">sumber unik</div>
                        </div>
                        <div className="stat-cell">
                            <div className="stat-n">{fmtK(statistics.totalWords)}</div>
                            <div className="stat-lbl">total kata</div>
                        </div>
                        <div className="stat-cell">
                            <div className="stat-n">{statistics.avgWords || '—'}</div>
                            <div className="stat-lbl">rata kata/post</div>
                        </div>
                    </div>
                </div>

                {/* Sentiment */}
                <div>
                    <p className="srule">distribusi sentimen</p>
                    <div className="stat-row">
                        <div className="stat-cell">
                            <div className="stat-n" style={{ color: 'var(--color-positive)' }}>{statistics.sentiments?.positive || 0}</div>
                            <div className="stat-lbl">positif</div>
                        </div>
                        <div className="stat-cell">
                            <div className="stat-n" style={{ color: 'var(--color-negative)' }}>{statistics.sentiments?.negative || 0}</div>
                            <div className="stat-lbl">negatif</div>
                        </div>
                        <div className="stat-cell">
                            <div className="stat-n" style={{ color: 'var(--color-neutral)' }}>{statistics.sentiments?.neutral || 0}</div>
                            <div className="stat-lbl">netral</div>
                        </div>
                    </div>
                    {statistics.total > 0 && (
                        <div className="stat-bar-wrap">
                            <div
                                className="stat-bar-segment"
                                style={{
                                    width: `${((statistics.sentiments?.positive || 0) / statistics.total) * 100}%`,
                                    background: 'var(--color-positive)',
                                }}
                            />
                            <div
                                className="stat-bar-segment"
                                style={{
                                    width: `${((statistics.sentiments?.neutral || 0) / statistics.total) * 100}%`,
                                    background: 'var(--color-neutral)',
                                }}
                            />
                            <div
                                className="stat-bar-segment"
                                style={{
                                    width: `${((statistics.sentiments?.negative || 0) / statistics.total) * 100}%`,
                                    background: 'var(--color-negative)',
                                }}
                            />
                        </div>
                    )}
                </div>

                {/* Platform */}
                {Object.keys(platformBreakdown).length > 0 && (
                    <div>
                        <p className="srule">platform</p>
                        <div className="stat-platform-list">
                            {Object.entries(platformBreakdown)
                                .sort((a, b) => b[1] - a[1])
                                .map(([name, count]) => (
                                    <div key={name} className="stat-platform-item">
                                        <span className="plat-tag">{name}</span>
                                        <span className="stat-platform-count">{count} post</span>
                                    </div>
                                ))
                            }
                        </div>
                    </div>
                )}

                {/* Engagement */}
                {hasEngagement && (
                    <div>
                        <p className="srule">engagement</p>
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
                )}
            </div>
        </div>
    );
}
