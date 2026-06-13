import React, { useState, useEffect } from 'react';

const PLATFORMS = [
    { id: 'twitter', name: 'Twitter/X', icon: 'fa-brands fa-x-twitter', desc: 'Real-time tweets & opini publik' },
    { id: 'reddit', name: 'Reddit', icon: 'fa-brands fa-reddit-alien', desc: 'Diskusi & komunitas' },
    { id: 'news', name: 'Google News', icon: 'fa-solid fa-newspaper', desc: 'Berita terkini dari seluruh dunia' },
    { id: 'stackoverflow', name: 'Stack Overflow', icon: 'fa-brands fa-stack-overflow', desc: 'Q&A developer & programmer' },
    { id: 'github', name: 'GitHub', icon: 'fa-brands fa-github', desc: 'Repositori open source & proyek' },
    { id: 'youtube', name: 'YouTube', icon: 'fa-brands fa-youtube', desc: 'Video & konten kreator' },
    { id: 'instagram', name: 'Instagram', icon: 'fa-brands fa-instagram', desc: 'Foto, reels & influencer' },
    { id: 'tiktok', name: 'TikTok', icon: 'fa-brands fa-tiktok', desc: 'Video pendek & tren viral' },
    { id: 'facebook', name: 'Facebook', icon: 'fa-brands fa-facebook', desc: 'Grup, halaman & komunitas' },
];

// Fallback suggestions if no real data yet
const FALLBACK_SUGGESTIONS = [
    'AI Indonesia',
    'Startup Jakarta',
    'Pilpres 2024',
    'E-sports Indonesia',
    'K-pop Fanbase',
    'Crypto Indonesia',
];

export default function HomeContent({ onQuickSearch }) {
    const [popularSearches, setPopularSearches] = useState([]);

    useEffect(() => {
        fetchPopularSearches();
    }, []);

    const fetchPopularSearches = async () => {
        try {
            const response = await fetch('/api/popular-searches?limit=8');
            const data = await response.json();
            if (data.success && data.searches.length > 0) {
                setPopularSearches(data.searches);
            }
        } catch (err) {
            console.error('Failed to fetch popular searches:', err);
        }
    };

    const suggestions = popularSearches.length > 0
        ? popularSearches.map(s => s.keyword)
        : FALLBACK_SUGGESTIONS;

    return (
        <div className="home-wrap">
            {/* How It Works */}
            <section className="home-section">
                <div className="home-section-header">
                    <span className="home-section-num">I</span>
                    <h2 className="home-section-title">Cara Kerja</h2>
                </div>
                <div className="home-divider" />
                <div className="home-steps">
                    <div className="home-step">
                        <span className="home-step-num">01</span>
                        <h3 className="home-step-title">Masukkan Kata Kunci</h3>
                        <p className="home-step-desc">Ketik topik yang ingin Anda telusuri di media sosial dan internet</p>
                    </div>
                    <div className="home-step">
                        <span className="home-step-num">02</span>
                        <h3 className="home-step-title">Pilih Platform</h3>
                        <p className="home-step-desc">Twitter, Reddit, YouTube, GitHub, dan 5 platform lainnya tersedia</p>
                    </div>
                    <div className="home-step">
                        <span className="home-step-num">03</span>
                        <h3 className="home-step-title">Analisis Sentimen</h3>
                        <p className="home-step-desc">AI menganalisis sentimen publik: positif, negatif, atau netral</p>
                    </div>
                </div>
            </section>

            {/* Quick Search */}
            <section className="home-section">
                <div className="home-section-header">
                    <span className="home-section-num">II</span>
                    <h2 className="home-section-title">Pencarian Populer</h2>
                    {popularSearches.length > 0 && (
                        <span className="home-section-live">
                            <i className="fa-solid fa-circle" /> real-time
                        </span>
                    )}
                </div>
                <div className="home-divider" />
                <div className="home-chips">
                    {suggestions.map((kw) => (
                        <button
                            key={kw}
                            className="home-chip"
                            onClick={() => onQuickSearch(kw)}
                        >
                            {kw}
                            {popularSearches.find(s => s.keyword === kw) && (
                                <span className="home-chip-count">
                                    {popularSearches.find(s => s.keyword === kw).count}
                                </span>
                            )}
                        </button>
                    ))}
                </div>
            </section>

            {/* Platform Showcase */}
            <section className="home-section">
                <div className="home-section-header">
                    <span className="home-section-num">III</span>
                    <h2 className="home-section-title">Platform yang Didukung</h2>
                </div>
                <div className="home-divider" />
                <div className="home-platforms">
                    {PLATFORMS.map((p) => (
                        <div key={p.id} className="home-platform">
                            <i className={`${p.icon} home-platform-icon`} />
                            <div>
                                <div className="home-platform-name">{p.name}</div>
                                <div className="home-platform-desc">{p.desc}</div>
                            </div>
                        </div>
                    ))}
                </div>
            </section>
        </div>
    );
}
