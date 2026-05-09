<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Services\ScraperService;
use App\Services\SentimentAnalysisService;
use App\Services\WebScraperService;
use App\Services\CsvExportService;
use Illuminate\Support\Facades\Log;
use Symfony\Component\HttpFoundation\BinaryFileResponse;

class ScraperController extends Controller
{
    protected $scraperService;
    protected $sentimentService;
    protected $webScraperService;

    public function __construct(
        ScraperService $scraperService,
        SentimentAnalysisService $sentimentService,
        WebScraperService $webScraperService
    ) {
        $this->scraperService = $scraperService;
        $this->sentimentService = $sentimentService;
        $this->webScraperService = $webScraperService;
    }

    /**
     * Mulai scraping dari platform menggunakan API official
     */
    public function scrape(Request $request)
    {
        $validated = $request->validate([
            'platform' => 'required|string|in:twitter,instagram,tiktok,facebook,reddit,youtube,news,stackoverflow,github',
            'keyword' => 'required|string|max:255',
            'limit' => 'required|integer|min:1|max:1000',
            'method' => 'nullable|string|in:api,webscrape',
        ]);

        try {
            $method = $validated['method'] ?? 'webscrape';

            if ($method === 'webscrape') {
                // Web scraping method
                $results = $this->webScrape(
                    $validated['platform'],
                    $validated['keyword'],
                    $validated['limit']
                );
            } else {
                // API method (fallback)
                $results = $this->scraperService->scrape(
                    $validated['platform'],
                    $validated['keyword'],
                    $validated['limit']
                );
            }

            return response()->json([
                'success' => true,
                'data' => $results,
                'total' => count($results),
                'platform' => $validated['platform'],
                'keyword' => $validated['keyword'],
                'method' => $method,
            ]);
        } catch (\Exception $e) {
            Log::error("Scraping error: " . $e->getMessage());
            return response()->json([
                'success' => false,
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Web scraping untuk berbagai platform
     */
    private function webScrape(string $platform, string $keyword, int $limit): array
    {
        try {
            switch ($platform) {
                case 'twitter':
                    return $this->webScraperService->scrapeTwitter($keyword, $limit);
                case 'reddit':
                    return $this->webScraperService->scrapeReddit($keyword, $limit);
                case 'news':
                    return $this->webScraperService->scrapeNews($keyword, $limit);
                case 'stackoverflow':
                    return $this->webScraperService->scrapeStackOverflow($keyword, $limit);
                case 'github':
                    return $this->webScraperService->scrapeGitHub($keyword, $limit);
                case 'youtube':
                    return $this->webScraperService->scrapeYouTube($keyword, $limit);
                case 'instagram':
                    return $this->webScraperService->scrapeInstagram($keyword, $limit);
                case 'tiktok':
                    return $this->webScraperService->scrapeTikTok($keyword, $limit);
                case 'facebook':
                    return $this->webScraperService->scrapeFacebook($keyword, $limit);
                default:
                    return [];
            }
        } catch (\Exception $e) {
            Log::error("Web scraping error for $platform: " . $e->getMessage());
            throw $e;
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
            Log::error("Sentiment analysis error: " . $e->getMessage());
            return response()->json([
                'success' => false,
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Export data ke CSV
     */
    public function exportData(Request $request)
    {
        $validated = $request->validate([
            'data' => 'required|array',
            'type' => 'required|string|in:scraping,analysis,statistics',
            'filename' => 'nullable|string',
        ]);

        try {
            $data = $validated['data'];
            $type = $validated['type'];
            $filename = $validated['filename'] ?? null;

            $filepath = match ($type) {
                'scraping' => CsvExportService::exportScrapingData($data, $filename),
                'analysis' => CsvExportService::exportAnalysis($data['data'] ?? [], $data['analysis'] ?? [], $filename),
                'statistics' => CsvExportService::exportStatistics($data, $filename),
                default => throw new \Exception('Invalid export type'),
            };

            if (!file_exists($filepath)) {
                throw new \Exception('Failed to create export file');
            }

            // Return file for download
            return response()->download($filepath, basename($filepath), [
                'Content-Type' => 'text/csv',
                'Content-Disposition' => 'attachment; filename="' . basename($filepath) . '"',
            ]);
        } catch (\Exception $e) {
            Log::error("Export error: " . $e->getMessage());
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
                'twitter' => 'Twitter/X (Web Scrape)',
                'reddit' => 'Reddit (Web Scrape)',
                'news' => 'Google News (Web Scrape)',
                'stackoverflow' => 'Stack Overflow (Web Scrape)',
                'github' => 'GitHub (Web Scrape)',
                'youtube' => 'YouTube (Fallback)',
                'instagram' => 'Instagram (Fallback)',
                'tiktok' => 'TikTok (Fallback)',
                'facebook' => 'Facebook (Fallback)',
            ],
        ]);
    }

    /**
     * Dapatkan list export files
     */
    public function getExports()
    {
        try {
            $exports = CsvExportService::listExports();

            return response()->json([
                'success' => true,
                'exports' => $exports,
            ]);
        } catch (\Exception $e) {
            Log::error("List exports error: " . $e->getMessage());
            return response()->json([
                'success' => false,
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Download export file
     */
    public function downloadExport($filename)
    {
        try {
            $filepath = CsvExportService::downloadFile($filename);

            return response()->download($filepath, $filename, [
                'Content-Type' => 'text/csv',
            ]);
        } catch (\Exception $e) {
            Log::error("Download export error: " . $e->getMessage());
            return response()->json([
                'success' => false,
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Delete export file
     */
    public function deleteExport($filename)
    {
        try {
            $success = CsvExportService::deleteFile($filename);

            if (!$success) {
                throw new \Exception('Failed to delete file');
            }

            return response()->json([
                'success' => true,
                'message' => 'Export file deleted',
            ]);
        } catch (\Exception $e) {
            Log::error("Delete export error: " . $e->getMessage());
            return response()->json([
                'success' => false,
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Dapatkan history scraping (future implementation)
     */
    public function getHistory()
    {
        // TODO: Implementasi dengan database
        return response()->json([
            'history' => [],
        ]);
    }

    /**
     * Hapus history scraping (future implementation)
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
