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

    const pos = analysis.positive || analysis.summary?.positive || 0;
    const neg = analysis.negative || analysis.summary?.negative || 0;
    const neu = analysis.neutral || analysis.summary?.neutral || 0;
    const tot = pos + neg + neu;
    const pct = analysis.percentage || analysis.summary?.percentage || {};
    const posP = pct.positive || Math.round(pos / tot * 100) || 0;
    const negP = pct.negative || Math.round(neg / tot * 100) || 0;
    const neuP = 100 - posP - negP;

    // LLM-specific fields
    const aiAnalysis = analysis.analysis || null;
    const keyInsights = analysis.key_insights || [];
    const dominantEmotion = analysis.dominant_emotion || null;
    const overallSentiment = analysis.summary?.overall || (pos > neg ? 'positive' : neg > pos ? 'negative' : 'neutral');
    const overallConfidence = analysis.summary?.overall_confidence || null;

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

    const getEmotionEmoji = (emotion) => {
        if (!emotion) return '';
        const e = emotion.toLowerCase();
        if (e.includes('antusias') || e.includes('excited') || e.includes('senang')) return '🔥';
        if (e.includes('khawatir') || e.includes('cemas') || e.includes('worried')) return '😟';
        if (e.includes('harap') || e.includes('hope') || e.includes('optimis')) return '✨';
        if (e.includes('kecewa') || e.includes('disappointed') || e.includes('frustrasi')) return '😞';
        if (e.includes('marah') || e.includes('angry') || e.includes('kesal')) return '😠';
        if (e.includes('netral') || e.includes('neutral') || e.includes('objektif')) return '⚖️';
        return '📊';
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

    // Keyword detection from details
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

                    {/* Overall Sentiment Summary */}
                    <div className="pq">
                        <p>
                            {getEmotionEmoji(dominantEmotion)} Komunitas {pos > neg ? 'antusias' : neg > pos ? 'kritis' : 'netral'} — sentimen {getSentimentLabel(overallSentiment).toLowerCase()} mendominasi {pos > neg ? posP : neg > pos ? negP : neuP}% dari total data.
                            {dominantEmotion && ` Emosi dominan: ${dominantEmotion}.`}
                        </p>
                        <cite>
                            {aiAnalysis ? 'MiMo v2.5 Pro · AI Sentiment Analysis' : 'Keyword Matching · Fallback'}
                            {overallConfidence && ` · Confidence: ${overallConfidence}%`}
                        </cite>
                    </div>

                    {/* Sentiment Numbers */}
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

                    {/* AI Analysis Section */}
                    {aiAnalysis && (
                        <div style={{ marginBottom: '18px' }}>
                            <p className="srule">analisis AI</p>
                            <div style={{
                                padding: '14px 16px',
                                background: 'var(--color-surface)',
                                border: '0.5px solid var(--color-border-secondary)',
                                fontSize: '13px',
                                lineHeight: '1.6',
                                fontFamily: "'Playfair Display', serif",
                            }}>
                                {aiAnalysis}
                            </div>
                        </div>
                    )}

                    {/* Key Insights */}
                    {keyInsights.length > 0 && (
                        <div style={{ marginBottom: '18px' }}>
                            <p className="srule">insight utama</p>
                            <div className="post-list">
                                {keyInsights.map((insight, index) => (
                                    <div key={index} className="post-row" style={{ gridTemplateColumns: '18px 1fr' }}>
                                        <div style={{
                                            fontFamily: "'Playfair Display', serif",
                                            fontSize: '16px',
                                            fontWeight: 700,
                                            color: 'var(--color-text-faded)',
                                        }}>
                                            {index + 1}
                                        </div>
                                        <div className="post-text" style={{ fontSize: '12px' }}>{insight}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Detailed Results */}
                    <p className="srule">data mentah · {details.length} item</p>
                    <div className="post-list">
                        {details.map((item, index) => (
                            <div key={index} className="post-row">
                                <div>
                                    <div className="post-text">{item.text}</div>
                                    <div className="post-by">
                                        <span style={{ color: item.sentiment === 'positive' ? 'var(--color-positive)' : item.sentiment === 'negative' ? 'var(--color-negative)' : 'var(--color-neutral)', fontWeight: 500 }}>
                                            {getSentimentLabel(item.sentiment)}
                                        </span>
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

                    {/* Dominant Emotion */}
                    {dominantEmotion && (
                        <div className="side-block">
                            <p className="side-head">Emosi dominan</p>
                            <div style={{
                                padding: '10px 12px',
                                background: 'var(--color-surface)',
                                border: '0.5px solid var(--color-border-secondary)',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                            }}>
                                <span style={{ fontSize: '20px' }}>{getEmotionEmoji(dominantEmotion)}</span>
                                <span style={{
                                    fontFamily: "'Playfair Display', serif",
                                    fontSize: '14px',
                                    fontWeight: 700,
                                    textTransform: 'capitalize',
                                }}>
                                    {dominantEmotion}
                                </span>
                            </div>
                        </div>
                    )}

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

                    {/* AI Model Info */}
                    {aiAnalysis && (
                        <div className="side-block">
                            <p className="side-head">Model AI</p>
                            <div style={{
                                padding: '8px 10px',
                                background: 'var(--color-surface)',
                                border: '0.5px solid var(--color-border-secondary)',
                                fontSize: '10px',
                                color: 'var(--color-text-secondary)',
                            }}>
                                <div style={{ fontWeight: 500, marginBottom: '2px' }}>MiMo v2.5 Pro</div>
                                <div>LLM Sentiment Analysis</div>
                                {overallConfidence && <div>Overall Confidence: {overallConfidence}%</div>}
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
