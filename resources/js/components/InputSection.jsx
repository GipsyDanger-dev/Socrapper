import React, { useState, useEffect } from 'react';

export default function InputSection({ onScrape, onSurf }) {
    const [mode, setMode] = useState('scraper'); // 'scraper' atau 'surfer'
    const [platform, setPlatform] = useState('');
    const [keyword, setKeyword] = useState('');
    const [limit, setLimit] = useState(50);
    const [platforms, setPlatforms] = useState({});
    const [loading, setLoading] = useState(false);

    // Surf options
    const [surfMode, setSurfMode] = useState('full'); // 'quick', 'full', 'deep'
    const [searchLimit, setSearchLimit] = useState(5);
    const [extractContent, setExtractContent] = useState(true);
    const [analyzeSentiment, setAnalyzeSentiment] = useState(true);

    useEffect(() => {
        if (mode === 'scraper') {
            loadPlatforms();
        }
    }, [mode]);

    const loadPlatforms = async () => {
        try {
            const response = await fetch('/api/platforms');
            const data = await response.json();
            setPlatforms(data.platforms || {});
        } catch (error) {
            console.error('Error loading platforms:', error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!keyword) {
            alert('Masukkan keyword/pertanyaan terlebih dahulu!');
            return;
        }

        if (mode === 'scraper' && !platform) {
            alert('Pilih platform terlebih dahulu!');
            return;
        }

        setLoading(true);
        try {
            if (mode === 'scraper') {
                await onScrape(platform, keyword, limit);
            } else {
                await onSurf(keyword, {
                    mode: surfMode,
                    searchLimit,
                    extractContent,
                    analyzeSentiment,
                });
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <section className="input-section">
            <h2>
                {mode === 'scraper' ? '🔍 Konfigurasi Scraping' : '🌐 Internet Surfing'}
            </h2>

            {/* Mode Switcher */}
            <div className="mode-switcher">
                <button
                    className={`mode-btn ${mode === 'scraper' ? 'active' : ''}`}
                    onClick={() => setMode('scraper')}
                >
                    📊 Social Media Scraper
                </button>
                <button
                    className={`mode-btn ${mode === 'surfer' ? 'active' : ''}`}
                    onClick={() => setMode('surfer')}
                >
                    🌐 Internet Surfer
                </button>
            </div>

            <form onSubmit={handleSubmit}>
                {/* Scraper Mode */}
                {mode === 'scraper' && (
                    <>
                        <div className="form-group">
                            <label htmlFor="platform">Platform Media Sosial:</label>
                            <select
                                id="platform"
                                className="form-control"
                                value={platform}
                                onChange={(e) => setPlatform(e.target.value)}
                            >
                                <option value="">-- Pilih Platform --</option>
                                {Object.entries(platforms).map(([key, value]) => (
                                    <option key={key} value={key}>
                                        {value}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className="form-group">
                            <label htmlFor="keyword">Keyword/Hashtag:</label>
                            <input
                                type="text"
                                id="keyword"
                                className="form-control"
                                placeholder="Masukkan keyword..."
                                value={keyword}
                                onChange={(e) => setKeyword(e.target.value)}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="limit">Jumlah Data:</label>
                            <input
                                type="number"
                                id="limit"
                                className="form-control"
                                value={limit}
                                onChange={(e) => setLimit(parseInt(e.target.value))}
                                min="1"
                                max="1000"
                            />
                        </div>
                    </>
                )}

                {/* Surfer Mode */}
                {mode === 'surfer' && (
                    <>
                        <div className="form-group">
                            <label htmlFor="query">🔍 Apa yang ingin kamu cari?</label>
                            <input
                                type="text"
                                id="query"
                                className="form-control"
                                placeholder="Contoh: berita terbaru AI, review iPhone 16, analisis saham BBCA..."
                                value={keyword}
                                onChange={(e) => setKeyword(e.target.value)}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="surfMode">Mode Pencarian:</label>
                            <select
                                id="surfMode"
                                className="form-control"
                                value={surfMode}
                                onChange={(e) => setSurfMode(e.target.value)}
                            >
                                <option value="quick">⚡ Quick - Cepat, cuma search results</option>
                                <option value="full">🔍 Full - Search + extract konten</option>
                                <option value="deep">🧠 Deep - Multiple queries + analisis mendalam</option>
                            </select>
                        </div>

                        {surfMode !== 'deep' && (
                            <div className="form-group">
                                <label htmlFor="searchLimit">Jumlah Sumber:</label>
                                <input
                                    type="number"
                                    id="searchLimit"
                                    className="form-control"
                                    value={searchLimit}
                                    onChange={(e) => setSearchLimit(parseInt(e.target.value))}
                                    min="1"
                                    max="10"
                                />
                            </div>
                        )}

                        {surfMode === 'full' && (
                            <div className="form-group checkbox-group">
                                <label>
                                    <input
                                        type="checkbox"
                                        checked={extractContent}
                                        onChange={(e) => setExtractContent(e.target.checked)}
                                    />
                                    📄 Extract konten halaman
                                </label>
                                <label>
                                    <input
                                        type="checkbox"
                                        checked={analyzeSentiment}
                                        onChange={(e) => setAnalyzeSentiment(e.target.checked)}
                                    />
                                    📊 Analisis sentimen
                                </label>
                            </div>
                        )}
                    </>
                )}

                <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading}
                >
                    {loading ? (
                        <>⏳ Sedang {mode === 'scraper' ? 'scraping' : 'surfing'}...</>
                    ) : mode === 'scraper' ? (
                        <><i className="fas fa-search"></i> Mulai Scraping</>
                    ) : (
                        <><i className="fas fa-globe"></i> Surfing Sekarang</>
                    )}
                </button>
            </form>

            {/* Info Box */}
            {mode === 'surfer' && (
                <div className="info-box">
                    <p><strong>💡 Tips:</strong></p>
                    <ul>
                        <li><strong>Quick:</strong> Cari informasi cepat tanpa buka halaman</li>
                        <li><strong>Full:</strong> Baca konten lengkap dari setiap sumber</li>
                        <li><strong>Deep:</strong> Analisis mendalam dari berbagai sudut pandang</li>
                    </ul>
                </div>
            )}
        </section>
    );
}
