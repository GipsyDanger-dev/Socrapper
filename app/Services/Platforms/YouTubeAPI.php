<?php

namespace App\Services\Platforms;

use Carbon\Carbon;
use Illuminate\Support\Facades\Log;

class YouTubeAPI extends BasePlatformAPI
{
    protected $platformName = 'youtube';
    protected $apiKey;
    protected $apiBaseUrl = 'https://www.googleapis.com/youtube/v3';

    public function __construct()
    {
        parent::__construct();
        $this->apiKey = env('YOUTUBE_API_KEY');
        
        if (!$this->apiKey) {
            Log::warning('YouTube API Key not configured');
        }
    }

    /**
     * Search YouTube videos
     * 
     * @param string $keyword
     * @param int $limit
     * @return array
     */
    public function scrape(string $keyword, int $limit): array
    {
        if (!$this->apiKey) {
            return $this->getFallbackData($keyword, $limit);
        }

        try {
            // Search endpoint
            $url = "{$this->apiBaseUrl}/search";
            
            $query = [
                'q' => $keyword,
                'type' => 'video',
                'part' => 'snippet',
                'maxResults' => min($limit, 50),
                'order' => 'relevance',
                'key' => $this->apiKey,
            ];

            $response = $this->get($url, [], $query);

            if (isset($response['items']) && is_array($response['items'])) {
                // Get video IDs for statistics
                $videoIds = array_map(fn($item) => $item['id']['videoId'], $response['items']);
                $stats = $this->getVideoStatistics($videoIds);
                
                return $this->formatResponse($response['items'], $stats);
            }

            return $this->getFallbackData($keyword, $limit);
        } catch (\Exception $e) {
            Log::error("YouTube API error: " . $e->getMessage());
            return $this->getFallbackData($keyword, $limit);
        }
    }

    /**
     * Get video statistics (views, likes, comments)
     * 
     * @param array $videoIds
     * @return array
     */
    private function getVideoStatistics(array $videoIds): array
    {
        try {
            $url = "{$this->apiBaseUrl}/videos";
            
            $query = [
                'id' => implode(',', array_slice($videoIds, 0, 50)),
                'part' => 'statistics',
                'key' => $this->apiKey,
            ];

            $response = $this->get($url, [], $query);
            
            $stats = [];
            foreach ($response['items'] ?? [] as $item) {
                $stats[$item['id']] = $item['statistics'] ?? [];
            }
            
            return $stats;
        } catch (\Exception $e) {
            Log::error("YouTube statistics error: " . $e->getMessage());
            return [];
        }
    }

    /**
     * Format YouTube API response
     * 
     * @param array $videos
     * @param array $stats
     * @return array
     */
    protected function formatResponse(array $videos, array $stats = []): array
    {
        $formatted = [];

        foreach ($videos as $video) {
            $videoId = $video['id']['videoId'] ?? '';
            $videoStats = $stats[$videoId] ?? [];

            $formatted[] = [
                'id' => $videoId,
                'platform' => 'youtube',
                'author' => $video['snippet']['channelTitle'] ?? 'Unknown',
                'text' => $video['snippet']['title'] ?? '',
                'timestamp' => isset($video['snippet']['publishedAt'])
                    ? Carbon::parse($video['snippet']['publishedAt'])->toIso8601String()
                    : Carbon::now()->toIso8601String(),
                'likes' => $videoStats['likeCount'] ?? 0,
                'comments' => $videoStats['commentCount'] ?? 0,
                'shares' => 0, // YouTube doesn't provide share count
                'url' => "https://www.youtube.com/watch?v={$videoId}",
            ];
        }

        return $formatted;
    }

    /**
     * Return fallback data
     * 
     * @param string $keyword
     * @param int $limit
     * @return array
     */
    private function getFallbackData(string $keyword, int $limit): array
    {
        Log::info("Using fallback data for YouTube - API key not configured");
        
        $fallbackPosts = [];
        for ($i = 1; $i <= min($limit, 10); $i++) {
            $fallbackPosts[] = [
                'id' => 'yt_' . $i,
                'platform' => 'youtube',
                'author' => "YouTubeChannel{$i}",
                'text' => "Video Menarik tentang {$keyword} - Part {$i} [Fallback Data]",
                'timestamp' => Carbon::now()->subDays($i)->toIso8601String(),
                'likes' => rand(100, 10000),
                'comments' => rand(50, 1000),
                'shares' => 0,
                'url' => "https://www.youtube.com/watch?v=fallback{$i}",
            ];
        }
        return $fallbackPosts;
    }
}
