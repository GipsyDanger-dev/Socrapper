import React, { useState } from 'react';

export default function SurfResultsTab({ results }) {
    const [expandedItem, setExpandedItem] = useState(null);

    if (!results) {
        return (
            <div className="panel on">
                <div className="empty-state">Belum ada hasil surfing. Coba cari sesuatu!</div>
            </div>
        );
    }

    const query = results.query || '';
    const summary = results.summary || null;

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

    if (displayResults.length === 0) {
        return (
            <div className="panel on">
                <div className="empty-state">Tidak ditemukan hasil untuk "{query}"</div>
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
        <div className="panel on">
            {/* Summary */}
            {summary && (
                <>
                    <p className="srule">ringkasan: "{query}"</p>
                    <div className="tc" style={{ marginBottom: '18px' }}>
                        <div className="cell">
                            <div className="cn">{summary.total_sources || displayResults.length}</div>
                            <div className="clbl">sumber</div>
                        </div>
                        <div className="cell">
                            <div className="cn">{summary.total_words || 0}</div>
                            <div className="clbl">total kata</div>
                        </div>
                        {summary.sentiment_overview && (
                            <div className="cell">
                                <div className="cn">
                                    {summary.sentiment_overview.positive > summary.sentiment_overview.negative ? '+' : ''}
                                    {summary.sentiment_overview.positive || 0}
                                </div>
                                <div className="clbl">sentimen</div>
                            </div>
                        )}
                    </div>

                    {summary.key_topics && summary.key_topics.length > 0 && (
                        <div style={{ marginBottom: '18px' }}>
                            <p className="side-head" style={{ marginBottom: '6px' }}>Topik Utama</p>
                            <div className="kw-cloud">
                                {summary.key_topics.map((topic, i) => (
                                    <span key={i} className="kw">{topic}</span>
                                ))}
                            </div>
                        </div>
                    )}
                </>
            )}

            {/* Results */}
            <p className="srule">{displayResults.length} hasil ditemukan</p>
            <div className="post-list">
                {displayResults.map((item, index) => (
                    <div
                        key={index}
                        className="post-row"
                        style={{ cursor: 'pointer', flexDirection: 'column', alignItems: 'flex-start' }}
                        onClick={() => setExpandedItem(expandedItem === index ? null : index)}
                    >
                        <div style={{ width: '100%' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '8px' }}>
                                <div className="post-text" style={{ fontWeight: 700 }}>
                                    <span style={{ color: 'var(--color-text-faded)', marginRight: '6px' }}>#{index + 1}</span>
                                    {item.url ? (
                                        <a href={item.url} target="_blank" rel="noopener noreferrer" style={{ color: 'inherit', textDecoration: 'none' }}>
                                            {cleanText(item.title) || 'Untitled'}
                                        </a>
                                    ) : (
                                        cleanText(item.title) || 'Untitled'
                                    )}
                                </div>
                                <span style={{ fontSize: '10px', color: 'var(--color-text-faded)', whiteSpace: 'nowrap' }}>
                                    {expandedItem === index ? '▼' : '▶'}
                                </span>
                            </div>
                            <div className="post-by" style={{ marginTop: '4px' }}>
                                {item.source && <span className="plat-tag">{item.source}</span>}
                                {item.word_count > 0 && <span style={{ marginLeft: '6px' }}>{item.word_count} kata</span>}
                            </div>
                        </div>

                        {(item.snippet || item.description) && (
                            <div style={{ marginTop: '6px', fontSize: '12px', color: 'var(--color-text-secondary)', lineHeight: '1.5' }}>
                                {cleanText(item.snippet || item.description)}
                            </div>
                        )}

                        {expandedItem === index && (
                            <div style={{ marginTop: '10px', width: '100%' }}>
                                {item.author && (
                                    <div style={{ fontSize: '10px', color: 'var(--color-text-faded)', marginBottom: '4px' }}>
                                        {item.author} {item.publish_date ? `· ${item.publish_date}` : ''}
                                    </div>
                                )}
                                {item.content && (
                                    <div style={{ marginTop: '8px', padding: '12px', background: 'var(--color-surface)', fontSize: '12px', lineHeight: '1.6', maxHeight: '300px', overflow: 'auto' }}>
                                        {cleanText(item.content).substring(0, 2000)}
                                        {cleanText(item.content).length > 2000 && '...'}
                                    </div>
                                )}
                                {item.content_excerpt && !item.content && (
                                    <div style={{ marginTop: '8px', padding: '12px', background: 'var(--color-surface)', fontSize: '12px', lineHeight: '1.6' }}>
                                        {cleanText(item.content_excerpt)}
                                    </div>
                                )}
                                <div style={{ marginTop: '6px', fontSize: '9px', color: item.extraction_success ? 'var(--color-positive)' : 'var(--color-text-faded)' }}>
                                    {item.extraction_success ? '✓ konten berhasil di-extract' : '⚠ hanya snippet tersedia'}
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
