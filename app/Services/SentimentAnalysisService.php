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
     * Deteksi sentimen dari teks
     */
    protected function detectSentiment(string $text): string
    {
        $textLower = strtolower($text);

        $positiveCount = 0;
        $negativeCount = 0;

        foreach ($this->positiveKeywords as $keyword) {
            $positiveCount += substr_count($textLower, $keyword);
        }

        foreach ($this->negativeKeywords as $keyword) {
            $negativeCount += substr_count($textLower, $keyword);
        }

        if ($positiveCount > $negativeCount) {
            return 'positive';
        } elseif ($negativeCount > $positiveCount) {
            return 'negative';
        }

        return 'neutral';
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
            $matches += substr_count($textLower, $keyword);
        }

        return min($matches * 15, 100);
    }
}
