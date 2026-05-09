<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Services\ScraperService;
use App\Services\SentimentAnalysisService;

class ScraperController extends Controller
{
    protected $scraperService;
    protected $sentimentService;

    public function __construct(ScraperService $scraperService, SentimentAnalysisService $sentimentService)
    {
        $this->scraperService = $scraperService;
        $this->sentimentService = $sentimentService;
    }

    /**
     * Mulai scraping dari platform
     */
    public function scrape(Request $request)
    {
        $validated = $request->validate([
            'platform' => 'required|string|in:twitter,instagram,tiktok,facebook,reddit,youtube',
            'keyword' => 'required|string|max:255',
            'limit' => 'required|integer|min:1|max:1000',
        ]);

        try {
            $results = $this->scraperService->scrape(
                $validated['platform'],
                $validated['keyword'],
                $validated['limit']
            );

            return response()->json([
                'success' => true,
                'data' => $results,
                'total' => count($results),
                'platform' => $validated['platform'],
                'keyword' => $validated['keyword'],
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Analisis sentimen dari teks
     */
    public function analyze(Request $request)
    {
        $validated = $request->validate([
            'texts' => 'required|array|min:1',
            'texts.*' => 'required|string',
        ]);

        try {
            $analysis = $this->sentimentService->analyzeSentiments($validated['texts']);

            return response()->json([
                'success' => true,
                'analysis' => $analysis,
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Dapatkan daftar platform yang didukung
     */
    public function getPlatforms()
    {
        return response()->json([
            'platforms' => [
                'twitter' => 'Twitter/X',
                'instagram' => 'Instagram',
                'tiktok' => 'TikTok',
                'facebook' => 'Facebook',
                'reddit' => 'Reddit',
                'youtube' => 'YouTube',
            ],
        ]);
    }

    /**
     * Dapatkan history scraping
     */
    public function getHistory()
    {
        // TODO: Implementasi dengan database
        return response()->json([
            'history' => [],
        ]);
    }

    /**
     * Hapus history scraping
     */
    public function deleteHistory($id)
    {
        // TODO: Implementasi dengan database
        return response()->json([
            'success' => true,
            'message' => 'History deleted',
        ]);
    }
}
