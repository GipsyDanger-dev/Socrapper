import React, { useMemo } from 'react';

// Minimal Indonesian + English stopwords (keep short/common filler out)
const STOPWORDS = new Set([
    // English
    'the', 'and', 'for', 'that', 'this', 'with', 'from', 'have', 'has', 'had',
    'are', 'was', 'were', 'been', 'will', 'would', 'could', 'should', 'their',
    'there', 'they', 'them', 'your', 'you', 'our', 'its', 'not', 'but', 'all',
    'about', 'into', 'than', 'then', 'when', 'where', 'which', 'while', 'more',
    'most', 'other', 'some', 'such', 'only', 'just', 'also', 'after', 'before',
    'new', 'can', 'may', 'per', 'via', 'says', 'said', 'news', 'what', 'will',
    // Indonesian
    'yang', 'dan', 'di', 'ke', 'dari', 'ini', 'itu', 'untuk', 'dengan', 'pada',
    'adalah', 'akan', 'juga', 'sudah', 'belum', 'bisa', 'tidak', 'ada', 'oleh',
    'seperti', 'setelah', 'sebelum', 'atau', 'tapi', 'karena', 'jika', 'maka',
    'serta', 'antara', 'lain', 'lebih', 'dalam', 'kepada', 'kita', 'kami',
    'mereka', 'saat', 'kini', 'harus', 'saya', 'anda', 'kamu',
    // Common news filler
    'indonesia', 'jakarta', 'www', 'com', 'https', 'http', 'artikel', 'berita',
]);

const COLORS = [
    '#b3541e', '#1e6f5c', '#2b4f8a', '#8a2b4f', '#5c4a1e',
    '#3b6e22', '#6e226b', '#a63d2f', '#1e5f8a', '#8a6e1e',
];

function tokenize(text) {
    return String(text || '')
        .toLowerCase()
        .split(/[^a-z0-9]+/)
        .filter(w => w.length > 3 && w.length < 25 && !STOPWORDS.has(w) && !/^\d+$/.test(w));
}

function computeFrequencies(texts, limit = 60) {
    const counts = {};
    for (const text of texts) {
        for (const word of tokenize(text)) {
            counts[word] = (counts[word] || 0) + 1;
        }
    }
    const sorted = Object.entries(counts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, limit);

    if (sorted.length === 0) return [];

    const min = sorted[sorted.length - 1][1];
    const max = sorted[0][1];
    const range = Math.max(max - min, 1);

    return sorted.map(([text, count], idx) => ({
        text,
        count,
        size: Math.round(14 + ((count - min) / range) * 26),
        color: COLORS[idx % COLORS.length],
    }));
}

function collides(box, placed) {
    return placed.some(p =>
        box.x - box.w / 2 < p.x + p.w / 2 &&
        box.x + box.w / 2 > p.x - p.w / 2 &&
        box.y - box.h / 2 < p.y + p.h / 2 &&
        box.y + box.h / 2 > p.y - p.h / 2
    );
}

// Spiral placement with bounding-box collision detection.
function layoutWords(words, W, H) {
    const placed = [];
    const cx = W / 2;
    const cy = H / 2;
    let angle = 0;
    let radius = 0;

    for (let i = 0; i < words.length; i++) {
        const w = words[i];
        const rot = i % 5 === 0 ? -90 : 0; // rotate ~20% of words vertically
        const h = (w.size * 1.05) + 4;
        const ww = (w.text.length * w.size * 0.62) + 6;

        let x = cx;
        let y = cy;
        let placedOk = false;

        for (let attempt = 0; attempt < 500; attempt++) {
            if (attempt === 0) {
                x = cx;
                y = cy;
            } else {
                angle += 0.34;
                radius += 0.38;
                x = cx + Math.cos(angle) * radius;
                y = cy + Math.sin(angle) * radius * 0.6;
            }
            if (x - ww / 2 < 4 || x + ww / 2 > W - 4 || y - h / 2 < 4 || y + h / 2 > H - 4) continue;

            const box = { x, y, w: ww, h };
            if (!collides(box, placed)) {
                placed.push({ ...w, x, y, w: ww, h, rot });
                placedOk = true;
                break;
            }
        }

        if (!placedOk) {
            // Last resort: drop at a random free-ish spot so top words never vanish
            placed.push({
                ...w,
                x: 20 + Math.random() * (W - 40),
                y: 20 + Math.random() * (H - 40),
                w: ww,
                h,
                rot: 0,
            });
        }
    }
    return placed;
}

export default function WordCloudTab({ texts, note = 'Kata yang paling sering muncul di hasil' }) {
    const words = useMemo(() => computeFrequencies(texts || []), [texts]);
    const placed = useMemo(() => layoutWords(words, 720, 420), [words]);

    if (placed.length === 0) {
        return (
            <div className="panel">
                <h3 className="srule" style={{ marginTop: 0 }}>kata yang sering muncul</h3>
                <div className="empty-state">Belum ada cukup data untuk membuat word cloud.</div>
            </div>
        );
    }

    return (
        <div className="panel">
            <h3 className="srule" style={{ marginTop: 0 }}>kata yang sering muncul</h3>
            <p className="wc-note">{note} — {words.length} kata teratas</p>
            <svg
                viewBox="0 0 720 420"
                className="wc-svg"
                role="img"
                aria-label="Word cloud kata yang sering muncul"
            >
                {placed.map(w => (
                    <text
                        key={`${w.text}-${w.x}-${w.y}`}
                        x={w.x}
                        y={w.y}
                        fontSize={w.size}
                        fill={w.color}
                        textAnchor="middle"
                        dominantBaseline="middle"
                        transform={w.rot ? `rotate(${w.rot} ${w.x} ${w.y})` : undefined}
                        className="wc-word"
                    >
                        {w.text}
                    </text>
                ))}
            </svg>
        </div>
    );
}
