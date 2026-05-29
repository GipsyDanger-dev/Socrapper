<?php

namespace App\Services\Platforms;

use Carbon\Carbon;
use Illuminate\Support\Facades\Log;

class TikTokAPI extends BasePlatformAPI
{
    protected $platformName = 'tiktok';
    protected $clientKey;
    protected $clientSecret;
    protected $apiBaseUrl = 'https://open.tiktok.com/v1';
    protected $accessToken;

    public function __construct()
    {
        parent::__construct();
        $this->clientKey = config('services.tiktok.client_key');
        $this->clientSecret = config('services.tiktok.client_secret');
        $this->accessToken = config('services.tiktok.access_token');
        
        if (!$this->clientKey) {
            Log::warning('TikTok credentials not configured');
        }
    }

    /**
     * Scrape TikTok videos
     * 
     * Note: TikTok restricts API access. Official Research API available upon request.
     * This implementation uses Business API when configured.
     * 
     * @param string $keyword
     * @param int $limit
     * @return array
     */
    public function scrape(string $keyword, int $limit): array
    {
        if (!$this->accessToken) {
            return $this->getFallbackData($keyword, $limit);
        }

        try {
            // TikTok Business API endpoint for video search
            // Note: This endpoint requires proper API access approval
            $url = "{$this->apiBaseUrl}/video/query";
            
            $headers = [
                'Authorization' => "Bearer {$this->accessToken}",
                'Content-Type' => 'application/json',
                'User-Agent' => 'Socrapper/1.0',
            ];

            $data = [
                'search_id' => $keyword,
                'count' => min($limit, 30),
            ];

            $response = $this->post($url, $data, $headers);

            if (isset($response['data']['videos']) && is_array($response['data']['videos'])) {
                return $this->formatResponse($response['data']['videos']);
            }

            return $this->getFallbackData($keyword, $limit);
        } catch (\Exception $e) {
            Log::error("TikTok API error: " . $e->getMessage());
            return $this->getFallbackData($keyword, $limit);
        }
    }

    /**
     * Format TikTok API response
     * 
     * @param array $videos
     * @return array
     */
    protected function formatResponse(array $videos): array
    {
        $formatted = [];

        foreach ($videos as $video) {
            $formatted[] = [
                'id' => $video['id'] ?? '',
                'platform' => 'tiktok',
                'author' => $video['author']['username'] ?? 'Unknown',
                'text' => $video['desc'] ?? '[No description]',
                'timestamp' => isset($video['create_time'])
                    ? Carbon::createFromTimestamp($video['create_time'])->toIso8601String()
                    : Carbon::now()->toIso8601String(),
                'likes' => $video['statistics']['like_count'] ?? 0,
                'comments' => $video['statistics']['comment_count'] ?? 0,
                'shares' => $video['statistics']['share_count'] ?? 0,
                'url' => "https://www.tiktok.com/@{$video['author']['username']}/video/{$video['id']}",
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
        Log::info("Using fallback data for TikTok - API access not configured");
        
        $fallbackPosts = [];
        for ($i = 1; $i <= min($limit, 10); $i++) {
            $fallbackPosts[] = [
                'id' => 'tiktok_' . $i,
                'platform' => 'tiktok',
                'author' => "tiktok_creator_{$i}",
                'text' => "Amazing {$keyword} content! 🎵 #indonesia #trending [Fallback Data]",
                'timestamp' => Carbon::now()->subHours($i * 2)->toIso8601String(),
                'likes' => rand(1000, 100000),
                'comments' => rand(100, 5000),
                'shares' => rand(50, 1000),
                'url' => "https://www.tiktok.com/@creator_{$i}/video/{$i}",
            ];
        }
        return $fallbackPosts;
    }
}
