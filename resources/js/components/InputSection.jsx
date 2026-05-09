import React, { useState, useEffect } from 'react';

export default function InputSection({ onScrape }) {
    const [platform, setPlatform] = useState('');
    const [keyword, setKeyword] = useState('');
    const [limit, setLimit] = useState(50);
    const [platforms, setPlatforms] = useState({});
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadPlatforms();
    }, []);

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

        if (!platform) {
            alert('Pilih platform terlebih dahulu!');
            return;
        }
        if (!keyword) {
            alert('Masukkan keyword terlebih dahulu!');
            return;
        }

        setLoading(true);
        try {
            await onScrape(platform, keyword, limit);
        } finally {
            setLoading(false);
        }
    };

    return (
        <section className="input-section">
            <h2>Konfigurasi Scraping</h2>

            <form onSubmit={handleSubmit}>
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
                        onKeyPress={(e) => e.key === 'Enter' && handleSubmit(e)}
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

                <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading}
                >
                    <i className="fas fa-search"></i> Mulai Scraping
                </button>
            </form>
        </section>
    );
}
