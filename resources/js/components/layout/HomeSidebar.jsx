import React, { useState, useEffect, useRef } from 'react';

// Real quotes about media, journalism, and public opinion
const QUOTES = [
    { text: "Opini publik adalah kekuatan terbesar di dunia modern.", author: "Walter Lippmann" },
    { text: "Pers adalah penjaga kebebasan masyarakat.", author: "Thomas Jefferson" },
    { text: "Siapa yang mengontrol media, mengontrol pikiran publik.", author: "Noam Chomsky" },
    { text: "Kebebasan pers adalah fondasi demokrasi.", author: "Mahatma Gandhi" },
    { text: "Media massa adalah cerminan masyarakat yang melihatnya.", author: "Marshall McLuhan" },
    { text: "Dalam era informasi, kebenaran adalah mata uang paling berharga.", author: "Edward Snowden" },
    { text: "Jurnalisme adalah sejarah yang ditulis saat peristiwa terjadi.", author: "Theodore H. White" },
    { text: "Opini yang terbentuk tanpa informasi adalah prasangka.", author: "Aristoteles" },
    { text: "Media sosial memberikan suara kepada yang tidak bersuara.", author: "Mark Zuckerberg" },
    { text: "Kebenaran tidak pernah takut akan penyelidikan.", author: "Benjamin Franklin" },
];

export default function HomeSidebar() {
    const [news, setNews] = useState([]);
    const [activeNewsIndex, setActiveNewsIndex] = useState(0);
    const [newsFade, setNewsFade] = useState(true);
    const [quoteIndex, setQuoteIndex] = useState(0);
    const [quoteFade, setQuoteFade] = useState(true);
    const newsTimerRef = useRef(null);
    const quoteTimerRef = useRef(null);

    // Fetch news on mount
    useEffect(() => {
        fetchNews();
    }, []);

    // Auto-rotate news every 5 seconds
    useEffect(() => {
        if (news.length <= 1) return;
        newsTimerRef.current = setInterval(() => {
            setNewsFade(false);
            setTimeout(() => {
                setActiveNewsIndex((prev) => (prev + 1) % news.length);
                setNewsFade(true);
            }, 300);
        }, 5000);
        return () => clearInterval(newsTimerRef.current);
    }, [news]);

    // Auto-rotate quotes every 6 seconds
    useEffect(() => {
        quoteTimerRef.current = setInterval(() => {
            setQuoteFade(false);
            setTimeout(() => {
                setQuoteIndex((prev) => (prev + 1) % QUOTES.length);
                setQuoteFade(true);
            }, 400);
        }, 6000);
        return () => clearInterval(quoteTimerRef.current);
    }, []);

    const fetchNews = async () => {
        try {
            // Try cached news first (instant)
            const cachedRes = await fetch('/api/cached-news');
            const cachedData = await cachedRes.json();
            if (cachedData.success && cachedData.general.length > 0) {
                setNews(cachedData.general);
                return;
            }

            // Fallback to live fetch
            const response = await fetch('/api/surf/quick', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: 'berita terkini Indonesia', limit: 10 }),
            });
            if (!response.ok) return;
            const data = await response.json();
            if (data.success && data.results) {
                setNews(data.results);
            }
        } catch (err) {
            console.error('Failed to fetch news:', err);
        }
    };

    const currentNews = news[activeNewsIndex];
    const currentQuote = QUOTES[quoteIndex];

    return (
        <div className="sidebar-wrap">
            {/* News Ticker 1 */}
            <div className="sidebar-news-box">
                <div className="sidebar-section-label">
                    <i className="fa-solid fa-bolt" /> Berita Terkini
                </div>
                {currentNews ? (
                    <a
                        href={currentNews.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`sidebar-news-link ${newsFade ? 'sidebar-news-visible' : 'sidebar-news-hidden'}`}
                    >
                        <div className="sidebar-news-source">{currentNews.source || 'News'}</div>
                        <div className="sidebar-news-title">{currentNews.title}</div>
                        {currentNews.snippet && (
                            <div className="sidebar-news-snippet">{currentNews.snippet.substring(0, 100)}...</div>
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
                                className={`sidebar-news-dot ${i === activeNewsIndex % 5 ? 'active' : ''}`}
                                onClick={() => { setNewsFade(false); setTimeout(() => { setActiveNewsIndex(i); setNewsFade(true); }, 200); }}
                            />
                        ))}
                    </div>
                )}
            </div>

            {/* Quote - rotating */}
            <div className="sidebar-section">
                <div className="sidebar-section-label">Kutipan</div>
                <div className={`sidebar-quote-wrap ${quoteFade ? 'sidebar-quote-visible' : 'sidebar-quote-hidden'}`}>
                    <blockquote className="sidebar-quote">
                        "{currentQuote.text}"
                    </blockquote>
                    <div className="sidebar-quote-attr">— {currentQuote.author}</div>
                </div>
                {/* Quote dots */}
                <div className="sidebar-quote-dots">
                    {QUOTES.map((_, i) => (
                        <span
                            key={i}
                            className={`sidebar-quote-dot ${i === quoteIndex ? 'active' : ''}`}
                            onClick={() => { setQuoteFade(false); setTimeout(() => { setQuoteIndex(i); setQuoteFade(true); }, 200); }}
                        />
                    ))}
                </div>
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
                        href={news[(activeNewsIndex + 3) % news.length]?.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`sidebar-news-link ${newsFade ? 'sidebar-news-visible' : 'sidebar-news-hidden'}`}
                    >
                        <div className="sidebar-news-source">
                            {news[(activeNewsIndex + 3) % news.length]?.source || 'News'}
                        </div>
                        <div className="sidebar-news-title">
                            {news[(activeNewsIndex + 3) % news.length]?.title}
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
