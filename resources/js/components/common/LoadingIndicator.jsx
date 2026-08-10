import React from 'react';

const STAGES = [
    { key: 'collecting', label: 'mengumpulkan', progress: 100 },
    { key: 'analyzing', label: 'menganalisis', progress: 100 },
    { key: 'assembling', label: 'menyusun', progress: 100 },
];

function getStageIndex(stage) {
    const idx = STAGES.findIndex(s => s.key === stage);
    return idx >= 0 ? idx : -1;
}

export default function LoadingIndicator({ show, keyword, stage }) {
    if (!show) return null;

    const currentIdx = getStageIndex(stage);

    return (
        <div className="ld" style={{ display: 'block' }}>
            <div className="ldh">
                <span className="ldi">memuat hasil untuk</span>
                <span className="ldq">"{keyword || '...'}"</span>
            </div>
            <div className="lps">
                {STAGES.map((s, i) => {
                    const isDone = i < currentIdx || (i === currentIdx && stage === 'assembling' && i === 2);
                    const isActive = i === currentIdx;
                    const isPending = i > currentIdx;

                    let width = '0%';
                    if (isDone) width = '100%';
                    else if (isActive) width = '60%';

                    return (
                        <div className="lp" key={s.key}>
                            <span className="lpn">{s.label}</span>
                            <div className="ltr">
                                <div
                                    className={`lf${isDone ? ' done' : ''}`}
                                    style={{ width, transition: isActive ? 'width 2s ease' : 'width 0.3s ease' }}
                                />
                            </div>
                            <span className={`ls${isDone ? ' done' : ''}`}>
                                {isDone ? 'selesai' : isActive ? '...' : '—'}
                            </span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
