import React, { useState, useEffect, useRef } from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Tooltip,
    Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

const RANGES = [
    { days: 7, label: '7 hari' },
    { days: 30, label: '30 hari' },
    { days: 90, label: '90 hari' },
];

const TREND_META = {
    improving: { label: 'membaik', cls: 'tr-up' },
    declining: { label: 'menurun', cls: 'tr-down' },
    stable: { label: 'stabil', cls: 'tr-flat' },
    'no-data': { label: 'belum ada data', cls: 'tr-none' },
};

// Canvas colors must be literal (Chart.js does not resolve CSS variables)
const LINE_COLORS = {
    positive: { border: '#2e7d32', fill: 'rgba(46,125,50,0.10)' },
    negative: { border: '#c62828', fill: 'rgba(198,40,40,0.10)' },
    neutral: { border: '#8d8678', fill: 'rgba(141,134,120,0.10)' },
};

export default function TrendPanel({ currentKeyword }) {
    const [keyword, setKeyword] = useState(currentKeyword || '');
    const [days, setDays] = useState(30);
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [loadedKeyword, setLoadedKeyword] = useState('');
    const didAutoLoad = useRef(false);

    // Keep the input in sync with the currently searched keyword
    useEffect(() => {
        if (currentKeyword) setKeyword(currentKeyword);
    }, [currentKeyword]);

    // Clear stale results whenever the input no longer matches the loaded
    // keyword, so a changed keyword never shows the previous keyword's chart.
    useEffect(() => {
        if (
            loadedKeyword &&
            keyword.trim().toLowerCase() !== loadedKeyword.toLowerCase()
        ) {
            setData(null);
            setError('');
        }
    }, [keyword, loadedKeyword]);

    // Auto-load once the user actually searched something
    useEffect(() => {
        if (currentKeyword && !didAutoLoad.current) {
            didAutoLoad.current = true;
            load(currentKeyword, days);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [currentKeyword]);

    const load = async (kw, d) => {
        const k = (kw || '').trim();
        if (!k) {
            setError('Masukkan keyword terlebih dahulu.');
            return;
        }
        setLoading(true);
        setError('');
        try {
            const res = await fetch(
                `/api/trend?keyword=${encodeURIComponent(k)}&days=${d}`,
                {
                    headers: { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
                },
            );
            const json = await res.json();
            if (!res.ok || !json.success) {
                setError(json.error || 'Gagal memuat tren.');
                return;
            }
            setLoadedKeyword(json.keyword || k.toLowerCase());
            setData(json);
        } catch (e) {
            console.error('Trend error:', e);
            setError('Gagal terhubung ke server.');
        } finally {
            setLoading(false);
        }
    };

    const chartData = data
        ? {
            labels: data.points.map(p => p.date),
            datasets: ['positive', 'negative', 'neutral'].map(key => ({
                label: key === 'positive' ? 'Positif' : key === 'negative' ? 'Negatif' : 'Netral',
                data: data.points.map(p => p[key]),
                borderColor: LINE_COLORS[key].border,
                backgroundColor: LINE_COLORS[key].fill,
                fill: true,
                tension: 0.3,
                pointRadius: 3,
                pointHoverRadius: 5,
                borderWidth: 2,
            })),
        }
        : null;

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: '#8a8272', font: { family: "'Playfair Display', serif", size: 11 } } },
        },
        scales: {
            x: { ticks: { color: '#8a8272', font: { family: "'Playfair Display', serif", size: 10 } } },
            y: { beginAtZero: true, ticks: { precision: 0, color: '#a89e8a' } },
        },
    };

    const meta = data ? TREND_META[data.summary.trend] || TREND_META['no-data'] : null;

    return (
        <section className="tr" aria-label="Trend sentimen keyword">
            <div className="cmp-head">
                <h2 className="cmp-title">Trend Sentimen</h2>
                <p className="cmp-sub">Perkembangan sentimen sebuah keyword dari waktu ke waktu</p>
            </div>

            <div className="tr-controls">
                <input
                    className="cmp-input tr-input"
                    type="text"
                    value={keyword}
                    placeholder="Keyword (contoh: harga bbm)"
                    onChange={e => setKeyword(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') load(keyword, days); }}
                />
                <div className="tr-ranges">
                    {RANGES.map(r => (
                        <button
                            key={r.days}
                            className={`tr-range ${days === r.days ? 'on' : ''}`}
                            onClick={() => { setDays(r.days); load(keyword, r.days); }}
                        >
                            {r.label}
                        </button>
                    ))}
                </div>
                <button className="cmp-run" onClick={() => load(keyword, days)} disabled={loading}>
                    {loading ? 'Memuat...' : 'Lihat Tren'}
                </button>
            </div>

            {error && <div className="cmp-err">{error}</div>}

            {data && (
                <div className="tr-result">
                    {data.total_snapshots === 0 ? (
                        <div className="tr-empty">
                            <p>Belum ada data tren untuk "{data.keyword}".</p>
                            <p className="tr-empty-sub">
                                Lakukan <strong>scrape</strong> atau <strong>surf</strong> dengan keyword ini
                                beberapa kali (pada hari berbeda) — setiap analisis sentimen otomatis tercatat
                                sebagai titik tren.
                            </p>
                        </div>
                    ) : (
                        <>
                            <div className="tr-stats">
                                <div className="tr-stat">
                                    <span className="tr-stat-num">{data.total_snapshots}</span>
                                    <span className="tr-stat-label">titik data</span>
                                </div>
                                <div className="tr-stat">
                                    <span className="tr-stat-num">{data.summary.total_results}</span>
                                    <span className="tr-stat-label">total hasil</span>
                                </div>
                                <div className="tr-stat">
                                    <span className="tr-stat-num">{data.summary.avg_positive_pct}%</span>
                                    <span className="tr-stat-label">rata-rata positif</span>
                                </div>
                                <div className={`tr-stat tr-trend ${meta.cls}`}>
                                    <span className="tr-stat-num">{meta.label}</span>
                                    <span className="tr-stat-label">
                                        tren {data.summary.positive_delta > 0 ? `+${data.summary.positive_delta}%` : `${data.summary.positive_delta}%`}
                                    </span>
                                </div>
                            </div>

                            <div className="tr-chart-wrap">
                                <Line data={chartData} options={chartOptions} />
                            </div>
                        </>
                    )}
                </div>
            )}
        </section>
    );
}
