import React from 'react';

export default function RawDataTab({ data }) {
    if (!data || data.length === 0) {
        return (
            <div id="raw-data" className="tab-content active">
                <div className="data-container">
                    <p className="info-text">Hasil scraping akan ditampilkan di sini</p>
                </div>
            </div>
        );
    }

    return (
        <div id="raw-data" className="tab-content active">
            <div className="data-container">
                {data.map((item, index) => (
                    <div key={index} className="data-item">
                        <div className="data-item-header">
                            <div>
                                <div className="data-item-author">{item.author}</div>
                                <span className="data-item-platform">{item.platform}</span>
                            </div>
                        </div>
                        <div className="data-item-text">{item.text}</div>
                        <div className="data-item-stats">
                            <span><i className="fas fa-heart"></i> {item.likes}</span>
                            <span><i className="fas fa-comment"></i> {item.comments}</span>
                            <span><i className="fas fa-share"></i> {item.shares}</span>
                        </div>
                        <div className="data-item-timestamp">
                            {new Date(item.timestamp).toLocaleString('id-ID')}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
