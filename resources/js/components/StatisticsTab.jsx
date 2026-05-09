import React from 'react';

export default function StatisticsTab({ statistics }) {
    if (!statistics) {
        return (
            <div id="statistics" className="tab-content active">
                <div className="stats-container">
                    <p className="info-text">Statistik akan ditampilkan di sini</p>
                </div>
            </div>
        );
    }

    return (
        <div id="statistics" className="tab-content active">
            <div className="stats-container">
                <div className="stat-card">
                    <div className="stat-card-value">{statistics.total}</div>
                    <div className="stat-card-label">Total Postingan</div>
                </div>
                <div className="stat-card">
                    <div className="stat-card-value">{statistics.totalLikes}</div>
                    <div className="stat-card-label">Total Likes</div>
                </div>
                <div className="stat-card">
                    <div className="stat-card-value">{statistics.totalComments}</div>
                    <div className="stat-card-label">Total Comments</div>
                </div>
                <div className="stat-card">
                    <div className="stat-card-value">{statistics.totalShares}</div>
                    <div className="stat-card-label">Total Shares</div>
                </div>
                <div className="stat-card">
                    <div className="stat-card-value">{statistics.avgLikes}</div>
                    <div className="stat-card-label">Rata-rata Likes</div>
                </div>
                <div className="stat-card">
                    <div className="stat-card-value">{statistics.avgComments}</div>
                    <div className="stat-card-label">Rata-rata Comments</div>
                </div>
            </div>
        </div>
    );
}
