<?php

namespace App\Services;

class SentimentAnalysisService
{
    protected $positiveKeywords = [
        'bagus', 'mantap', 'hebat', 'keren', 'amazing', 'excellent',
        'love', 'suka', 'fantastic', 'wonderful', 'great', 'awesome',
        'luar biasa', 'sempurna', 'terbaik', 'sungguh',
    ];

    protected $negativeKeywords = [
        'buruk', 'jelek', 'kecewa', 'marah', 'benci', 'hate', 'terrible',
        'awful', 'horrible', 'bad', 'worst', 'sucks', 'stupid', 'sampah',
        'mengecewakan', 'parah', 'tidak suka', 'sangat marah',
    ];

    protected $negationWords = [
        'tidak', 'bukan', 'kurang', 'jangan', 'belum',
        'ga', 'gak', 'nggak', 'enggak', 'tanpa',
    ];

    /**
     * Analisis sentimen dari teks-teks
     */
    public function analyzeSentiments(array $texts): array
    {
        $analysis = [
            'positive' => 0,
            'negative' => 0,
            'neutral' => 0,
            'details' => [],
        ];

        foreach ($texts as $text) {
            $sentiment = $this->detectSentiment($text);
            $confidence = $this->calculateConfidence($text, $sentiment);

            if ($sentiment === 'positive') {
                $analysis['positive']++;
            } elseif ($sentiment === 'negative') {
                $analysis['negative']++;
            } else {
                $analysis['neutral']++;
            }

            $analysis['details'][] = [
                'text' => $text,
                'sentiment' => $sentiment,
                'confidence' => round($confidence, 2),
            ];
        }

        // Hitung persentase
        $total = count($texts);
        $analysis['percentage'] = [
            'positive' => round(($analysis['positive'] / $total) * 100, 2),
            'negative' => round(($analysis['negative'] / $total) * 100, 2),
            'neutral' => round(($analysis['neutral'] / $total) * 100, 2),
        ];

        return $analysis;
    }

    /**
     * Deteksi sentimen dari teks dengan negation handling
     */
    protected function detectSentiment(string $text): string
    {
        $textLower = strtolower($text);

        $positiveCount = 0;
        $negativeCount = 0;

        // Pisahkan multi-word dan single-word keywords
        $multiWordPositive = array_filter($this->positiveKeywords, fn($k) => str_contains($k, ' '));
        $singleWordPositive = array_filter($this->positiveKeywords, fn($k) => !str_contains($k, ' '));
        $multiWordNegative = array_filter($this->negativeKeywords, fn($k) => str_contains($k, ' '));
        $singleWordNegative = array_filter($this->negativeKeywords, fn($k) => !str_contains($k, ' '));

        // 1. Multi-word keywords: match sebagai phrase, tidak perlu negation check
        //    (sudah mengandung konteks negasi sendiri, misal "tidak suka")
        foreach ($multiWordPositive as $keyword) {
            $pattern = '/\b' . preg_quote($keyword, '/') . '\b/u';
            $positiveCount += preg_match_all($pattern, $textLower);
        }

        foreach ($multiWordNegative as $keyword) {
            $pattern = '/\b' . preg_quote($keyword, '/') . '\b/u';
            $negativeCount += preg_match_all($pattern, $textLower);
        }

        // 2. Single-word keywords: match dengan word boundary + negation check
        foreach ($singleWordPositive as $keyword) {
            $pattern = '/\b' . preg_quote($keyword, '/') . '\b/ui';
            if (preg_match_all($pattern, $textLower, $matches, PREG_OFFSET_CAPTURE)) {
                foreach ($matches[0] as $match) {
                    $offset = $match[1];
                    $textBefore = substr($textLower, 0, $offset);
                    if ($this->isNegated($textBefore)) {
                        $negativeCount++; // Negated positive = negative
                    } else {
                        $positiveCount++;
                    }
                }
            }
        }

        foreach ($singleWordNegative as $keyword) {
            $pattern = '/\b' . preg_quote($keyword, '/') . '\b/ui';
            if (preg_match_all($pattern, $textLower, $matches, PREG_OFFSET_CAPTURE)) {
                foreach ($matches[0] as $match) {
                    $offset = $match[1];
                    $textBefore = substr($textLower, 0, $offset);
                    if ($this->isNegated($textBefore)) {
                        $positiveCount++; // Negated negative = positive
                    } else {
                        $negativeCount++;
                    }
                }
            }
        }

        if ($positiveCount > $negativeCount) {
            return 'positive';
        } elseif ($negativeCount > $positiveCount) {
            return 'negative';
        }

        return 'neutral';
    }

    /**
     * Cek apakah teks sebelum match mengandung negasi dalam window 3 kata
     */
    protected function isNegated(string $textBeforeMatch): bool
    {
        $words = preg_split('/\s+/', trim($textBeforeMatch));
        $window = array_slice($words, -3);

        foreach ($window as $word) {
            if (in_array($word, $this->negationWords)) {
                return true;
            }
        }

        return false;
    }

    /**
     * Hitung confidence score
     */
    protected function calculateConfidence(string $text, string $sentiment): float
    {
        $textLower = strtolower($text);
        $matches = 0;

        $keywords = $sentiment === 'positive' ? $this->positiveKeywords :
                   ($sentiment === 'negative' ? $this->negativeKeywords : []);

        foreach ($keywords as $keyword) {
            $pattern = '/\b' . preg_quote($keyword, '/') . '\b/u';
            $matches += preg_match_all($pattern, $textLower);
        }

        return min($matches * 15, 100);
    }
}
