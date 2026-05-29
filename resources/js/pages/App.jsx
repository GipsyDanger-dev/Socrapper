import React, { useState } from 'react';
import InputSection from '../components/InputSection';
import RawDataTab from '../components/RawDataTab';
import SentimentTab from '../components/SentimentTab';
import StatisticsTab from '../components/StatisticsTab';
import HistoryTab from '../components/HistoryTab';
import SurfResultsTab from '../components/SurfResultsTab';
import AiAnalysisCard from '../components/AiAnalysisCard';
import LoadingIndicator from '../components/LoadingIndicator';

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

    // Surf state
    const [surfResults, setSurfResults] = useState(null);
    const [aiAnalysis, setAiAnalysis] = useState(null);
    const [aiLoading, setAiLoading] = useState(false);

    const handleScrape = async (platform, keyword, limit) => {
        setLoading(true);
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
                setData(result.data);

                // Analisis sentimen
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
                if (analysisResult.success) {
                    setAnalysis(analysisResult.analysis);
                }

                // Hitung statistik
                calculateStatistics(result.data);
                setActiveTab('raw-data');
            } else {
                alert('Error: ' + result.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Terjadi kesalahan saat scraping');
        } finally {
            setLoading(false);
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
                setActiveTab('raw-data');
            } catch (error) {
                console.error('Error loading history:', error);
            } finally {
                setLoading(false);
            }
        }
    };

    const handleSurf = async (query, options) => {
        setLoading(true);
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

            console.log('Surf response status:', response.status);
            const result = await response.json();
            console.log('Surf result:', result);

            if (result.success) {
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

        setStatistics({
            total: dataItems.length,
            totalLikes,
            totalComments,
            totalShares,
            avgLikes: (totalLikes / dataItems.length).toFixed(1),
            avgComments: (totalComments / dataItems.length).toFixed(1),
            avgShares: (totalShares / dataItems.length).toFixed(1),
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

                alert('✅ File berhasil didownload!');
            } else {
                alert('❌ Error: Gagal export file');
            }
        } catch (error) {
            console.error('Export error:', error);
            alert('Terjadi kesalahan saat export');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="app">
            <LoadingIndicator show={loading} />

            <header className="header">
                <div className="header-content">
                    <h1><i className="fas fa-globe"></i> Socrapper</h1>
                    <p>
                        {currentMode === 'scraper'
                            ? 'Social Media Sentiment Analysis Tool'
                            : '🌐 Internet Surfing & Sentiment Analysis'
                        }
                    </p>
                </div>
            </header>

            <main className="main-content">
                <div className="content-grid">
                    <InputSection onScrape={handleScrape} onSurf={handleSurf} />

                    <section className="results-section">
                        <div className="tabs">
                            {currentMode === 'scraper' ? (
                                <>
                                    <button
                                        className={`tab-btn ${activeTab === 'raw-data' ? 'active' : ''}`}
                                        onClick={() => setActiveTab('raw-data')}
                                    >
                                        📊 Data Mentah
                                    </button>
                                    <button
                                        className={`tab-btn ${activeTab === 'sentiment' ? 'active' : ''}`}
                                        onClick={() => setActiveTab('sentiment')}
                                    >
                                        😊 Analisis Sentimen
                                    </button>
                                    <button
                                        className={`tab-btn ${activeTab === 'statistics' ? 'active' : ''}`}
                                        onClick={() => setActiveTab('statistics')}
                                    >
                                        📈 Statistik
                                    </button>
                                    <button
                                        className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
                                        onClick={() => setActiveTab('history')}
                                    >
                                        📋 History
                                    </button>
                                </>
                            ) : (
                                <>
                                    <button
                                        className={`tab-btn ${activeTab === 'surf-results' ? 'active' : ''}`}
                                        onClick={() => setActiveTab('surf-results')}
                                    >
                                        🌐 Hasil Surfing
                                    </button>
                                    {analysis && (
                                        <button
                                            className={`tab-btn ${activeTab === 'sentiment' ? 'active' : ''}`}
                                            onClick={() => setActiveTab('sentiment')}
                                        >
                                            😊 Analisis Sentimen
                                        </button>
                                    )}
                                </>
                            )}
                        </div>

                        {data.length > 0 && currentMode === 'scraper' && (
                            <div className="export-buttons">
                                <button
                                    className="btn-export"
                                    onClick={() => handleExportData('scraping')}
                                    title="Export raw data to CSV"
                                >
                                    📥 Export Raw Data
                                </button>
                                {analysis && (
                                    <button
                                        className="btn-export"
                                        onClick={() => handleExportData('analysis')}
                                        title="Export sentiment analysis to CSV"
                                    >
                                        📥 Export Sentiment
                                    </button>
                                )}
                                {statistics && (
                                    <button
                                        className="btn-export"
                                        onClick={() => handleExportData('statistics')}
                                        title="Export statistics to CSV"
                                    >
                                        📥 Export Statistics
                                    </button>
                                )}
                            </div>
                        )}

                        {activeTab === 'raw-data' && currentMode === 'scraper' && (
                            <RawDataTab data={data} />
                        )}
                        {activeTab === 'surf-results' && currentMode === 'surfer' && (
                            <>
                                <SurfResultsTab results={surfResults} />
                                {surfResults && surfResults.total_results > 0 && (
                                    <div className="ai-analysis-section">
                                        <div className="ai-buttons">
                                            <button 
                                                className="btn-ai" 
                                                onClick={() => handleAiAnalyze('general')}
                                                disabled={aiLoading}
                                            >
                                                {aiLoading ? '⏳ AI sedang analisis...' : '🤖 AI General Analysis'}
                                            </button>
                                            <button 
                                                className="btn-ai btn-ai-market" 
                                                onClick={() => handleAiAnalyze('market')}
                                                disabled={aiLoading}
                                            >
                                                {aiLoading ? '⏳ AI sedang analisis...' : '📈 AI Market Analysis'}
                                            </button>
                                        </div>
                                        {aiAnalysis && <AiAnalysisCard analysis={aiAnalysis} />}
                                    </div>
                                )}
                            </>
                        )}
                        {activeTab === 'sentiment' && <SentimentTab analysis={analysis} />}
                        {activeTab === 'history' && currentMode === 'scraper' && (
                            <HistoryTab
                                key={historyRefreshKey}
                                onLoadHistory={handleLoadHistory}
                                onRefresh={() => setHistoryRefreshKey(k => k + 1)}
                            />
                        )}
                        {activeTab === 'statistics' && currentMode === 'scraper' && (
                            <StatisticsTab statistics={statistics} />
                        )}
                    </section>
                </div>
            </main>
        </div>
    );
}
