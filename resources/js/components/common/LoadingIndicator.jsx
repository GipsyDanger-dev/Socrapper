import React, { useState, useEffect, useRef } from 'react';

const STAGES = [
    { key: 'collecting', label: 'mengumpulkan', progress: 100 },
    { key: 'analyzing', label: 'menganalisis', progress: 100 },
    { key: 'assembling', label: 'menyusun', progress: 100 },
];

// Stage-specific rotating status messages (newsroom flavor)
const STATUS_MESSAGES = {
    collecting: [
        'menghubungi sumber...',
        'menyisir Google News & web...',
        'mengambil headline terbaru...',
        'mencari hasil di banyak platform...',
    ],
    analyzing: [
        'membaca setiap baris teks...',
        'mendeteksi sentimen & emosi...',
        'menghitung keyword positif/negatif...',
        'membandingkan konteks kalimat...',
    ],
    assembling: [
        'menyusun data ke dalam tabel...',
        'menggabungkan hasil dengan sumber...',
        'merapikan layout laporan...',
        'menyiapkan statistik ringkas...',
    ],
};

// Rotating ticker of pseudo-activity lines shown under the bars
const ACTIVITY_TICKER = [
    '📰 melewati halaman berita',
    '🔍 memeriksa kata kunci',
    '📝 mencatat 12 sumber baru',
    '⚡ mempercepat pengambilan data',
    '🧠 menyiapkan analisis sentimen',
    '📊 menghitung distribusi opini',
    '🌐 menelusuri platform lain',
    '✅ verifikasi data selesai',
];

function getStageIndex(stage) {
    const idx = STAGES.findIndex(s => s.key === stage);
    return idx >= 0 ? idx : -1;
}

export default function LoadingIndicator({ show, keyword, stage }) {
    const currentIdx = getStageIndex(stage);
    const [typeIdx, setTypeIdx] = useState(0);
    const [msgIdx, setMsgIdx] = useState(0);
    const [tickerIdx, setTickerIdx] = useState(0);
    const [progress, setProgress] = useState(0);

    // Reset progress whenever a new stage starts
    useEffect(() => {
        if (show && currentIdx >= 0) {
            setProgress(0);
            const interval = setInterval(() => {
                setProgress(p => Math.min(p + Math.random() * 18 + 6, 92));
            }, 380);
            return () => clearInterval(interval);
        }
    }, [show, stage, currentIdx]);

    // Rotate status messages
    useEffect(() => {
        if (!show) return;
        const interval = setInterval(() => setMsgIdx(i => (i + 1) % 4), 2600);
        return () => clearInterval(interval);
    }, [show, stage]);

    // Rotate ticker lines
    useEffect(() => {
        if (!show) return;
        const interval = setInterval(() => setTickerIdx(i => (i + 1) % ACTIVITY_TICKER.length), 1800);
        return () => clearInterval(interval);
    }, [show]);

    // Typewriter effect for the keyword
    useEffect(() => {
        if (!show) return;
        const full = keyword || '...';
        let i = 0;
        setTypeIdx(0);
        const interval = setInterval(() => {
            i += 1;
            setTypeIdx(i);
            if (i >= full.length) clearInterval(interval);
        }, 45);
        return () => clearInterval(interval);
    }, [show, keyword]);

    if (!show) return null;

    const activeMsgs = STATUS_MESSAGES[stage] || STATUS_MESSAGES.collecting;
    const statusText = activeMsgs[msgIdx % activeMsgs.length];
    const tickerLine = ACTIVITY_TICKER[tickerIdx % ACTIVITY_TICKER.length];

    return (
        <div className="ld ld-animated" style={{ display: 'block' }}>
            {/* Header with blinking caret */}
            <div className="ldh">
                <span className="ldi">memuat hasil untuk</span>
                <span className="ldq">
                    "{keyword || '...'}"<span className="ld-caret" aria-hidden="true">▍</span>
                </span>
            </div>

            {/* Stage progress bars */}
            <div className="lps">
                {STAGES.map((s, i) => {
                    const isDone = i < currentIdx || (i === currentIdx && stage === 'assembling' && i === 2);
                    const isActive = i === currentIdx;
                    const isPending = i > currentIdx;

                    let width = '0%';
                    if (isDone) width = '100%';
                    else if (isActive) width = `${progress}%`;

                    return (
                        <div className={`lp${isActive ? ' active' : ''}${isDone ? ' done' : ''}`} key={s.key}>
                            <span className="lpn">
                                {isActive && <span className="ld-spinner" aria-hidden="true" />}
                                {s.label}
                            </span>
                            <div className="ltr">
                                {isActive ? (
                                    <div className="lf lf-active" style={{ width }} />
                                ) : (
                                    <div className={`lf${isDone ? ' done' : ''}`} style={{ width }} />
                                )}
                                {isActive && <div className="lf-shimmer" aria-hidden="true" />}
                            </div>
                            <span className={`ls${isDone ? ' done' : ''}`}>
                                {isDone ? 'selesai' : isActive ? '...' : '—'}
                            </span>
                        </div>
                    );
                })}
            </div>

            {/* Rotating status line */}
            <div className="ld-status">
                <span className="ld-status-dots" aria-hidden="true"><i /><i /><i /></span>
                <span key={msgIdx} className="ld-status-text">{statusText}</span>
            </div>

            {/* Activity ticker */}
            <div className="ld-ticker">
                <span className="ld-ticker-label">KABAR TERBARU</span>
                <span key={tickerIdx} className="ld-ticker-text">{tickerLine}</span>
            </div>
        </div>
    );
}
