import React, { useState, useEffect } from 'react';

export default function InputSection({ onScrape, onSurf }) {
    const [mode, setMode] = useState('scraper');
    const [platform, setPlatform] = useState('');
    const [keyword, setKeyword] = useState('');
    const [limit, setLimit] = useState(50);
    const [platforms, setPlatforms] = useState({});
    const [loading, setLoading] = useState(false);

    // Surf options
    const [surfMode, setSurfMode] = useState('full');
    const [searchLimit, setSearchLimit] = useState(15);
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
            alert('Masukkan keyword terlebih dahulu!');
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
        <div className="inp-sec">
            <p className="sec-lbl">
                {mode === 'scraper' ? 'Konfigurasi Scraping' : 'Internet Surfing'}
            </p>

            {/* Mode Switcher */}
            <div className="mode-row">
                <button
                    className={`mode-btn ${mode === 'scraper' ? 'active' : ''}`}
                    onClick={() => setMode('scraper')}
                >
                    Social Media Scraper
                </button>
                <button
                    className={`mode-btn ${mode === 'surfer' ? 'active' : ''}`}
                    onClick={() => setMode('surfer')}
                >
                    Internet Surfer
                </button>
            </div>

            <form onSubmit={handleSubmit}>
                {/* Scraper Mode */}
                {mode === 'scraper' && (
                    <>
                        <div className="sr">
                            <input
                                type="text"
                                value={keyword}
                                onChange={(e) => setKeyword(e.target.value)}
                                placeholder="masukkan kata kunci..."
                            />
                            <input
                                type="number"
                                value={limit}
                                onChange={(e) => setLimit(parseInt(e.target.value))}
                                min="1"
                                max="200"
                            />
                            <button type="submit" disabled={loading}>
                                {loading ? 'memuat...' : 'scrape →'}
                            </button>
                        </div>
                        <div className="plats">
                            {Object.entries(platforms).map(([key, value]) => (
                                <button
                                    key={key}
                                    type="button"
                                    className={`plat ${platform === key ? 'on' : ''}`}
                                    onClick={() => setPlatform(key)}
                                >
                                    {value}
                                </button>
                            ))}
                        </div>
                    </>
                )}

                {/* Surfer Mode */}
                {mode === 'surfer' && (
                    <>
                        <div className="sr">
                            <input
                                type="text"
                                value={keyword}
                                onChange={(e) => setKeyword(e.target.value)}
                                placeholder="apa yang ingin kamu cari..."
                            />
                            <button type="submit" disabled={loading}>
                                {loading ? 'memuat...' : 'surf →'}
                            </button>
                        </div>
                        <div className="plats">
                            <button
                                type="button"
                                className={`plat ${surfMode === 'quick' ? 'on' : ''}`}
                                onClick={() => setSurfMode('quick')}
                            >
                                Quick
                            </button>
                            <button
                                type="button"
                                className={`plat ${surfMode === 'full' ? 'on' : ''}`}
                                onClick={() => setSurfMode('full')}
                            >
                                Full
                            </button>
                            <button
                                type="button"
                                className={`plat ${surfMode === 'deep' ? 'on' : ''}`}
                                onClick={() => setSurfMode('deep')}
                            >
                                Deep
                            </button>
                            {surfMode !== 'deep' && (
                                <span className="limit-row">
                                    <span className="limit-label">sumber:</span>
                                    <input
                                        type="number"
                                        className="limit-input"
                                        value={searchLimit}
                                        onChange={(e) => setSearchLimit(parseInt(e.target.value))}
                                        min="1"
                                        max="50"
                                    />
                                </span>
                            )}
                        </div>
                    </>
                )}
            </form>
        </div>
    );
}
