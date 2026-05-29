<?php

namespace App\Services;

use Illuminate\Support\Facades\Log;
use GuzzleHttp\Client;

class LLMAnalysisService
{
    protected $httpClient;
    protected $apiKey;
    protected $baseUrl;
    protected $model;

    public function __construct()
    {
        $this->apiKey = config('services.llm.api_key');
        $this->baseUrl = config('services.llm.base_url');
        $this->model = config('services.llm.model');

        $this->httpClient = new Client([
            'timeout' => 120,
            'connect_timeout' => 30,
            'verify' => false,
            'headers' => [
                'Authorization' => 'Bearer ' . $this->apiKey,
                'Content-Type' => 'application/json',
            ],
        ]);
    }

    /**
     * Check apakah LLM configured
     */
    public function isConfigured(): bool
    {
        return !empty($this->apiKey) && !empty($this->baseUrl);
    }

    /**
     * Analyze content dengan LLM
     */
    public function analyze(string $prompt, string $systemPrompt = ''): ?string
    {
        if (!$this->isConfigured()) {
            Log::warning('LLM not configured. Set LLM_API_KEY and LLM_BASE_URL in .env');
            return null;
        }

        try {
            $messages = [];

            if (!empty($systemPrompt)) {
                $messages[] = [
                    'role' => 'system',
                    'content' => $systemPrompt,
                ];
            }

            $messages[] = [
                'role' => 'user',
                'content' => $prompt,
            ];

            $response = $this->httpClient->post($this->baseUrl . '/chat/completions', [
                'json' => [
                    'model' => $this->model,
                    'messages' => $messages,
                    'temperature' => 0.3,
                    'max_tokens' => 2000,
                ],
                'timeout' => 90,
                'connect_timeout' => 30,
            ]);

            $data = json_decode($response->getBody()->getContents(), true);

            return $data['choices'][0]['message']['content'] ?? null;
        } catch (\Exception $e) {
            Log::error('LLM analysis error: ' . $e->getMessage());
            return null;
        }
    }

    /**
     * Sentiment analysis dengan LLM
     */
    public function analyzeSentiment(array $texts): array
    {
        $systemPrompt = <<<'PROMPT'
Kamu adalah analis sentimen profesional. Analisis sentimen dari teks-teks yang diberikan.

Untuk setiap teks, berikan:
1. Sentimen: positive/negative/neutral
2. Confidence: 0-100%
3. Alasan singkat (1 kalimat)

Response dalam format JSON:
{
  "results": [
    {
      "text": "teks asli",
      "sentiment": "positive/negative/neutral",
      "confidence": 85,
      "reason": "alasan singkat"
    }
  ],
  "summary": {
    "positive": 5,
    "negative": 3,
    "neutral": 2,
    "overall": "positive",
    "overall_confidence": 78
  }
}
PROMPT;

        $textList = '';
        foreach ($texts as $i => $text) {
            $textList .= ($i + 1) . ". " . substr($text, 0, 500) . "\n\n";
        }

        $prompt = "Analisis sentimen dari teks berikut:\n\n$textList";

        $response = $this->analyze($prompt, $systemPrompt);

        if (!$response) {
            return $this->fallbackSentiment($texts);
        }

        // Parse JSON response
        $parsed = $this->parseJson($response);
        if ($parsed) {
            return $parsed;
        }

        return $this->fallbackSentiment($texts);
    }

    /**
     * Financial / Market analysis dengan LLM
     */
    public function analyzeMarket(string $query, array $articles): array
    {
        $systemPrompt = <<<'PROMPT'
Kamu adalah analis pasar finansial profesional. Analisis data pasar yang diberikan dan berikan insight yang actionable.

Response dalam format JSON:
{
  "query": "query asli",
  "sentiment": {
    "overall": "bullish/bearish/neutral",
    "confidence": 0-100,
    "score": -100 to 100
  },
  "summary": "Ringkasan analisis 2-3 kalimat",
  "key_points": [
    "Poin penting 1",
    "Poin penting 2"
  ],
  "risk_factors": [
    "Risiko 1",
    "Risiko 2"
  ],
  "opportunities": [
    "Peluang 1",
    "Peluang 2"
  ],
  "recommendation": "Rekomendasi singkat",
  "timeframe": "short-term/medium-term/long-term"
}
PROMPT;

        $articleTexts = '';
        foreach ($articles as $i => $article) {
            $title = $article['title'] ?? '';
            $snippet = $article['snippet'] ?? $article['content_excerpt'] ?? '';
            $source = $article['source'] ?? '';
            $date = $article['publish_date'] ?? '';

            $articleTexts .= "--- Artikel " . ($i + 1) . " ---\n";
            $articleTexts .= "Judul: $title\n";
            $articleTexts .= "Sumber: $source\n";
            $articleTexts .= "Tanggal: $date\n";
            $articleTexts .= "Konten: " . substr(strip_tags($snippet), 0, 800) . "\n\n";
        }

        $prompt = "Query: \"$query\"\n\nBerikut artikel-artikel terkait:\n\n$articleTexts\n\nBerikan analisis pasar yang komprehensif berdasarkan data di atas.";

        $response = $this->analyze($prompt, $systemPrompt);

        if (!$response) {
            return $this->fallbackMarketAnalysis($query, $articles);
        }

        $parsed = $this->parseJson($response);
        if ($parsed) {
            return $parsed;
        }

        return $this->fallbackMarketAnalysis($query, $articles);
    }

