import React, { useState, useEffect } from 'react';
import InputSection from '../components/InputSection';
import RawDataTab from '../components/RawDataTab';
import SentimentTab from '../components/SentimentTab';
import StatisticsTab from '../components/StatisticsTab';
import LoadingIndicator from '../components/LoadingIndicator';

export default function App() {
    const [activeTab, setActiveTab] = useState('raw-data');
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState([]);
    const [analysis, setAnalysis] = useState(null);
    const [statistics, setStatistics] = useState(null);
    const [currentPlatform, setCurrentPlatform] = useState('');
    const [currentKeyword, setCurrentKeyword] = useState('');

    const handleScrape = async (platform, keyword, limit) => {
        setLoading(true);
        setCurrentPlatform(platform);
        setCurrentKeyword(keyword);
        
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
                    method: 'webscrape', // Use web scraping by default
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
                // Download file
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
                    <p>Social Media Sentiment Analysis Tool (Web Scraping)</p>
                </div>
            </header>

            <main className="main-content">
                <div className="content-grid">
                    <InputSection onScrape={handleScrape} />

                    <section className="results-section">
                        <div className="tabs">
                            <button
                                className={`tab-btn ${activeTab === 'raw-data' ? 'active' : ''}`}
                                onClick={() => setActiveTab('raw-data')}
                            >
                                Data Mentah
                            </button>
                            <button
                                className={`tab-btn ${activeTab === 'sentiment' ? 'active' : ''}`}
                                onClick={() => setActiveTab('sentiment')}
                            >
                                Analisis Sentimen
                            </button>
                            <button
                                className={`tab-btn ${activeTab === 'statistics' ? 'active' : ''}`}
                                onClick={() => setActiveTab('statistics')}
                            >
                                Statistik
                            </button>
                        </div>

                        {data.length > 0 && (
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

                        {activeTab === 'raw-data' && <RawDataTab data={data} />}
                        {activeTab === 'sentiment' && <SentimentTab analysis={analysis} />}
                        {activeTab === 'statistics' && <StatisticsTab statistics={statistics} />}
                    </section>
                </div>
            </main>
        </div>
    );
}
