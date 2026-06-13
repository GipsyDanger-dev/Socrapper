import React, { useState, useEffect, useRef } from 'react';

export default function HomeSidebar() {
    const [news, setNews] = useState([]);
    const [activeIndex, setActiveIndex] = useState(0);
    const [fade, setFade] = useState(true);
    const timerRef = useRef(null);

    // Fetch news on mount
    useEffect(() => {
        fetchNews();
    }, []);

    // Auto-rotate every 5 seconds
    useEffect(() => {
        if (news.length <= 1) return;
        timerRef.current = setInterval(() => {
            setFade(false);
            setTimeout(() => {
                setActiveIndex((prev) => (prev + 1) % news.length);
                setFade(true);
            }, 300);
        }, 5000);
        return () => clearInterval(timerRef.current);
    }, [news]);

    const fetchNews = async () => {
        try {
            const response = await fetch('/api/surf/quick', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: 'berita terkini Indonesia', limit: 10 }),
            });
            const data = await response.json();
            if (data.success && data.results) {
                setNews(data.results);
            }
        } catch (err) {
            console.error('Failed to fetch news:', err);
        }
    };

    const current = news[activeIndex];

    return (
        <div className="sidebar-wrap">
            {/* News Ticker 1 */}
            <div className="sidebar-news-box">
                <div className="sidebar-section-label">
                    <i className="fa-solid fa-bolt" /> Berita Terkini
                </div>
                {current ? (
                    <a
                        href={current.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`sidebar-news-link ${fade ? 'sidebar-news-visible' : 'sidebar-news-hidden'}`}
                    >
                        <div className="sidebar-news-source">{current.source || 'News'}</div>
                        <div className="sidebar-news-title">{current.title}</div>
                        {current.snippet && (
                            <div className="sidebar-news-snippet">{current.snippet.substring(0, 100)}...</div>
                        )}
                        <div className="sidebar-news-cta">buka berita <i className="fa-solid fa-arrow-up-right-from-square" /></div>
                    </a>
                ) : (
                    <div className="sidebar-news-loading">
                        <i className="fa-solid fa-spinner fa-spin" /> memuat berita...
                    </div>
                )}
                {/* Dots indicator */}
                {news.length > 1 && (
                    <div className="sidebar-news-dots">
                        {news.slice(0, 5).map((_, i) => (
                            <span
                                key={i}
                                className={`sidebar-news-dot ${i === activeIndex % 5 ? 'active' : ''}`}
                                onClick={() => { setFade(false); setTimeout(() => { setActiveIndex(i); setFade(true); }, 200); }}
                            />
                        ))}
                    </div>
                )}
            </div>

            {/* Quote of the day */}
            <div className="sidebar-section">
                <div className="sidebar-section-label">Kutipan</div>
                <blockquote className="sidebar-quote">
                    "Opini publik adalah cerminan dari kebenaran yang belum ditemukan."
                </blockquote>
                <div className="sidebar-quote-attr">— Pepatah Jurnalis</div>
            </div>

            {/* Facts */}
            <div className="sidebar-section">
                <div className="sidebar-section-label">Fakta Singkat</div>
                <div className="sidebar-fact">
                    <span className="sidebar-fact-num">4.9M</span>
                    <span className="sidebar-fact-desc">pengguna internet di Indonesia aktif di media sosial</span>
                </div>
                <div className="sidebar-fact">
                    <span className="sidebar-fact-num">2h 31m</span>
                    <span className="sidebar-fact-desc">rata-rata waktu harian di media sosial</span>
                </div>
                <div className="sidebar-fact">
                    <span className="sidebar-fact-num">73%</span>
                    <span className="sidebar-fact-desc">konsumen mengandalkan ulasan online sebelum membeli</span>
                </div>
            </div>

            {/* News Ticker 2 */}
            <div className="sidebar-news-box">
                <div className="sidebar-section-label">
                    <i className="fa-solid fa-fire" /> Trending
                </div>
                {news.length > 1 ? (
                    <a
                        href={news[(activeIndex + 3) % news.length]?.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`sidebar-news-link ${fade ? 'sidebar-news-visible' : 'sidebar-news-hidden'}`}
                    >
                        <div className="sidebar-news-source">
                            {news[(activeIndex + 3) % news.length]?.source || 'News'}
                        </div>
                        <div className="sidebar-news-title">
                            {news[(activeIndex + 3) % news.length]?.title}
                        </div>
                        <div className="sidebar-news-cta">buka berita <i className="fa-solid fa-arrow-up-right-from-square" /></div>
                    </a>
                ) : (
                    <div className="sidebar-news-loading">
                        <i className="fa-solid fa-spinner fa-spin" /> memuat...
                    </div>
                )}
            </div>

            {/* Decorative ornament */}
            <div className="sidebar-ornament">— ✦ —</div>
        </div>
    );
}
