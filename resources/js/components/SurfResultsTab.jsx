import React, { useState } from 'react';

export default function SurfResultsTab({ results }) {
    const [expandedItem, setExpandedItem] = useState(null);

    console.log('SurfResultsTab results:', results);

    if (!results) {
        return (
            <div className="tab-content empty-state">
                <p>🌐 Belum ada hasil surfing. Coba cari sesuatu!</p>
            </div>
        );
    }

    // Support both quick surf and full surf
    const query = results.query || '';
    const summary = results.summary || null;
    const sentiment = results.sentiment || null;

    // Get display results from multiple possible locations
    let displayResults = [];
    if (results.merged_results && results.merged_results.length > 0) {
        displayResults = results.merged_results;
    } else if (results.results && results.results.length > 0) {
        displayResults = results.results;
    } else if (results.search_results && results.search_results.length > 0) {
        displayResults = results.search_results;
    } else if (Array.isArray(results.data)) {
        displayResults = results.data;
    }

    console.log('displayResults:', displayResults);

    if (displayResults.length === 0) {
        return (
            <div className="tab-content empty-state">
                <p>❌ Tidak ditemukan hasil untuk "{query}"</p>
                <pre style={{textAlign: 'left', fontSize: '0.8em', marginTop: '10px', color: '#999'}}>
                    {JSON.stringify(results, null, 2).substring(0, 500)}
                </pre>
            </div>
        );
    }

    const cleanText = (text) => {
        if (!text) return '';
        return text
            .replace(/<[^>]*>/g, '')
            .replace(/&nbsp;/g, ' ')
            .replace(/&amp;/g, '&')
            .replace(/&lt;/g, '<')
            .replace(/&gt;/g, '>')
            .replace(/&quot;/g, '"')
            .replace(/&#39;/g, "'")
            .trim();
    };

    return (
        <div className="tab-content surf-results">
            {/* Summary Card */}
            {summary && (
                <div className="surf-summary-card">
                    <h3>📋 Ringkasan: "{query}"</h3>
                    <div className="summary-stats">
                        <div className="stat-item">
                            <span className="stat-value">{summary.total_sources || displayResults.length}</span>
                            <span className="stat-label">Sumber</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-value">{summary.total_words || 0}</span>
                            <span className="stat-label">Total Kata</span>
                        </div>
                        {summary.sentiment_overview && (
                            <div className="stat-item">
                                <span className="stat-value">
                                    {summary.sentiment_overview.positive > summary.sentiment_overview.negative
                                        ? summary.sentiment_overview.positive > summary.sentiment_overview.neutral
                                            ? '😊 Positif'
                                            : '😐 Netral'
                                        : summary.sentiment_overview.negative > summary.sentiment_overview.neutral
                                            ? '😟 Negatif'
                                            : '😐 Netral'
                                    }
                                </span>
                                <span className="stat-label">Sentimen Dominan</span>
                            </div>
                        )}
                    </div>

                    {summary.key_topics && summary.key_topics.length > 0 && (
                        <div className="key-topics">
                            <strong>🏷️ Topik Utama:</strong>
                            <div className="topic-tags">
                                {summary.key_topics.map((topic, i) => (
                                    <span key={i} className="topic-tag">{topic}</span>
                                ))}
                            </div>
                        </div>
                    )}

                    {summary.unique_sources && summary.unique_sources.length > 0 && (
                        <div className="sources-list">
                            <strong>📡 Sumber:</strong>
                            <div className="source-tags">
                                {summary.unique_sources.map((source, i) => (
                                    <span key={i} className="source-tag">{source}</span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Results List */}
            <div className="surf-results-list">
                <h3>📄 {displayResults.length} Hasil Ditemukan</h3>

                {displayResults.map((item, index) => (
                    <div
                        key={index}
                        className={`surf-result-item ${expandedItem === index ? 'expanded' : ''}`}
                    >
                        <div
                            className="result-header"
                            onClick={() => setExpandedItem(expandedItem === index ? null : index)}
                        >
                            <div className="result-title-section">
                                <span className="result-number">#{index + 1}</span>
                                <h4>
                                    <a href={item.url} target="_blank" rel="noopener noreferrer">
                                        {cleanText(item.title) || 'Untitled'}
                                    </a>
                                </h4>
                            </div>
                            <div className="result-meta">
                                {item.source && (
                                    <span className="result-source">{item.source}</span>
                                )}
                                {item.type && (
                                    <span className="result-source" style={{background: '#dbeafe', color: '#1d4ed8'}}>
                                        {item.type}
                                    </span>
                                )}
                                {item.word_count > 0 && (
                                    <span className="result-wordcount">{item.word_count} kata</span>
                                )}
                                <span className="expand-icon">
                                    {expandedItem === index ? '▼' : '▶'}
                                </span>
                            </div>
                        </div>

                        {(item.snippet || item.description) && (
                            <p className="result-snippet">
                                {cleanText(item.snippet || item.description)}
                            </p>
                        )}

                        {expandedItem === index && (
                            <div className="result-expanded">
                                <div className="result-details">
                                    {item.author && (
                                        <span className="detail-item">✍️ {item.author}</span>
                                    )}
                                    {item.publish_date && (
                                        <span className="detail-item">📅 {item.publish_date}</span>
                                    )}
                                    {item.url && (
                                        <span className="detail-item">
                                            🔗 <a href={item.url} target="_blank" rel="noopener noreferrer">
                                                {item.url.length > 60 ? item.url.substring(0, 60) + '...' : item.url}
                                            </a>
                                        </span>
                                    )}
                                </div>

                                {item.content && (
                                    <div className="result-content">
                                        <h5>📄 Konten Lengkap:</h5>
                                        <div className="content-text">
                                            {item.content.substring(0, 2000)}
                                            {item.content.length > 2000 && '...'}
                                        </div>
                                    </div>
                                )}

                                {item.content_excerpt && !item.content && (
                                    <div className="result-content">
                                        <h5>📄 Cuplikan:</h5>
                                        <div className="content-text">{item.content_excerpt}</div>
                                    </div>
                                )}

                                {item.images && item.images.length > 0 && (
                                    <div className="result-images">
                                        <h5>🖼️ Gambar:</h5>
                                        <div className="image-grid">
                                            {item.images.slice(0, 3).map((img, i) => (
                                                <img
                                                    key={i}
                                                    src={img}
                                                    alt={`Image ${i + 1}`}
                                                    className="result-thumbnail"
                                                    onError={(e) => e.target.style.display = 'none'}
                                                />
                                            ))}
                                        </div>
                                    </div>
                                )}

                                <div className="extraction-status">
                                    {item.extraction_success ? (
                                        <span className="status-success">✅ Konten berhasil di-extract</span>
                                    ) : (
                                        <span className="status-fallback">⚠️ Hanya snippet tersedia</span>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