    /**
     * General analysis — untuk query apapun
     */
    public function analyzeGeneral(string $query, array $articles): array
    {
        $systemPrompt = <<<'PROMPT'
Kamu adalah asisten AI yang ahli menganalisis informasi dari berbagai sumber. Berikan analisis yang komprehensif, objektif, dan terstruktur.

Response dalam format JSON:
{
  "query": "query asli",
  "analysis": "Analisis lengkap 3-5 paragraf",
  "key_findings": [
    "Temuan penting 1",
    "Temuan penting 2"
  ],
  "sentiment": {
    "overall": "positive/negative/neutral/mixed",
    "confidence": 0-100
  },
  "entities": {
    "people": ["nama orang"],
    "organizations": ["nama organisasi"],
    "locations": ["lokasi"],
    "topics": ["topik utama"]
  },
  "related_topics": ["topik terkait"],
  "credibility": {
    "score": 0-100,
    "factors": ["faktor yang mempengaruhi kredibilitas"]
  }
}
PROMPT;

        $articleTexts = '';
        foreach ($articles as $i => $article) {
            $title = $article['title'] ?? '';
            $snippet = $article['snippet'] ?? $article['content_excerpt'] ?? '';
            $source = $article['source'] ?? '';

            $articleTexts .= "--- Sumber " . ($i + 1) . ": $source ---\n";
            $articleTexts .= "Judul: $title\n";
            $articleTexts .= "Konten: " . substr(strip_tags($snippet), 0, 600) . "\n\n";
        }

        $prompt = "Query: \"$query\"\n\nInformasi dari berbagai sumber:\n\n$articleTexts\n\nBerikan analisis komprehensif berdasarkan data di atas.";

        $response = $this->analyze($prompt, $systemPrompt);

        if (!$response) {
            return $this->fallbackGeneralAnalysis($query, $articles);
        }

        $parsed = $this->parseJson($response);
        if ($parsed) {
            return $parsed;
        }

        // Kalau JSON parse gagal, return raw text sebagai analysis
        return [
            'query' => $query,
            'analysis' => $response,
            'key_findings' => [],
            'sentiment' => [
                'overall' => 'neutral',
                'confidence' => 50,
            ],
            'entities' => ['people' => [], 'organizations' => [], 'locations' => [], 'topics' => []],
            'related_topics' => [],
            'credibility' => ['score' => 50, 'factors' => []],
        ];
    }

    /**
     * Parse JSON dari LLM response
     */
    protected function parseJson(string $response): ?array
    {
        // Coba langsung parse
        $parsed = json_decode($response, true);
        if ($parsed) return $parsed;

        // Coba extract JSON dari markdown code block
        if (preg_match('/```(?:json)?\s*([\s\S]*?)```/', $response, $match)) {
            $parsed = json_decode(trim($match[1]), true);
            if ($parsed) return $parsed;
        }

        // Coba cari JSON object dalam response
        if (preg_match('/\{[\s\S]*\}/', $response, $match)) {
            $parsed = json_decode($match[0], true);
            if ($parsed) return $parsed;
        }

        return null;
    }

    /**
     * Fallback sentiment analysis (keyword-based)
     */
    protected function fallbackSentiment(array $texts): array
    {
        $service = new SentimentAnalysisService();
        $result = $service->analyzeSentiments($texts);

        return [
            'results' => array_map(function ($detail) {
                return [
                    'text' => $detail['text'],
                    'sentiment' => $detail['sentiment'],
                    'confidence' => $detail['confidence'],
                    'reason' => 'Keyword-based analysis',
                ];
            }, $result['details']),
            'summary' => [
                'positive' => $result['positive'],
                'negative' => $result['negative'],
                'neutral' => $result['neutral'],
                'overall' => $result['percentage']['positive'] > $result['percentage']['negative'] ? 'positive' : ($result['percentage']['negative'] > $result['percentage']['positive'] ? 'negative' : 'neutral'),
                'overall_confidence' => 50,
            ],
        ];
    }

    /**
     * Fallback market analysis
     */
    protected function fallbackMarketAnalysis(string $query, array $articles): array
    {
        return [
            'query' => $query,
            'sentiment' => ['overall' => 'neutral', 'confidence' => 0, 'score' => 0],
            'summary' => 'LLM tidak tersedia. Menampilkan data mentah tanpa analisis AI.',
            'key_points' => [],
            'risk_factors' => [],
            'opportunities' => [],
            'recommendation' => 'Konfigurasi LLM API untuk analisis otomatis.',
            'timeframe' => 'N/A',
        ];
    }

    /**
     * Fallback general analysis
     */
    protected function fallbackGeneralAnalysis(string $query, array $articles): array
    {
        return [
            'query' => $query,
            'analysis' => 'LLM tidak tersedia. Konfigurasi LLM_API_KEY dan LLM_BASE_URL di .env untuk analisis AI.',
            'key_findings' => [],
            'sentiment' => ['overall' => 'neutral', 'confidence' => 0],
            'entities' => ['people' => [], 'organizations' => [], 'locations' => [], 'topics' => []],
            'related_topics' => [],
            'credibility' => ['score' => 0, 'factors' => []],
        ];
    }
}
