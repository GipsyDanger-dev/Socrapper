import React, { useState } from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Tooltip,
    Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const SENTIMENT_COLORS = { positive: '#2e7d32', negative: '#c62828', neutral: '#8d8678' };
const SENTIMENT_LABELS = { positive: 'positif', negative: 'negatif', neutral: 'netral' };

export default function ComparePanel() {
    const [queries, setQueries] = useState(['', '']);
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const update = (i, value) => setQueries(qs => qs.map((q, idx) => (idx === i ? value : q)));
    const addRow = () => { if (queries.length < 4) setQueries([...queries, '']); };
    const removeRow = i => { if (queries.length > 2) setQueries(qs => qs.filter((_, idx) => idx !== i)); };

    const run = async () => {
        const list = queries.map(q => q.trim()).filter(Boolean);
        if (list.length < 2) {
            setError('Minimal 2 keyword untuk dibandingkan.');
            return;
        }
        setLoading(true);
        setError('');
        setResults(null);
        try {
            const response = await fetch('/api/surf/compare', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify({ queries: list }),
            });
            const data = await response.json();
            if (!response.ok || !data.success) {
                setError(data.error || 'Gagal membandingkan keyword.');
                return;
            }
            setResults(data.comparisons);
        } catch (e) {
            console.error('Compare error:', e);
            setError('Gagal terhubung ke server.');
        } finally {
            setLoading(false);
        }
    };

    const chartData = results
        ? {
            labels: results.map(r => r.query),
            datasets: ['positive', 'negative', 'neutral'].map(key => ({
                label: SENTIMENT_LABELS[key],
                data: results.map(r => (r.sentiment || {})[key] || 0),
                backgroundColor: SENTIMENT_COLORS[key],
                borderRadius: 3,
            })),
        }
        : null;

    // Chart.js paints on <canvas> — CSS variables do not resolve reliably
    // there, so use literal hex colors (dark-theme friendly neutrals).
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: '#8a8272', font: { family: "'Playfair Display', serif", size: 11 } } },
        },
        scales: {
            x: { ticks: { color: '#8a8272', font: { family: "'Playfair Display', serif", size: 11 } } },
            y: { beginAtZero: true, ticks: { precision: 0, color: '#a89e8a' } },
        },
    };

    return (
        <section className="cmp" aria-label="Bandingkan keyword">
            <div className="cmp-head">
                <h2 className="cmp-title">Bandingkan Keyword</h2>
                <p className="cmp-sub">Bandingkan sentimen 2–4 keyword sekaligus</p>
            </div>

            <div className="cmp-inputs">
                {queries.map((q, i) => (
                    <div className="cmp-row" key={i}>
                        <input
                            className="cmp-input"
                            type="text"
                            value={q}
                            placeholder={`Keyword ${i + 1}`}
                            onChange={e => update(i, e.target.value)}
                            onKeyDown={e => { if (e.key === 'Enter') run(); }}
                        />
                        {queries.length > 2 && (
                            <button className="cmp-x" onClick={() => removeRow(i)} aria-label={`Hapus keyword ${i + 1}`}>×</button>
                        )}
                    </div>
                ))}
            </div>

            <div className="cmp-actions">
                {queries.length < 4 && (
                    <button className="cmp-add" onClick={addRow}>+ Tambah keyword</button>
                )}
                <button className="cmp-run" onClick={run} disabled={loading}>
                    {loading ? 'Membandingkan...' : 'Bandingkan →'}
                </button>
            </div>

            {error && <div className="cmp-err">{error}</div>}

            {results && results.length > 0 && (
                <div className="cmp-result">
                    <div className="cmp-chart-wrap">
                        <Bar data={chartData} options={chartOptions} />
                    </div>

                    <div className="cmp-grid">
                        {results.map(r => {
                            const s = r.sentiment || {};
                            const total = s.positive + s.negative + s.neutral || 0;
                            const pct = k => (total > 0 ? Math.round((s[k] / total) * 100) : 0);
                            return (
                                <div className="cmp-card" key={r.query}>
                                    <div className="cmp-card-query">"{r.query}"</div>
                                    <div className="cmp-card-stats">
                                        <span className="cmp-card-total">{r.total} hasil</span>
                                        <span className={`cmp-dom cmp-dom-${s.overall || 'neutral'}`}>
                                            dominan {SENTIMENT_LABELS[s.overall] || s.overall}
                                        </span>
                                    </div>
                                    <div className="cmp-bars">
                                        {['positive', 'negative', 'neutral'].map(k => (
                                            <div className="cmp-bar" key={k}>
                                                <span className="cmp-bar-label">{SENTIMENT_LABELS[k]}</span>
                                                <div className="cmp-bar-track">
                                                    <div
                                                        className="cmp-bar-fill"
                                                        style={{ width: `${pct(k)}%`, background: SENTIMENT_COLORS[k] }}
                                                    />
                                                </div>
                                                <span className="cmp-bar-val">{s[k]}</span>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="cmp-card-topics">
                                        <span className="cmp-card-h">Topik:</span>{' '}
                                        {(r.top_topics || []).slice(0, 5).join(' · ') || '—'}
                                    </div>
                                    <div className="cmp-card-sources">
                                        <span className="cmp-card-h">Sumber:</span>{' '}
                                        {(r.top_sources || []).map(s => s.source).slice(0, 4).join(' · ') || '—'}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </section>
    );
}
