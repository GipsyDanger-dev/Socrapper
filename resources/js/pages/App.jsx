import React, { useState, useCallback } from 'react';
import InputSection from '../components/InputSection';
import RawDataTab from '../components/RawDataTab';
import SentimentTab from '../components/SentimentTab';
import StatisticsTab from '../components/StatisticsTab';
import HistoryTab from '../components/HistoryTab';
import SurfResultsTab from '../components/SurfResultsTab';
import AiAnalysisCard from '../components/AiAnalysisCard';
import LoadingIndicator from '../components/LoadingIndicator';
import HomeContent from '../components/HomeContent';
import HomeSidebar from '../components/HomeSidebar';
import SocrapperLoader from '../components/SocrapperLoader';

// Toast notification component
function Toast({ message, type, onClose }) {
    if (!message) return null;
    return (
        <div role="alert" aria-live="assertive" style={{
            position: 'fixed', top: '20px', right: '20px', zIndex: 10000,
            padding: '12px 20px', maxWidth: '420px',
            background: type === 'error' ? '#dc3545' : '#198754',
            color: '#fff', fontSize: '13px', fontFamily: "'Playfair Display', serif",
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px',
        }}>
            <span>{message}</span>
            <button onClick={onClose} style={{
                background: 'none', border: 'none', color: '#fff', cursor: 'pointer',
                fontSize: '16px', padding: '0 4px', opacity: 0.8,
            }}>×</button>
        </div>
    );
}

async function fetchJSON(url, options = {}) {
    const controller = new AbortController();
    const timeout = options.timeout || 60000;
    const timer = setTimeout(() => controller.abort(), timeout);
    try {
        const response = await fetch(url, { ...options, signal: controller.signal });
        if (!response.ok) {
            let errorMsg = `HTTP ${response.status}`;
            try {
                const errData = await response.json();
                errorMsg = errData.error || errData.detail || errorMsg;
            } catch {}
            throw new Error(errorMsg);
        }
        return await response.json();
    } finally {
        clearTimeout(timer);
    }
}

