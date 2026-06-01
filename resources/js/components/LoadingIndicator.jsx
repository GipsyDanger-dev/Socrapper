import React from 'react';

export default function LoadingIndicator({ show, keyword }) {
    if (!show) return null;

    return (
        <div className="ld" style={{ display: 'block' }}>
            <div className="ldh">
                <span className="ldi">memuat hasil untuk</span>
                <span className="ldq">"{keyword || '...'}"</span>
            </div>
            <div className="lps">
                <div className="lp">
                    <span className="lpn">mengumpulkan</span>
                    <div className="ltr"><div className="lf" style={{ width: '60%', transition: 'width 2s ease' }}></div></div>
                    <span className="ls">...</span>
                </div>
                <div className="lp">
                    <span className="lpn">menganalisis</span>
                    <div className="ltr"><div className="lf" style={{ width: '30%', transition: 'width 3s ease' }}></div></div>
                    <span className="ls">...</span>
                </div>
                <div className="lp">
                    <span className="lpn">menyusun</span>
                    <div className="ltr"><div className="lf" style={{ width: '10%', transition: 'width 4s ease' }}></div></div>
                    <span className="ls">...</span>
                </div>
            </div>
        </div>
    );
}
