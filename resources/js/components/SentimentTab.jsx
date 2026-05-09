import React from 'react';

export default function SentimentTab({ analysis }) {
    if (!analysis) {
        return (
            <div id="sentiment" className="tab-content active">
                <div className="sentiment-summary">
                    <div className="sentiment-stat">
                        <div className="stat-value positive">0</div>
                        <div className="stat-label">Positif</div>
                    </div>
                    <div className="sentiment-stat">
                        <div className="stat-value neutral">0</div>
                        <div className="stat-label">Netral</div>
                    </div>
                    <div className="sentiment-stat">
                        <div className="stat-value negative">0</div>
                        <div className="stat-label">Negatif</div>
                    </div>
                </div>
                <div className="sentiment-details">
                    <p className="info-text">Hasil analisis sentimen akan ditampilkan di sini</p>
                </div>
            </div>
        );
    }

    const getSentimentLabel = (sentiment) => {
        const labels = {
            'positive': 'Positif',
            'negative': 'Negatif',
            'neutral': 'Netral',
        };
        return labels[sentiment] || 'Tidak Diketahui';
    };

    return (
        <div id="sentiment" className="tab-content active">
            <div className="sentiment-summary">
                <div className="sentiment-stat">
                    <div className="stat-value positive">{analysis.positive}</div>
                    <div className="stat-label">Positif ({analysis.percentage.positive}%)</div>
                </div>
                <div className="sentiment-stat">
                    <div className="stat-value neutral">{analysis.neutral}</div>
                    <div className="stat-label">Netral ({analysis.percentage.neutral}%)</div>
                </div>
                <div className="sentiment-stat">
                    <div className="stat-value negative">{analysis.negative}</div>
                    <div className="stat-label">Negatif ({analysis.percentage.negative}%)</div>
                </div>
            </div>

            <div className="sentiment-details">
                {analysis.details.map((item, index) => (
                    <div key={index} className={`sentiment-item ${item.sentiment}`}>
                        <span className={`sentiment-badge ${item.sentiment}`}>
                            {getSentimentLabel(item.sentiment)}
                        </span>
                        <div className="sentiment-text">"{item.text}"</div>
                        <div className="sentiment-confidence">
                            Confidence: {item.confidence}%
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
