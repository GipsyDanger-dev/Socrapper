import React from 'react';

export default function AiAnalysisCard({ analysis }) {
    if (!analysis) return null;

    const getSentimentColor = (sentiment) => {
        if (!sentiment) return '#6b7280';
        const s = (sentiment.overall || sentiment).toLowerCase();
        if (s === 'bullish' || s === 'positive') return '#10b981';
        if (s === 'bearish' || s === 'negative') return '#ef4444';
        if (s === 'mixed') return '#f59e0b';
        return '#6b7280';
    };

    const getSentimentEmoji = (sentiment) => {
        if (!sentiment) return '😐';
        const s = (sentiment.overall || sentiment).toLowerCase();
        if (s === 'bullish' || s === 'positive') return '🟢';
        if (s === 'bearish' || s === 'negative') return '🔴';
        if (s === 'mixed') return '🟡';
        return '⚪';
    };

    return (
        <div className="ai-analysis-card">
            <div className="ai-header">
                <h3>🤖 AI Analysis</h3>
                <span className="ai-model-badge">
                    {analysis.model || 'MiMo v2.5 Pro'}
                </span>
            </div>

            {/* Sentiment Overview */}
            {analysis.sentiment && (
                <div className="ai-sentiment-overview">
                    <div className="ai-sentiment-main" style={{borderColor: getSentimentColor(analysis.sentiment)}}>
                        <span className="ai-sentiment-emoji">{getSentimentEmoji(analysis.sentiment)}</span>
                        <div>
                            <span className="ai-sentiment-label" style={{color: getSentimentColor(analysis.sentiment)}}>
                                {(analysis.sentiment.overall || 'neutral').toUpperCase()}
                            </span>
                            {analysis.sentiment.confidence !== undefined && (
                                <span className="ai-confidence">
                                    Confidence: {analysis.sentiment.confidence}%
                                </span>
                            )}
                            {analysis.sentiment.score !== undefined && (
                                <span className="ai-confidence">
                                    Score: {analysis.sentiment.score > 0 ? '+' : ''}{analysis.sentiment.score}
                                </span>
                            )}
                        </div>
                    </div>
                    {analysis.timeframe && (
                        <span className="ai-timeframe">⏱️ {analysis.timeframe}</span>
                    )}
                </div>
            )}

            {/* Summary / Analysis */}
            {(analysis.summary || analysis.analysis) && (
                <div className="ai-section">
                    <h4>📋 Ringkasan</h4>
                    <p>{analysis.summary || analysis.analysis}</p>
                </div>
            )}

            {/* Key Points / Findings */}
            {(analysis.key_points || analysis.key_findings) && (analysis.key_points || analysis.key_findings).length > 0 && (
                <div className="ai-section">
                    <h4>🎯 Poin Utama</h4>
                    <ul>
                        {(analysis.key_points || analysis.key_findings).map((point, i) => (
                            <li key={i}>{point}</li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Risk Factors */}
            {analysis.risk_factors && analysis.risk_factors.length > 0 && (
                <div className="ai-section">
                    <h4>⚠️ Risiko</h4>
                    <ul className="risk-list">
                        {analysis.risk_factors.map((risk, i) => (
                            <li key={i}>{risk}</li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Opportunities */}
            {analysis.opportunities && analysis.opportunities.length > 0 && (
                <div className="ai-section">
                    <h4>🚀 Peluang</h4>
                    <ul className="opportunity-list">
                        {analysis.opportunities.map((opp, i) => (
                            <li key={i}>{opp}</li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Recommendation */}
            {analysis.recommendation && (
                <div className="ai-section ai-recommendation">
                    <h4>💡 Rekomendasi</h4>
                    <p>{analysis.recommendation}</p>
                </div>
            )}

            {/* Entities */}
            {analysis.entities && (
                <div className="ai-section">
                    <h4>🏷️ Entitas Terdeteksi</h4>
                    <div className="ai-entities">
                        {analysis.entities.people && analysis.entities.people.length > 0 && (
                            <div className="entity-group">
                                <span className="entity-label">👤 Orang:</span>
                                {analysis.entities.people.map((p, i) => (
                                    <span key={i} className="entity-tag">{p}</span>
                                ))}
                            </div>
                        )}
                        {analysis.entities.organizations && analysis.entities.organizations.length > 0 && (
                            <div className="entity-group">
                                <span className="entity-label">🏢 Organisasi:</span>
                                {analysis.entities.organizations.map((o, i) => (
                                    <span key={i} className="entity-tag">{o}</span>
                                ))}
                            </div>
                        )}
                        {analysis.entities.topics && analysis.entities.topics.length > 0 && (
                            <div className="entity-group">
                                <span className="entity-label">📌 Topik:</span>
                                {analysis.entities.topics.map((t, i) => (
                                    <span key={i} className="entity-tag">{t}</span>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Credibility */}
            {analysis.credibility && analysis.credibility.score > 0 && (
                <div className="ai-section">
                    <h4>🔍 Kredibilitas Sumber</h4>
                    <div className="credibility-bar">
                        <div 
                            className="credibility-fill" 
                            style={{width: `${analysis.credibility.score}%`}}
                        ></div>
                    </div>
                    <span className="credibility-score">{analysis.credibility.score}/100</span>
                </div>
            )}
        </div>
    );
}
