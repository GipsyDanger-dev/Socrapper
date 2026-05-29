<?php

namespace App\Services;

use Illuminate\Support\Facades\Log;

class InternetSurferService
{
    protected $searchEngine;
    protected $contentExtractor;
    protected $sentimentService;

    public function __construct(
        SearchEngineService $searchEngine,
        ContentExtractorService $contentExtractor,
        SentimentAnalysisService $sentimentService
    ) {
        $this->searchEngine = $searchEngine;
        $this->contentExtractor = $contentExtractor;
        $this->sentimentService = $sentimentService;
    }

    /**
     * Surf the internet: Search → Extract → Analyze
     */
    public function surf(string $query, array $options = []): array
    {
        $searchLimit = $options['search_limit'] ?? 5;
        $extractContent = $options['extract_content'] ?? true;
        $analyzeSentiment = $options['analyze_sentiment'] ?? true;

        try {
            // Step 1: Search
            $searchResults = $this->searchEngine->search($query, $searchLimit);

            if (empty($searchResults)) {
                return [
                    'success' => false,
                    'error' => 'No search results found',
                    'query' => $query,
                ];
            }

            // Step 2: Filter hanya URL yang bisa di-fetch (http/https)
            $fetchableUrls = array_filter(array_column($searchResults, 'url'), function ($url) {
                return strpos($url, 'http') === 0;
            });

            // Step 3: Extract content dari URL yang bisa di-fetch
            $extractedData = [];
            if ($extractContent && !empty($fetchableUrls)) {
                $extractedData = $this->contentExtractor->extractMultiple(array_values($fetchableUrls));
            }

            // Step 4: Merge search results dengan extracted content
            $mergedResults = $this->mergeResults($searchResults, $extractedData);

            // Step 5: Analisis sentimen
            $sentimentAnalysis = null;
            if ($analyzeSentiment && !empty($mergedResults)) {
                $texts = array_map(function ($item) {
                    $parts = array_filter([
                        $item['title'] ?? '',
                        $item['snippet'] ?? '',
                        $item['content_excerpt'] ?? '',
                    ]);
                    $text = implode('. ', $parts);
                    // Strip HTML tags
                    $text = strip_tags($text);
                    $text = html_entity_decode($text, ENT_QUOTES, 'UTF-8');
                    return trim($text);
                }, $mergedResults);

                $texts = array_filter($texts, function ($t) {
                    return strlen(trim($t)) > 10;
                });

                if (!empty($texts)) {
                    $sentimentAnalysis = $this->sentimentService->analyzeSentiments(array_values($texts));
                }
            }

            // Step 6: Generate summary
            $summary = $this->generateSummary($query, $mergedResults, $sentimentAnalysis);

            return [
                'success' => true,
                'query' => $query,
                'search_results' => $searchResults,
                'extracted_content' => $extractedData,
                'merged_results' => $mergedResults,
                'sentiment' => $sentimentAnalysis,
                'summary' => $summary,
                'total_results' => count($mergedResults),
            ];
        } catch (\Exception $e) {
            Log::error("Internet surfing error: " . $e->getMessage());
            return [
                'success' => false,
                'error' => $e->getMessage(),
                'query' => $query,
            ];
        }
    }

    /**
     * Deep surf: search + extract full content + detailed analysis
     */
    public function deepSurf(string $query, int $pages = 3): array
    {
        $allResults = [];

        // Multiple search queries untuk coverage lebih luas
        $queries = [
            $query,
            "$query terbaru",
            "$query analisis",
        ];

        foreach ($queries as $q) {
            $results = $this->surf($q, [
                'search_limit' => $pages,
                'extract_content' => true,
                'analyze_sentiment' => false, // analyze nanti sekaligus
            ]);

            if ($results['success']) {
                $allResults = array_merge($allResults, $results['merged_results'] ?? []);
            }
        }

        // Deduplicate berdasarkan URL
        $uniqueResults = [];
        $seenUrls = [];
        foreach ($allResults as $result) {
            $url = $result['url'] ?? '';
            if (!in_array($url, $seenUrls)) {
                $seenUrls[] = $url;
                $uniqueResults[] = $result;
            }
        }

        // Analisis sentimen gabungan
        $texts = array_map(function ($item) {
            return $item['title'] . '. ' . ($item['content_excerpt'] ?? '');
        }, $uniqueResults);

        $texts = array_filter($texts, function ($t) {
            return strlen(trim($t)) > 10;
        });

        $sentiment = null;
        if (!empty($texts)) {
            $sentiment = $this->sentimentService->analyzeSentiments(array_values($texts));
        }

        return [
            'success' => true,
            'query' => $query,
            'total_results' => count($uniqueResults),
            'results' => $uniqueResults,
            'sentiment' => $sentiment,
            'summary' => $this->generateSummary($query, $uniqueResults, $sentiment),
        ];
    }

    /**
     * Quick surf: search aja tanpa extract content (cepat)
     */
    public function quickSurf(string $query, int $limit = 5): array
    {
        $searchResults = $this->searchEngine->search($query, $limit);

        return [
            'success' => true,
            'query' => $query,
            'results' => $searchResults,
            'total' => count($searchResults),
        ];
    }

