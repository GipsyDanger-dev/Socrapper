import React from 'react';

export default function AiAnalysisCard({ analysis }) {
    if (!analysis) return null;

    const getSentimentColor = (sentiment) => {
        if (!sentiment) return 'var(--color-neutral)';
        const s = (sentiment.overall || sentiment).toLowerCase();
        if (s === 'bullish' || s === 'positive') return 'var(--color-positive)';
        if (s === 'bearish' || s === 'negative') return 'var(--color-negative)';
        return 'var(--color-neutral)';
    };

    const getSentimentLabel = (sentiment) => {
        if (!sentiment) return 'NETRAL';
        const s = (sentiment.overall || sentiment).toLowerCase();
        if (s === 'bullish' || s === 'positive') return 'POSITIF';
        if (s === 'bearish' || s === 'negative') return 'NEGATIF';
        return 'NETRAL';
    };

    return (
        <div style={{ marginTop: '16px' }}>
            {/* Sentiment Overview */}
            {analysis.sentiment && (
                <div className="tc" style={{ marginBottom: '16px' }}>
                    <div className="cell">
                        <div className="cn" style={{ color: getSentimentColor(analysis.sentiment) }}>
                            {getSentimentLabel(analysis.sentiment)}
                        </div>
                        <div className="clbl">sentimen</div>
                    </div>
                    <div className="cell">
                        <div className="cn">
                            {analysis.sentiment.confidence !== undefined ? `${analysis.sentiment.confidence}%` : '—'}
                        </div>
                        <div className="clbl">confidence</div>
                    </div>
                    <div className="cell">
                        <div className="cn">
                            {analysis.sentiment.score !== undefined
                                ? (analysis.sentiment.score > 0 ? '+' : '') + analysis.sentiment.score
                                : '—'
                            }
                        </div>
                        <div className="clbl">skor</div>
                    </div>
                </div>
            )}

            {/* Summary */}
            {(analysis.summary || analysis.analysis) && (
                <div className="pq">
                    <p>{analysis.summary || analysis.analysis}</p>
                    <cite>AI Analysis · {analysis.model || 'LLM'}</cite>
                </div>
            )}

            {/* Key Points */}
            {(analysis.key_points || analysis.key_findings) && (analysis.key_points || analysis.key_findings).length > 0 && (
                <div style={{ marginBottom: '16px' }}>
                    <p className="srule">poin utama</p>
                    <div className="post-list">
                        {(analysis.key_points || analysis.key_findings).map((point, i) => (
                            <div key={i} className="post-row">
                                <div className="post-text" style={{ fontSize: '12px' }}>{point}</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Risks */}
            {analysis.risk_factors && analysis.risk_factors.length > 0 && (
                <div style={{ marginBottom: '16px' }}>
                    <p className="srule" style={{ borderColor: 'var(--color-negative)', color: 'var(--color-negative)' }}>risiko</p>
                    <div className="post-list">
                        {analysis.risk_factors.map((risk, i) => (
                            <div key={i} className="post-row">
                                <div className="post-text" style={{ fontSize: '12px' }}>{risk}</div>
                                <div className="pip neg">!</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Opportunities */}
            {analysis.opportunities && analysis.opportunities.length > 0 && (
                <div style={{ marginBottom: '16px' }}>
                    <p className="srule" style={{ borderColor: 'var(--color-positive)', color: 'var(--color-positive)' }}>peluang</p>
                    <div className="post-list">
                        {analysis.opportunities.map((opp, i) => (
                            <div key={i} className="post-row">
                                <div className="post-text" style={{ fontSize: '12px' }}>{opp}</div>
                                <div className="pip pos">✓</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Recommendation */}
            {analysis.recommendation && (
                <div className="pq" style={{ borderLeftColor: 'var(--color-positive)' }}>
                    <p>{analysis.recommendation}</p>
                    <cite>Rekomendasi</cite>
                </div>
            )}

            {/* Entities */}
            {analysis.entities && (
                <div style={{ marginBottom: '16px' }}>
                    <p className="srule">entitas terdeteksi</p>
                    <div className="kw-cloud">
                        {analysis.entities.people && analysis.entities.people.map((p, i) => (
                            <span key={`p-${i}`} className="kw">{p}</span>
                        ))}
                        {analysis.entities.organizations && analysis.entities.organizations.map((o, i) => (
                            <span key={`o-${i}`} className="kw">{o}</span>
                        ))}
                        {analysis.entities.topics && analysis.entities.topics.map((t, i) => (
                            <span key={`t-${i}`} className="kw">{t}</span>
                        ))}
                    </div>
                </div>
            )}

            {/* Credibility */}
            {analysis.credibility && analysis.credibility.score > 0 && (
                <div>
                    <p className="srule">kredibilitas sumber</p>
                    <div className="bar-block">
                        <div className="bar-meta">
                            <span className="bar-name">skor</span>
                            <span className="bar-pct">{analysis.credibility.score}/100</span>
                        </div>
                        <div className="bar-track">
                            <div className="bar-fill" style={{ width: `${analysis.credibility.score}%` }}></div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
