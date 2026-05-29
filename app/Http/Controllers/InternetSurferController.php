<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Services\InternetSurferService;
use App\Services\LLMAnalysisService;
use Illuminate\Support\Facades\Log;

class InternetSurferController extends Controller
{
    protected $surferService;
    protected $llmService;

    public function __construct(InternetSurferService $surferService, LLMAnalysisService $llmService)
    {
        $this->surferService = $surferService;
        $this->llmService = $llmService;
    }

    /**
     * Quick surf: search aja tanpa extract content
     * POST /api/surf/quick
     */
    public function quickSurf(Request $request)
    {
        $validated = $request->validate([
            'query' => 'required|string|max:500',
            'limit' => 'nullable|integer|min:1|max:20',
        ]);

        try {
            $results = $this->surferService->quickSurf(
                $validated['query'],
                $validated['limit'] ?? 5
            );

            return response()->json($results);
        } catch (\Exception $e) {
            Log::error("Quick surf error: " . $e->getMessage());
            return response()->json([
                'success' => false,
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Full surf: search + extract + analyze
     * POST /api/surf
     */
    public function surf(Request $request)
    {
        $validated = $request->validate([
            'query' => 'required|string|max:500',
            'search_limit' => 'nullable|integer|min:1|max:10',
            'extract_content' => 'nullable|boolean',
            'analyze_sentiment' => 'nullable|boolean',
        ]);

        try {
            $results = $this->surferService->surf($validated['query'], [
                'search_limit' => $validated['search_limit'] ?? 5,
                'extract_content' => $validated['extract_content'] ?? true,
                'analyze_sentiment' => $validated['analyze_sentiment'] ?? true,
            ]);

            return response()->json($results);
        } catch (\Exception $e) {
            Log::error("Surf error: " . $e->getMessage());
            return response()->json([
                'success' => false,
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Deep surf: multiple queries + full extraction + detailed analysis
     * POST /api/surf/deep
     */
    public function deepSurf(Request $request)
    {
        $validated = $request->validate([
            'query' => 'required|string|max:500',
            'pages' => 'nullable|integer|min:1|max:5',
        ]);

        try {
            $results = $this->surferService->deepSurf(
                $validated['query'],
                $validated['pages'] ?? 3
            );

            return response()->json($results);
        } catch (\Exception $e) {
            Log::error("Deep surf error: " . $e->getMessage());
            return response()->json([
                'success' => false,
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Extract content dari URL langsung
     * POST /api/surf/extract
     */
    public function extractUrl(Request $request)
    {
        $validated = $request->validate([
            'url' => 'required|url',
        ]);

        try {
            $result = app(\App\Services\ContentExtractorService::class)
                ->extract($validated['url']);

            return response()->json($result);
        } catch (\Exception $e) {
            Log::error("Extract URL error: " . $e->getMessage());
            return response()->json([
                'success' => false,
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * AI-powered analysis
     * POST /api/surf/ai-analyze
     */
    public function aiAnalyze(Request $request)
    {
        $validated = $request->validate([
            'query' => 'required|string|max:500',
            'articles' => 'required|array|min:1',
            'type' => 'nullable|string|in:market,general',
        ]);

        try {
            $type = $validated['type'] ?? 'general';
            $articles = $validated['articles'];
            $query = $validated['query'];

            if (!$this->llmService->isConfigured()) {
                return response()->json([
                    'success' => false,
                    'error' => 'LLM not configured. Set LLM_API_KEY and LLM_BASE_URL in .env',
                    'configured' => false,
                ]);
            }

            if ($type === 'market') {
                $result = $this->llmService->analyzeMarket($query, $articles);
            } else {
                $result = $this->llmService->analyzeGeneral($query, $articles);
            }

            return response()->json([
                'success' => true,
                'ai_analysis' => $result,
                'type' => $type,
                'model' => env('LLM_MODEL', 'mimo-v2.5-pro'),
            ]);
        } catch (\Exception $e) {
            Log::error("AI analyze error: " . $e->getMessage());
            return response()->json([
                'success' => false,
                'error' => $e->getMessage(),
            ], 500);
        }
    }
}