    /**
     * Merge search results dengan extracted content
     */
    protected function mergeResults(array $searchResults, array $extractedData): array
    {
        $merged = [];

        foreach ($searchResults as $index => $searchResult) {
            $item = [
                'title' => $searchResult['title'] ?? '',
                'url' => $searchResult['url'] ?? '',
                'snippet' => $searchResult['snippet'] ?? '',
                'source' => $searchResult['source'] ?? '',
                'content' => '',
                'content_excerpt' => '',
                'author' => '',
                'publish_date' => '',
                'word_count' => 0,
                'images' => [],
                'extraction_success' => false,
            ];

            // Merge dengan extracted content kalau ada
            if (isset($extractedData[$index]) && $extractedData[$index]['success']) {
                $extracted = $extractedData[$index];
                $item['content'] = $extracted['content'] ?? '';
                $item['content_excerpt'] = $this->getContentExcerpt($extracted['content'] ?? '', 500);
                $item['author'] = $extracted['author'] ?? '';
                $item['publish_date'] = $extracted['publish_date'] ?? '';
                $item['word_count'] = $extracted['word_count'] ?? 0;
                $item['images'] = $extracted['images'] ?? [];
                $item['extraction_success'] = true;
            }

            $merged[] = $item;
        }

        return $merged;
    }

    /**
     * Get excerpt dari content
     */
    protected function getContentExcerpt(string $content, int $maxLength = 500): string
    {
        if (strlen($content) <= $maxLength) {
            return $content;
        }

        // Potong di kata terdekat
        $excerpt = substr($content, 0, $maxLength);
        $lastSpace = strrpos($excerpt, ' ');

        if ($lastSpace > 0) {
            $excerpt = substr($excerpt, 0, $lastSpace);
        }

        return $excerpt . '...';
    }

    /**
     * Generate summary dari hasil surf
     */
    protected function generateSummary(string $query, array $results, ?array $sentiment): array
    {
        $totalResults = count($results);
        $totalWords = array_sum(array_column($results, 'word_count'));
        $sources = array_unique(array_column($results, 'source'));

        $summary = [
            'query' => $query,
            'total_sources' => $totalResults,
            'total_words' => $totalWords,
            'unique_sources' => array_values($sources),
            'has_content' => $totalResults > 0,
        ];

        // Tambah sentiment summary
        if ($sentiment) {
            $summary['sentiment_overview'] = [
                'positive' => $sentiment['percentage']['positive'] ?? 0,
                'negative' => $sentiment['percentage']['negative'] ?? 0,
                'neutral' => $sentiment['percentage']['neutral'] ?? 0,
                'dominant' => $this->getDominantSentiment($sentiment),
            ];
        }

        // Key topics (simple: ambil kata yang sering muncul)
        $summary['key_topics'] = $this->extractKeyTopics($results);

        return $summary;
    }

    /**
     * Get sentimen dominan
     */
    protected function getDominantSentiment(array $sentiment): string
    {
        $percentages = $sentiment['percentage'] ?? [];
        arsort($percentages);
        return key($percentages) ?? 'neutral';
    }

    /**
     * Extract key topics dari results (simple word frequency)
     */
    protected function extractKeyTopics(array $results): array
    {
        $allText = '';
        foreach ($results as $result) {
            $allText .= ' ' . ($result['title'] ?? '') . ' ' . ($result['content_excerpt'] ?? '');
        }

        $allText = strtolower(strip_tags($allText));

        // Stopwords Indonesia + English
        $stopwords = [
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'shall', 'can', 'need', 'dare', 'ought',
            'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
            'up', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'out', 'off', 'over', 'under', 'again',
            'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
            'how', 'all', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
            'too', 'very', 'just', 'because', 'but', 'and', 'or', 'if', 'while',
            'this', 'that', 'these', 'those', 'i', 'me', 'my', 'we', 'our',
            'you', 'your', 'he', 'him', 'his', 'she', 'her', 'it', 'its',
            'they', 'them', 'their', 'what', 'which', 'who', 'whom',
            'yang', 'dan', 'di', 'ke', 'dari', 'ini', 'itu', 'untuk', 'dengan',
            'pada', 'adalah', 'akan', 'juga', 'sudah', 'belum', 'bisa', 'tidak',
            'ada', 'oleh', 'seperti', 'setelah', 'sebelum', 'atau', 'tapi',
            'karena', 'jika', 'maka', 'serta', 'antara', 'lain', 'lebih',
        ];

        // Split jadi kata
        $words = preg_split('/\s+/', $allText);
        $words = array_filter($words, function ($w) use ($stopwords) {
            return strlen($w) > 3 && !in_array($w, $stopwords) && !is_numeric($w);
        });

        // Hitung frequency
        $frequency = array_count_values($words);
        arsort($frequency);

        // Ambil top 10
        return array_slice(array_keys($frequency), 0, 10);
    }
}