export default function App() {
    const [loaded, setLoaded] = useState(false);
    const [activeTab, setActiveTab] = useState('raw-data');
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState([]);
    const [analysis, setAnalysis] = useState(null);
    const [statistics, setStatistics] = useState(null);
    const [currentPlatform, setCurrentPlatform] = useState('');
    const [currentKeyword, setCurrentKeyword] = useState('');
    const [currentMode, setCurrentMode] = useState('scraper');
    const [historyRefreshKey, setHistoryRefreshKey] = useState(0);
    const [loadingStage, setLoadingStage] = useState(null);
    const [toast, setToast] = useState({ message: '', type: 'error' });

    // Surf state
    const [surfResults, setSurfResults] = useState(null);
    const [aiAnalysis, setAiAnalysis] = useState(null);
    const [aiLoading, setAiLoading] = useState(false);

    const showToast = useCallback((message, type = 'error') => {
        setToast({ message, type });
        setTimeout(() => setToast({ message: '', type: 'error' }), 5000);
    }, []);

    const handleScrape = async (platform, keyword, limit) => {
        setLoading(true);
        setLoadingStage('collecting');
        setCurrentPlatform(platform);
        setCurrentKeyword(keyword);
        setCurrentMode('scraper');
        setSurfResults(null);

        try {
            const result = await fetchJSON('/api/scrape', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                body: JSON.stringify({ platform, keyword, limit, method: 'webscrape' }),
                timeout: 120000,
            });

            if (result.success) {
                setLoadingStage('analyzing');

                const analysisResult = await fetchJSON('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                    body: JSON.stringify({ texts: result.data.map(item => item.text) }),
                    timeout: 60000,
                });

                setLoadingStage('assembling');

                setData(result.data);
                if (analysisResult.success) {
                    setAnalysis(analysisResult.analysis);
                }

                calculateStatistics(result.data);
                setActiveTab('sentiment');
            } else {
                showToast(result.error || 'Scraping gagal');
            }
        } catch (error) {
            console.error('Error:', error);
            showToast(error.name === 'AbortError' ? 'Request timeout — coba lagi' : error.message);
        } finally {
            setLoading(false);
            setLoadingStage(null);
        }
    };

    const handleLoadHistory = async (item) => {
        if (item.raw_data && item.raw_data.length > 0) {
            setLoading(true);
            try {
                setData(item.raw_data);
                setCurrentPlatform(item.platform);
                setCurrentKeyword(item.keyword);
                setCurrentMode('scraper');

                const analysisResult = await fetchJSON('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                    body: JSON.stringify({ texts: item.raw_data.map(d => d.text) }),
                    timeout: 60000,
                });
                if (analysisResult.success) {
                    setAnalysis(analysisResult.analysis);
                }

                calculateStatistics(item.raw_data);
                setActiveTab('sentiment');
            } catch (error) {
                console.error('Error loading history:', error);
                showToast('Gagal memuat history: ' + error.message);
            } finally {
                setLoading(false);
            }
        }
    };

    const handleSurf = async (query, options) => {
        setLoading(true);
        setLoadingStage('collecting');
        setCurrentKeyword(query);
        setCurrentMode('surfer');
        setData([]);
        setAnalysis(null);
        setStatistics(null);

        try {
            let endpoint = '/api/surf';
            let body = { query };

            if (options.mode === 'quick') {
                endpoint = '/api/surf/quick';
                body.limit = options.searchLimit;
            } else if (options.mode === 'deep') {
                endpoint = '/api/surf/deep';
                body.pages = 3;
            } else {
                body.search_limit = options.searchLimit;
                body.extract_content = options.extractContent;
                body.analyze_sentiment = options.analyzeSentiment;
            }

            const result = await fetchJSON(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify(body),
                timeout: 120000,
            });

            if (result.success) {
                setLoadingStage('assembling');
                setSurfResults(result);
                setAnalysis(result.sentiment || null);
                setAiAnalysis(null);
                setActiveTab('surf-results');
            } else {
                showToast(result.error || 'Gagal surfing');
            }
        } catch (error) {
            console.error('Surf error:', error);
            showToast(error.name === 'AbortError' ? 'Request timeout — coba lagi' : error.message);
        } finally {
            setLoading(false);
            setLoadingStage(null);
        }
    };

    const handleAiAnalyze = async (type = 'general') => {
        if (!surfResults) return;

        const articles = surfResults.merged_results || surfResults.results || surfResults.search_results || [];
        if (articles.length === 0) {
            showToast('Tidak ada data untuk dianalisis');
            return;
        }

        setAiLoading(true);
        try {
            const result = await fetchJSON('/api/surf/ai-analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify({
                    query: currentKeyword,
                    articles: articles.slice(0, 5),
                    type: type,
                }),
                timeout: 120000,
            });

            if (result.success) {
                setAiAnalysis(result.ai_analysis);
            } else {
                showToast(result.error || 'Gagal analisis AI');
            }
        } catch (error) {
            console.error('AI error:', error);
            showToast(error.name === 'AbortError' ? 'AI analysis timeout' : error.message);
        } finally {
            setAiLoading(false);
        }
    };

    const calculateStatistics = (dataItems) => {
        if (!dataItems || dataItems.length === 0) return;

        const totalLikes = dataItems.reduce((sum, item) => sum + (item.likes || 0), 0);
        const totalComments = dataItems.reduce((sum, item) => sum + (item.comments || 0), 0);
        const totalShares = dataItems.reduce((sum, item) => sum + (item.shares || 0), 0);
        const totalWords = dataItems.reduce((sum, item) => sum + (item.text ? item.text.split(/\s+/).length : 0), 0);

        const platforms = {};
        dataItems.forEach(item => {
            const p = item.platform || 'unknown';
            platforms[p] = (platforms[p] || 0) + 1;
        });

        const sources = new Set(dataItems.map(item => item.author || item.source || '').filter(Boolean));

        const sentiments = { positive: 0, negative: 0, neutral: 0 };
        dataItems.forEach(item => {
            const s = (item.sentiment || '').toLowerCase();
            if (s === 'positive' || s === 'positif') sentiments.positive++;
            else if (s === 'negative' || s === 'negatif') sentiments.negative++;
            else sentiments.neutral++;
        });

        setStatistics({
            total: dataItems.length,
            totalLikes,
            totalComments,
            totalShares,
            avgLikes: (totalLikes / dataItems.length).toFixed(1),
            avgComments: (totalComments / dataItems.length).toFixed(1),
            avgShares: (totalShares / dataItems.length).toFixed(1),
            totalWords,
            avgWords: Math.round(totalWords / dataItems.length),
            platforms,
            uniqueSources: sources.size,
            sentiments,
        });
    };

    const handleExportData = async (type) => {
        try {
            setLoading(true);

            let exportData = {};
            if (type === 'scraping') {
                exportData = data;
            } else if (type === 'analysis') {
                exportData = { data, analysis };
            } else if (type === 'statistics') {
                exportData = statistics;
            }

            const controller = new AbortController();
            const timer = setTimeout(() => controller.abort(), 30000);
            const response = await fetch('/api/export', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    data: exportData,
                    type: type,
                    filename: `${type}_${currentKeyword}_${new Date().toISOString().slice(0, 10)}.csv`,
                }),
                signal: controller.signal,
            });
            clearTimeout(timer);

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${type}_${currentKeyword}.csv`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else {
                showToast('Gagal export file');
            }
        } catch (error) {
            console.error('Export error:', error);
            showToast(error.name === 'AbortError' ? 'Export timeout' : 'Gagal export: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    const hasData = data.length > 0 || surfResults;

    if (!loaded) {
        return <SocrapperLoader onDone={() => setLoaded(true)} />;
    }

    return (
        <div className="root">
            <Toast message={toast.message} type={toast.type} onClose={() => setToast({ message: '', type: 'error' })} />

            {/* Masthead */}
            <header className="mh">
                <div>
                    <h1 className="logo">Socrapper</h1>
                    <p className="tag">
                        {currentMode === 'scraper'
                            ? 'Social Media Sentiment Scraper'
                            : 'Internet Surfing & Sentiment Analysis'
                        }
                    </p>
                </div>
                <div className="mh-meta">
                    {new Date().toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
                    <br />9 Platforms
                </div>
            </header>

            {/* Skip to content link for accessibility */}
            <a href="#main-content" className="skip-link" style={{
                position: 'absolute', left: '-9999px', top: 'auto', width: '1px', height: '1px', overflow: 'hidden',
            }}>Langsung ke konten utama</a>

            {/* Issue bar */}
            {currentKeyword && (
                <div className="ib">
                    <span className="it">query: <strong>"{currentKeyword}"</strong></span>
                    <span className="it">hasil: <strong>{data.length || (surfResults?.total_results || 0)}</strong></span>
                    <span className="it">platform: <strong>{currentPlatform || 'multi'}</strong></span>
                </div>
            )}

            {/* Input */}
            <InputSection onScrape={handleScrape} onSurf={handleSurf} />

            {/* Home content (before scraping) */}
            {!hasData && (
                <div className="home-grid">
                    <div className="home-main">
                        <HomeContent onQuickSearch={(kw) => handleScrape('news', kw, 10)} />
                    </div>
                    <aside className="home-sidebar">
                        <HomeSidebar />
                    </aside>
                </div>
            )}

            {/* Loading */}
            <LoadingIndicator show={loading} keyword={currentKeyword} stage={loadingStage} />

            {/* Main content */}
            <main id="main-content">
                {/* Tabs + panels */}
                {hasData && (
                    <div className="tabs-wrap">
                        <nav className="tabs-bar" role="tablist" aria-label="Navigasi konten">
                            {currentMode === 'scraper' ? (
                                <>
                                    <button
                                        role="tab"
                                        aria-selected={activeTab === 'sentiment'}
                                        aria-controls="panel-sentiment"
                                        className={`tab ${activeTab === 'sentiment' ? 'on' : ''}`}
                                        onClick={() => setActiveTab('sentiment')}
                                    >
                                        Sentimen
                                    </button>
                                    <button
                                        role="tab"
                                        aria-selected={activeTab === 'raw-data'}
                                        aria-controls="panel-raw-data"
                                        className={`tab ${activeTab === 'raw-data' ? 'on' : ''}`}
                                        onClick={() => setActiveTab('raw-data')}
                                    >
                                        Data Mentah
                                    </button>
                                    <button
                                        role="tab"
                                        aria-selected={activeTab === 'statistics'}
                                        aria-controls="panel-statistics"
                                        className={`tab ${activeTab === 'statistics' ? 'on' : ''}`}
                                        onClick={() => setActiveTab('statistics')}
                                    >
                                        Statistik
                                    </button>
                                    <button
                                        role="tab"
                                        aria-selected={activeTab === 'history'}
                                        aria-controls="panel-history"
                                        className={`tab ${activeTab === 'history' ? 'on' : ''}`}
                                        onClick={() => setActiveTab('history')}
                                    >
                                        History
                                    </button>
                                </>
                            ) : (
                                <>
                                    <button
                                        role="tab"
                                        aria-selected={activeTab === 'surf-results'}
                                        aria-controls="panel-surf"
                                        className={`tab ${activeTab === 'surf-results' ? 'on' : ''}`}
                                        onClick={() => setActiveTab('surf-results')}
                                    >
                                        Hasil Surfing
                                    </button>
                                    {analysis && (
                                        <button
                                            role="tab"
                                            aria-selected={activeTab === 'sentiment'}
                                            aria-controls="panel-sentiment"
                                            className={`tab ${activeTab === 'sentiment' ? 'on' : ''}`}
                                            onClick={() => setActiveTab('sentiment')}
                                        >
                                            Sentimen
                                        </button>
                                    )}
                                </>
                            )}
                            <span className="tab-rc" aria-live="polite">
                                {data.length || (surfResults?.total_results || 0)} hasil
                            </span>
                        </nav>

                        {/* PANEL: Sentiment */}
                        {activeTab === 'sentiment' && (
                            <div role="tabpanel" id="panel-sentiment">
                                <SentimentTab
                                    analysis={analysis}
                                    data={data}
                                    currentKeyword={currentKeyword}
                                    onExport={() => handleExportData('analysis')}
                                />
                            </div>
                        )}

                        {/* PANEL: Raw Data */}
                        {activeTab === 'raw-data' && currentMode === 'scraper' && (
                            <div role="tabpanel" id="panel-raw-data">
                                <RawDataTab
                                    data={data}
                                    onExport={() => handleExportData('scraping')}
                                />
                            </div>
                        )}

                        {/* PANEL: Statistics */}
                        {activeTab === 'statistics' && currentMode === 'scraper' && (
                            <div role="tabpanel" id="panel-statistics">
                                <StatisticsTab statistics={statistics} platform={currentPlatform} />
                            </div>
                        )}

                        {/* PANEL: History */}
                        {activeTab === 'history' && currentMode === 'scraper' && (
                            <div role="tabpanel" id="panel-history">
                                <HistoryTab
                                    key={historyRefreshKey}
                                    onLoadHistory={handleLoadHistory}
                                    onRefresh={() => setHistoryRefreshKey(k => k + 1)}
                                />
                            </div>
                        )}

                        {/* PANEL: Surf Results */}
                        {activeTab === 'surf-results' && currentMode === 'surfer' && (
                            <div role="tabpanel" id="panel-surf">
                                <SurfResultsTab results={surfResults} />
                                {surfResults && surfResults.total_results > 0 && (
                                    <div className="ai-section">
                                        <div className="ai-buttons">
                                            <button
                                                className="ai-btn"
                                                onClick={() => handleAiAnalyze('general')}
                                                disabled={aiLoading}
                                            >
                                                {aiLoading ? 'AI menganalisis...' : 'AI General Analysis'}
                                            </button>
                                            <button
                                                className="ai-btn"
                                                onClick={() => handleAiAnalyze('market')}
                                                disabled={aiLoading}
                                            >
                                                {aiLoading ? 'AI menganalisis...' : 'AI Market Analysis'}
                                            </button>
                                        </div>
                                        {aiAnalysis && <AiAnalysisCard analysis={aiAnalysis} />}
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Export row for scraper mode */}
                        {data.length > 0 && currentMode === 'scraper' && activeTab !== 'history' && (
                            <div className="exp-row">
                                <span className="exp-note">{data.length} baris · UTF-8</span>
                                <button className="exp-btn" onClick={() => handleExportData('scraping')}>
                                    ↓ CSV
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </main>

            <footer style={{
                textAlign: 'center', padding: '24px 16px', fontSize: '11px',
                color: 'var(--color-text-faded, #a89e8a)',
                fontFamily: "'Playfair Display', serif",
            }}>
                <p>Socrapper v2.0 — Analisis Sentimen Media Sosial & Internet berbasis AI</p>
                <p style={{ marginTop: '4px' }}>Scrape & analisis dari Twitter, Reddit, YouTube, Instagram, TikTok, GitHub, StackOverflow, dan berita.</p>
            </footer>
        </div>
    );
}
