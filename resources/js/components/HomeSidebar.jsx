import React from 'react';

export default function HomeSidebar() {
    return (
        <div className="sidebar-wrap">
            {/* Vintage image placeholder 1 */}
            <div className="sidebar-img-placeholder sidebar-img-large">
                <div className="sidebar-img-inner">
                    <i className="fa-regular fa-image sidebar-img-icon" />
                    <span>Gambar vintage akan ditambahkan</span>
                </div>
            </div>

            {/* Quote of the day */}
            <div className="sidebar-section">
                <div className="sidebar-section-label">Kutipan</div>
                <blockquote className="sidebar-quote">
                    "Opini publik adalah cerminan dari kebenaran yang belum ditemukan."
                </blockquote>
                <div className="sidebar-quote-attr">— Pepatah Jurnalis</div>
            </div>

            {/* Facts */}
            <div className="sidebar-section">
                <div className="sidebar-section-label">Fakta Singkat</div>
                <div className="sidebar-fact">
                    <span className="sidebar-fact-num">4.9M</span>
                    <span className="sidebar-fact-desc">pengguna internet di Indonesia aktif di media sosial</span>
                </div>
                <div className="sidebar-fact">
                    <span className="sidebar-fact-num">2h 31m</span>
                    <span className="sidebar-fact-desc">rata-rata waktu harian di media sosial</span>
                </div>
                <div className="sidebar-fact">
                    <span className="sidebar-fact-num">73%</span>
                    <span className="sidebar-fact-desc">konsumen mengandalkan ulasan online sebelum membeli</span>
                </div>
            </div>

            {/* Vintage image placeholder 2 */}
            <div className="sidebar-img-placeholder sidebar-img-small">
                <div className="sidebar-img-inner">
                    <i className="fa-regular fa-image sidebar-img-icon" />
                    <span>Ilustrasi vintage</span>
                </div>
            </div>

            {/* Decorative ornament */}
            <div className="sidebar-ornament">— ✦ —</div>
        </div>
    );
}
