import React, { useState } from "react";

export default function SurfResultsTab({ results }) {
  const [expandedItem, setExpandedItem] = useState(null);

  if (!results) {
    return (
      <div className="panel on">
        <div className="empty-state">
          Belum ada hasil surfing. Coba cari sesuatu!
        </div>
      </div>
    );
  }

  const query = results.query || "";
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

  // Clean all result text fields upfront
  const cleanItem = (item) => {
    const c = (t) => {
      if (!t) return "";
      return String(t)
        .replace(/<[^>]*>/g, " ")
        .replace(/&nbsp;/g, " ")
        .replace(/&amp;/g, "&")
        .replace(/&lt;/g, "<")
        .replace(/&gt;/g, ">")
        .replace(/&quot;/g, '"')
        .replace(/&#39;/g, "'")
        .replace(/\s+/g, " ")
        .trim();
    };
    return {
      ...item,
      title: c(item.title),
      snippet: c(item.snippet),
      description: c(item.description),
      content: c(item.content),
      content_excerpt: c(item.content_excerpt),
      source: c(item.source),
      author: c(item.author),
    };
  };
  displayResults = displayResults.map(cleanItem);

  const cleanText = (text) => {
    if (!text) return "";
    return text
      .replace(/<[^>]*>/g, "")
      .replace(/&nbsp;/g, " ")
      .replace(/&amp;/g, "&")
      .replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">")
      .replace(/&quot;/g, '"')
      .replace(/&#39;/g, "'")
      .trim();
  };

  return (
    <div className="panel on">          {/* Summary */}
      {summary && (
        <>
          <h3 className="srule" style={{ margin: 0 }}>ringkasan: "{query}"</h3>
          <div className="tc" style={{ marginBottom: "18px" }}>
            <div className="cell">
              <div className="cn">
                {summary.total_sources || displayResults.length}
              </div>
              <div className="clbl">sumber</div>
            </div>
            <div className="cell">
              <div className="cn">{summary.total_words || 0}</div>
              <div className="clbl">total kata</div>
            </div>
            {summary.sentiment_overview && (
              <div className="cell">
                <div className="cn" style={{
                  fontSize: '14px',
                }}>
                  <span className="pos">{summary.sentiment_overview.positive || 0}↑</span>
                  {' '}
                  <span className="neg">{summary.sentiment_overview.negative || 0}↓</span>
                  {' '}
                  <span className="neu">{summary.sentiment_overview.neutral || 0}—</span>
                </div>
                <div className="clbl">sentimen (+/−/—)</div>
              </div>
            )}
          </div>

          {summary.key_topics && summary.key_topics.length > 0 && (
            <div style={{ marginBottom: "18px" }}>
              <p className="side-head" style={{ marginBottom: "6px" }}>
                Topik Utama
              </p>
              <div className="kw-cloud">
                {summary.key_topics.map((topic, i) => (
                  <span key={i} className="kw">
                    {topic}
                  </span>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Results */}
      <h3 className="srule" style={{ margin: 0 }}>{displayResults.length} hasil ditemukan</h3>
      <div className="post-list">
        {displayResults.map((item, index) => (
          <div
            key={index}
            className="post-row"
            style={{
              cursor: "pointer",
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-start",
            }}
            onClick={() =>
              setExpandedItem(expandedItem === index ? null : index)
            }
          >
            <div style={{ width: "100%" }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                  gap: "8px",
                }}
              >
                <div className="post-text" style={{ fontWeight: 700 }}>
                  <span
                    style={{
                      color: "var(--color-text-faded)",
                      marginRight: "6px",
                    }}
                  >
                    #{index + 1}
                  </span>
                  {item.url ? (
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: "inherit", textDecoration: "none" }}
                    >
                      {cleanText(item.title) || "Untitled"}
                    </a>
                  ) : (
                    cleanText(item.title) || "Untitled"
                  )}
                  {/* Per-item sentiment badge */}
                  {item.sentiment && (
                    <span style={{
                      display: 'inline-block',
                      fontSize: '9px',
                      padding: '1px 5px',
                      marginLeft: '6px',
                      borderRadius: '2px',
                      fontWeight: 500,
                      verticalAlign: 'middle',
                      color: '#000',
                      background: item.sentiment === 'positive' ? 'var(--color-positive, #2e7d32)'
                        : item.sentiment === 'negative' ? 'var(--color-negative, #c62828)'
                        : 'var(--color-text-faded, #888)',
                    }}>
                      {item.sentiment === 'positive' ? '+' : item.sentiment === 'negative' ? '−' : '•'}
                    </span>
                  )}
                </div>
                <span
                  style={{
                    fontSize: "10px",
                    color: "var(--color-text-faded)",
                    whiteSpace: "nowrap",
                  }}
                >
                  {expandedItem === index ? "▼" : "▶"}
                </span>
              </div>
              <div className="post-by" style={{ marginTop: "4px" }}>
                {item.source && item.url ? (
                  <a href={item.url} target="_blank" rel="noopener noreferrer" className="plat-tag plat-tag-link">
                    {item.source}
                  </a>
                ) : item.source ? (
                  <span className="plat-tag">{item.source}</span>
                ) : null}
                {item.word_count > 0 && (
                  <span style={{ marginLeft: "6px" }}>
                    {item.word_count} kata
                  </span>
                )}
              </div>
            </div>

            {(item.snippet || item.description) && (
              <div
                style={{
                  marginTop: "6px",
                  fontSize: "12px",
                  color: "var(--color-text-secondary)",
                  lineHeight: "1.6",
                }}
              >
                {cleanText(item.snippet || item.description)
                  .split("\n")
                  .filter(Boolean)
                  .map((line, i) => (
                    <div
                      key={i}
                      style={{
                        marginBottom:
                          i <
                          cleanText(item.snippet || item.description)
                            .split("\n")
                            .filter(Boolean).length -
                            1
                            ? "4px"
                            : 0,
                        paddingLeft: "10px",
                        borderLeft: "2px solid var(--color-border-secondary)",
                      }}
                    >
                      {line}
                    </div>
                  ))}
              </div>
            )}

            {expandedItem === index && (
              <div style={{ marginTop: "10px", width: "100%" }}>
                {item.author && (
                  <div
                    style={{
                      fontSize: "10px",
                      color: "var(--color-text-faded)",
                      marginBottom: "4px",
                    }}
                  >
                    {item.author}{" "}
                    {item.publish_date ? `· ${item.publish_date}` : ""}
                  </div>
                )}
                {item.content && (
                  <div
                    style={{
                      marginTop: "8px",
                      padding: "12px",
                      background: "var(--color-surface)",
                      fontSize: "12px",
                      lineHeight: "1.6",
                      maxHeight: "300px",
                      overflow: "auto",
                    }}
                  >
                    {cleanText(item.content).substring(0, 2000)}
                    {cleanText(item.content).length > 2000 && "..."}
                  </div>
                )}
                {item.content_excerpt && !item.content && (
                  <div
                    style={{
                      marginTop: "8px",
                      padding: "12px",
                      background: "var(--color-surface)",
                      fontSize: "12px",
                      lineHeight: "1.6",
                    }}
                  >
                    {cleanText(item.content_excerpt)}
                  </div>
                )}
                <div
                  style={{
                    marginTop: "6px",
                    display: "flex",
                    alignItems: "center",
                    gap: "12px",
                    fontSize: "9px",
                  }}
                >
                  <span style={{
                    color: item.extraction_success
                      ? "var(--color-positive)"
                      : "var(--color-text-faded)",
                  }}>
                    {item.extraction_success
                      ? "✓ konten berhasil di-extract"
                      : "⚠ hanya snippet tersedia"}
                  </span>
                  {item.url && (
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        color: "var(--color-text-secondary)",
                        textDecoration: "underline",
                        textUnderlineOffset: "2px",
                      }}
                    >
                      buka sumber →
                    </a>
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
