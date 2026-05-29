import React from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

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

    const totalData = {
        labels: ['Likes', 'Comments', 'Shares'],
        datasets: [{
            label: 'Total',
            data: [statistics.totalLikes, statistics.totalComments, statistics.totalShares],
            backgroundColor: ['#667eea', '#764ba2', '#10b981'],
            borderRadius: 6,
        }],
    };

    const avgData = {
        labels: ['Avg Likes', 'Avg Comments', 'Avg Shares'],
        datasets: [{
            label: 'Rata-rata',
            data: [statistics.avgLikes, statistics.avgComments, statistics.avgShares],
            backgroundColor: ['#667eea', '#764ba2', '#10b981'],
            borderRadius: 6,
        }],
    };

    const barOptions = {
        responsive: true,
        plugins: {
            legend: { display: false },
        },
        scales: {
            y: { beginAtZero: true },
        },
    };

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

            <div className="charts-row">
                <div className="chart-container">
                    <h3 className="chart-title">Total Engagement</h3>
                    <Bar data={totalData} options={barOptions} />
                </div>
                <div className="chart-container">
                    <h3 className="chart-title">Rata-rata Engagement</h3>
                    <Bar data={avgData} options={barOptions} />
                </div>
            </div>
        </div>
    );
}
