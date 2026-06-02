import React, { useState } from 'react';
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

export default function App() {
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

    // Surf state
    const [surfResults, setSurfResults] = useState(null);
    const [aiAnalysis, setAiAnalysis] = useState(null);
    const [aiLoading, setAiLoading] = useState(false);

    const handleScrape = async (platform, keyword, limit) => {
        setLoading(true);
        setLoadingStage('collecting');
        setCurrentPlatform(platform);
        setCurrentKeyword(keyword);
        setCurrentMode('scraper');
        setSurfResults(null);

        try {
            const response = await fetch('/api/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify({
                    platform,
                    keyword,
                    limit,
                    method: 'webscrape',
                }),
            });

            const result = await response.json();

            if (result.success) {
                setLoadingStage('analyzing');

                const analysisResponse = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                    },
                    body: JSON.stringify({
                        texts: result.data.map(item => item.text),
                    }),
                });

                const analysisResult = await analysisResponse.json();

                setLoadingStage('assembling');

                setData(result.data);
                if (analysisResult.success) {
                    setAnalysis(analysisResult.analysis);
                }

                calculateStatistics(result.data);
                setActiveTab('sentiment');
            } else {
                alert('Error: ' + result.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Terjadi kesalahan saat scraping');
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

                const analysisResponse = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                    },
                    body: JSON.stringify({ texts: item.raw_data.map(d => d.text) }),
                });
                const analysisResult = await analysisResponse.json();
                if (analysisResult.success) {
                    setAnalysis(analysisResult.analysis);
                }

                calculateStatistics(item.raw_data);
                setActiveTab('sentiment');
            } catch (error) {
                console.error('Error loading history:', error);
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

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify(body),
            });

            const result = await response.json();

            if (result.success) {
                setLoadingStage('assembling');
                setSurfResults(result);
                setAnalysis(result.sentiment || null);
                setAiAnalysis(null);
                setActiveTab('surf-results');
            } else {
                alert('Error: ' + (result.error || 'Gagal surfing'));
            }
        } catch (error) {
            console.error('Surf error:', error);
            alert('Terjadi kesalahan saat surfing');
        } finally {
            setLoading(false);
            setLoadingStage(null);
        }
    };

    const handleAiAnalyze = async (type = 'general') => {
        if (!surfResults) return;

        const articles = surfResults.merged_results || surfResults.results || surfResults.search_results || [];
        if (articles.length === 0) {
            alert('Tidak ada data untuk dianalisis');
            return;
        }

        setAiLoading(true);
        try {
            const response = await fetch('/api/surf/ai-analyze', {
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
            });

            const result = await response.json();
            if (result.success) {
                setAiAnalysis(result.ai_analysis);
            } else {
                alert('AI Error: ' + (result.error || 'Gagal analisis'));
            }
        } catch (error) {
            console.error('AI error:', error);
            alert('Terjadi kesalahan saat AI analysis');
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

            const response = await fetch('/api/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    data: exportData,
                    type: type,
                    filename: `${type}_${currentKeyword}_${new Date().toISOString().slice(0, 10)}.csv`,
                }),
            });

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
                alert('Error: Gagal export file');
            }
        } catch (error) {
            console.error('Export error:', error);
            alert('Terjadi kesalahan saat export');
        } finally {
            setLoading(false);
        }
    };

    const hasData = data.length > 0 || surfResults;

    return (
        <div className="root">
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

            {/* Tabs + panels */}
            {hasData && (
                <div className="tabs-wrap">
                    <div className="tabs-bar">
                        {currentMode === 'scraper' ? (
                            <>
                                <button
                                    className={`tab ${activeTab === 'sentiment' ? 'on' : ''}`}
                                    onClick={() => setActiveTab('sentiment')}
                                >
                                    Sentimen
                                </button>
                                <button
                                    className={`tab ${activeTab === 'raw-data' ? 'on' : ''}`}
                                    onClick={() => setActiveTab('raw-data')}
                                >
                                    Data Mentah
                                </button>
                                <button
                                    className={`tab ${activeTab === 'statistics' ? 'on' : ''}`}
                                    onClick={() => setActiveTab('statistics')}
                                >
                                    Statistik
                                </button>
                                <button
                                    className={`tab ${activeTab === 'history' ? 'on' : ''}`}
                                    onClick={() => setActiveTab('history')}
                                >
                                    History
                                </button>
                            </>
                        ) : (
                            <>
                                <button
                                    className={`tab ${activeTab === 'surf-results' ? 'on' : ''}`}
                                    onClick={() => setActiveTab('surf-results')}
                                >
                                    Hasil Surfing
                                </button>
                                {analysis && (
                                    <button
                                        className={`tab ${activeTab === 'sentiment' ? 'on' : ''}`}
                                        onClick={() => setActiveTab('sentiment')}
                                    >
                                        Sentimen
                                    </button>
                                )}
                            </>
                        )}
                        <span className="tab-rc">
                            {data.length || (surfResults?.total_results || 0)} hasil
                        </span>
                    </div>

                    {/* PANEL: Sentiment */}
                    {activeTab === 'sentiment' && (
                        <SentimentTab
                            analysis={analysis}
                            data={data}
                            currentKeyword={currentKeyword}
                            onExport={() => handleExportData('analysis')}
                        />
                    )}

                    {/* PANEL: Raw Data */}
                    {activeTab === 'raw-data' && currentMode === 'scraper' && (
                        <RawDataTab
                            data={data}
                            onExport={() => handleExportData('scraping')}
                        />
                    )}

                    {/* PANEL: Statistics */}
                    {activeTab === 'statistics' && currentMode === 'scraper' && (
                        <StatisticsTab statistics={statistics} platform={currentPlatform} />
                    )}

                    {/* PANEL: History */}
                    {activeTab === 'history' && currentMode === 'scraper' && (
                        <HistoryTab
                            key={historyRefreshKey}
                            onLoadHistory={handleLoadHistory}
                            onRefresh={() => setHistoryRefreshKey(k => k + 1)}
                        />
                    )}

                    {/* PANEL: Surf Results */}
                    {activeTab === 'surf-results' && currentMode === 'surfer' && (
                        <>
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
                        </>
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
        </div>
    );
}
