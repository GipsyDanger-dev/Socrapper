import React from 'react';

export default function SentimentTab({ analysis, data, currentKeyword, onExport }) {
    if (!analysis) {
        return (
            <div className="panel on">
                <div className="empty-state">
                    Hasil analisis sentimen akan ditampilkan di sini
                </div>
            </div>
        );
    }

    const pos = analysis.positive || 0;
    const neg = analysis.negative || 0;
    const neu = analysis.neutral || 0;
    const tot = pos + neg + neu;
    const posP = analysis.percentage?.positive || Math.round(pos / tot * 100) || 0;
    const negP = analysis.percentage?.negative || Math.round(neg / tot * 100) || 0;
    const neuP = 100 - posP - negP;

    const getSentimentClass = (s) => {
        if (s === 'positive') return 'pos';
        if (s === 'negative') return 'neg';
        return 'neu';
    };

    const getSentimentLabel = (s) => {
        if (s === 'positive') return 'Positif';
        if (s === 'negative') return 'Negatif';
        return 'Netral';
    };

    // Platform breakdown from data
    const platformMap = {};
    if (data) {
        data.forEach(item => {
            const p = item.platform || 'Unknown';
            platformMap[p] = (platformMap[p] || 0) + 1;
        });
    }
    const platforms = Object.entries(platformMap).sort((a, b) => b[1] - a[1]).slice(0, 5);
    const maxPl = platforms[0]?.[1] || 1;

    // Keyword detection from details (supports both LLM and keyword-based formats)
    const details = analysis.results || analysis.details || [];
    const allText = details.map(d => d.text?.toLowerCase() || '').join(' ');
    const posKw = ['bagus', 'mantap', 'great', 'amazing', 'inovatif', 'helpful', 'keren', 'mudah', 'positif', 'berkembang'].filter(k => allText.includes(k));
    const negKw = ['kurang', 'kendala', 'gagal', 'susah', 'mengecewakan', 'frustrasi', 'buruk', 'negatif'].filter(k => allText.includes(k));

    return (
        <div className="panel on">
            <div className="sl">
                <div className="sm">
                    <div className="bnum">{tot}</div>
                    <div className="blbl">total post dikumpulkan</div>

                    <div className="pq">
                        <p>
                            Komunitas {pos > neg ? 'antusias' : 'kritis'} — sentimen {pos > neg ? 'positif' : 'negatif'} mendominasi {pos > neg ? posP : negP}% dari total data.
                        </p>
                        <cite>SentimentAnalysisService · keyword matching</cite>
                    </div>

                    <div className="tc">
                        <div className="cell">
                            <div className="cn pos">{pos}</div>
                            <div className="clbl">positif</div>
                        </div>
                        <div className="cell">
                            <div className="cn neg">{neg}</div>
                            <div className="clbl">negatif</div>
                        </div>
                        <div className="cell">
                            <div className="cn neu">{neu}</div>
                            <div className="clbl">netral</div>
                        </div>
                    </div>

                    <p className="srule">data mentah · {Math.min(details.length, 5)} teratas</p>
                    <div className="post-list">
                        {details.slice(0, 5).map((item, index) => (
                            <div key={index} className="post-row">
                                <div>
                                    <div className="post-text">{item.text}</div>
                                    <div className="post-by">
                                        {getSentimentLabel(item.sentiment)}
                                        {item.confidence ? ` · ${item.confidence}% confidence` : ''}
                                        {item.reason ? ` · ${item.reason}` : ''}
                                    </div>
                                </div>
                                <div className={`pip ${getSentimentClass(item.sentiment)}`}>
                                    {item.sentiment?.slice(0, 3) || 'n/a'}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="ss">
                    {/* Sentiment Distribution */}
                    <div className="side-block">
                        <p className="side-head">Distribusi sentimen</p>
                        <div className="bar-block">
                            <div className="bar-meta">
                                <span className="bar-name">positif</span>
                                <span className="bar-pct">{posP}%</span>
                            </div>
                            <div className="bar-track">
                                <div className="bar-fill pos" style={{ width: `${posP}%` }}></div>
                            </div>
                        </div>
                        <div className="bar-block">
                            <div className="bar-meta">
                                <span className="bar-name">negatif</span>
                                <span className="bar-pct">{negP}%</span>
                            </div>
                            <div className="bar-track">
                                <div className="bar-fill neg" style={{ width: `${negP}%` }}></div>
                            </div>
                        </div>
                        <div className="bar-block">
                            <div className="bar-meta">
                                <span className="bar-name">netral</span>
                                <span className="bar-pct">{neuP}%</span>
                            </div>
                            <div className="bar-track">
                                <div className="bar-fill" style={{ width: `${neuP}%` }}></div>
                            </div>
                        </div>
                    </div>

                    {/* Platform Breakdown */}
                    {platforms.length > 0 && (
                        <div className="side-block">
                            <p className="side-head">Platform</p>
                            <div className="plat-rows">
                                {platforms.map(([name, count]) => (
                                    <div key={name} className="plat-row">
                                        <span className="plat-row-name">{name}</span>
                                        <div className="plat-row-bar">
                                            <div className="plat-row-fill" style={{ width: `${Math.round(count / maxPl * 100)}%` }}></div>
                                        </div>
                                        <span className="plat-row-n">{count}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Keywords */}
                    {(posKw.length > 0 || negKw.length > 0) && (
                        <div className="side-block">
                            <p className="side-head">Keyword terdeteksi</p>
                            <div className="kw-cloud">
                                {posKw.map(k => <span key={k} className="kw pos">{k}</span>)}
                                {negKw.map(k => <span key={k} className="kw neg">{k}</span>)}
                            </div>
                        </div>
                    )}

                    {/* Export */}
                    <div className="exp-row">
                        <span className="exp-note">{tot} baris · UTF-8</span>
                        <button className="exp-btn" onClick={onExport}>↓ CSV</button>
                    </div>
                </div>
            </div>
        </div>
    );
}
