<?php

namespace App\Services\Platforms;

use Carbon\Carbon;
use Illuminate\Support\Facades\Log;

class InstagramAPI extends BasePlatformAPI
{
    protected $platformName = 'instagram';
    protected $accessToken;
    protected $businessAccountId;
    protected $apiBaseUrl = 'https://graph.instagram.com';

    public function __construct()
    {
        parent::__construct();
        $this->accessToken = config('services.instagram.access_token');
        $this->businessAccountId = config('services.instagram.business_account_id');
        
        if (!$this->accessToken) {
            Log::warning('Instagram Access Token not configured');
        }
    }

    /**
     * Scrape Instagram posts
     * 
     * Note: Instagram Graph API requires business account and app approval
     * This implementation uses the official API when configured
     * 
     * @param string $keyword
     * @param int $limit
     * @return array
     */
    public function scrape(string $keyword, int $limit): array
    {
        if (!$this->accessToken || !$this->businessAccountId) {
            return $this->getFallbackData($keyword, $limit);
        }

        try {
            // Get media from Instagram business account
            $url = "{$this->apiBaseUrl}/{$this->businessAccountId}/media";
            
            $query = [
                'fields' => 'id,caption,media_type,media_url,timestamp,like_count,comments_count',
                'access_token' => $this->accessToken,
                'limit' => min($limit, 25),
            ];

            $response = $this->get($url, [], $query);

            if (isset($response['data']) && is_array($response['data'])) {
                // Filter by keyword in caption
                $filtered = array_filter($response['data'], function($post) use ($keyword) {
                    return stripos($post['caption'] ?? '', $keyword) !== false;
                });

                return $this->formatResponse(array_values($filtered));
            }

            return $this->getFallbackData($keyword, $limit);
        } catch (\Exception $e) {
            Log::error("Instagram API error: " . $e->getMessage());
            return $this->getFallbackData($keyword, $limit);
        }
    }

    /**
     * Format Instagram API response
     * 
     * @param array $posts
     * @return array
     */
    protected function formatResponse(array $posts): array
    {
        $formatted = [];

        foreach ($posts as $post) {
            $formatted[] = [
                'id' => $post['id'] ?? '',
                'platform' => 'instagram',
                'author' => 'Account',
                'text' => $post['caption'] ?? '[No caption]',
                'timestamp' => isset($post['timestamp'])
                    ? Carbon::parse($post['timestamp'])->toIso8601String()
                    : Carbon::now()->toIso8601String(),
                'likes' => $post['like_count'] ?? 0,
                'comments' => $post['comments_count'] ?? 0,
                'shares' => 0, // Instagram doesn't provide share count via API
                'url' => "https://instagram.com/p/{$post['id']}",
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
        Log::info("Using fallback data for Instagram - Business account not configured");
        
        $fallbackPosts = [];
        for ($i = 1; $i <= min($limit, 10); $i++) {
            $fallbackPosts[] = [
                'id' => 'ig_' . $i,
                'platform' => 'instagram',
                'author' => "instagramuser{$i}",
                'text' => "Beautiful post tentang {$keyword} ✨ #Indonesia #Travel [Fallback Data]",
                'timestamp' => Carbon::now()->subDays($i)->toIso8601String(),
                'likes' => rand(50, 2000),
                'comments' => rand(10, 200),
                'shares' => 0,
                'url' => "https://instagram.com/p/fallback{$i}",
            ];
        }
        return $fallbackPosts;
    }
}
