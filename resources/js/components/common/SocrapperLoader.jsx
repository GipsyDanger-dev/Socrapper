import { useEffect, useState, useRef } from "react";

export default function SocrapperLoader({ onDone }) {
    const [phase, setPhase] = useState("idle");
    const [scanY, setScanY] = useState(0);
    const rafRef = useRef(null);
    const startRef = useRef(null);

    useEffect(() => {
        const t1 = setTimeout(() => setPhase("title"), 400);
        const t2 = setTimeout(() => setPhase("subtitle"), 900);
        const t3 = setTimeout(() => {
            setPhase("scan");
            startRef.current = performance.now();
            const DURATION = 1300;
            function tick(now) {
                const elapsed = now - startRef.current;
                const pct = Math.min(elapsed / DURATION, 1);
                setScanY(pct * 100);
                if (pct < 1) rafRef.current = requestAnimationFrame(tick);
            }
            rafRef.current = requestAnimationFrame(tick);
        }, 1300);
        const t4 = setTimeout(() => setPhase("out"), 3000);
        const t5 = setTimeout(() => onDone?.(), 3400);

        return () => {
            [t1, t2, t3, t4, t5].forEach(clearTimeout);
            if (rafRef.current) cancelAnimationFrame(rafRef.current);
        };
    }, []);

    const isOut = phase === "out";

    return (
        <div style={styles.root(isOut)}>
            <div style={styles.grain} aria-hidden="true" />

            {phase === "scan" && (
                <div style={styles.scanline(scanY)} aria-hidden="true" />
            )}

            <div style={styles.center}>
                <h1 style={styles.logo(phase !== "idle")}>Socrapper</h1>
                <p style={styles.sub(phase === "subtitle" || phase === "scan" || phase === "out")}>
                    Social Media Sentiment Scraper
                </p>
                <div style={styles.rule(phase === "scan" || phase === "out")} aria-hidden="true" />
                <p style={styles.tagline(phase === "scan" || phase === "out")}>
                    Membaca opini publik, satu kata kunci.
                </p>
            </div>

            <div style={styles.corner}>
                <span style={styles.cornerText}>v2.0 · ID + EN · 9 Platforms</span>
            </div>
        </div>
    );
}

const PAPER = "#f2ede4";
const INK = "#1c1a14";
const INK_M = "#6b6355";
const INK_F = "#a89e8a";

const styles = {
    root: (out) => ({
        position: "fixed",
        inset: 0,
        zIndex: 9999,
        background: PAPER,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
        opacity: out ? 0 : 1,
        transition: out ? "opacity 0.4s ease" : "none",
        pointerEvents: out ? "none" : "all",
    }),

    grain: {
        position: "absolute",
        inset: 0,
        opacity: 0.035,
        backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
        backgroundSize: "256px 256px",
        pointerEvents: "none",
    },

    scanline: (y) => ({
        position: "absolute",
        left: 0,
        right: 0,
        top: `${y}%`,
        height: "1px",
        background: INK,
        opacity: 0.12,
        pointerEvents: "none",
        transition: "none",
    }),

    center: {
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        textAlign: "center",
        gap: 0,
        userSelect: "none",
    },

    logo: (visible) => ({
        fontFamily: "'Playfair Display', Georgia, serif",
        fontSize: "clamp(52px, 8vw, 88px)",
        fontWeight: 700,
        letterSpacing: "-3px",
        lineHeight: 1,
        color: INK,
        margin: 0,
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(12px)",
        transition: "opacity 0.5s ease, transform 0.5s ease",
    }),

    sub: (visible) => ({
        fontFamily: "'IBM Plex Mono', 'Courier New', monospace",
        fontSize: "11px",
        letterSpacing: "2.5px",
        textTransform: "uppercase",
        color: INK_M,
        margin: "10px 0 0",
        opacity: visible ? 1 : 0,
        transition: "opacity 0.4s ease 0.1s",
    }),

    rule: (visible) => ({
        width: visible ? "120px" : "0px",
        height: "1px",
        background: INK,
        margin: "20px auto 0",
        opacity: 0.25,
        transition: "width 0.6s cubic-bezier(.16,1,.3,1)",
    }),

    tagline: (visible) => ({
        fontFamily: "'Playfair Display', Georgia, serif",
        fontStyle: "italic",
        fontSize: "15px",
        color: INK_F,
        margin: "14px 0 0",
        opacity: visible ? 1 : 0,
        transition: "opacity 0.5s ease 0.2s",
    }),

    corner: {
        position: "absolute",
        bottom: "24px",
        left: "28px",
    },

    cornerText: {
        fontFamily: "'IBM Plex Mono', monospace",
        fontSize: "10px",
        letterSpacing: "1px",
        color: INK_F,
        textTransform: "uppercase",
    },
};
