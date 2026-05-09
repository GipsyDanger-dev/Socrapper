<?php

namespace App\Services\Platforms;

use Carbon\Carbon;
use Illuminate\Support\Facades\Log;

class FacebookAPI extends BasePlatformAPI
{
    protected $platformName = 'facebook';
    protected $accessToken;
    protected $pageId;
    protected $apiBaseUrl = 'https://graph.facebook.com/v18.0';

    public function __construct()
    {
        parent::__construct();
        $this->accessToken = env('FACEBOOK_ACCESS_TOKEN');
        $this->pageId = env('FACEBOOK_PAGE_ID');
        
        if (!$this->accessToken) {
            Log::warning('Facebook Access Token not configured');
        }
    }

    /**
     * Scrape Facebook posts
     * 
     * @param string $keyword
     * @param int $limit
     * @return array
     */
    public function scrape(string $keyword, int $limit): array
    {
        if (!$this->accessToken || !$this->pageId) {
            return $this->getFallbackData($keyword, $limit);
        }

        try {
            // Get posts from Facebook page
            $url = "{$this->apiBaseUrl}/{$this->pageId}/feed";
            
            $query = [
                'fields' => 'id,message,story,created_time,permalink_url,likes.summary(true).limit(0),comments.summary(true).limit(0),shares',
                'access_token' => $this->accessToken,
                'limit' => min($limit, 25),
            ];

            $response = $this->get($url, [], $query);

            if (isset($response['data']) && is_array($response['data'])) {
                // Filter by keyword
                $filtered = array_filter($response['data'], function($post) use ($keyword) {
                    $text = ($post['message'] ?? '') . ' ' . ($post['story'] ?? '');
                    return stripos($text, $keyword) !== false;
                });

                return $this->formatResponse(array_values($filtered));
            }

            return $this->getFallbackData($keyword, $limit);
        } catch (\Exception $e) {
            Log::error("Facebook API error: " . $e->getMessage());
            return $this->getFallbackData($keyword, $limit);
        }
    }

    /**
     * Format Facebook API response
     * 
     * @param array $posts
     * @return array
     */
    protected function formatResponse(array $posts): array
    {
        $formatted = [];

        foreach ($posts as $post) {
            $text = $post['message'] ?? $post['story'] ?? '[No text]';
            
            $formatted[] = [
                'id' => $post['id'] ?? '',
                'platform' => 'facebook',
                'author' => 'Page',
                'text' => $text,
                'timestamp' => isset($post['created_time'])
                    ? Carbon::parse($post['created_time'])->toIso8601String()
                    : Carbon::now()->toIso8601String(),
                'likes' => $post['likes']['summary']['total_count'] ?? 0,
                'comments' => $post['comments']['summary']['total_count'] ?? 0,
                'shares' => $post['shares'] ?? 0,
                'url' => $post['permalink_url'] ?? '',
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
        Log::info("Using fallback data for Facebook - Page not configured");
        
        $fallbackPosts = [];
        for ($i = 1; $i <= min($limit, 10); $i++) {
            $fallbackPosts[] = [
                'id' => 'fb_' . $i,
                'platform' => 'facebook',
                'author' => "facebook_page",
                'text' => "Update tentang {$keyword} - Jangan lewatkan! [Fallback Data]",
                'timestamp' => Carbon::now()->subDays($i)->toIso8601String(),
                'likes' => rand(20, 500),
                'comments' => rand(5, 100),
                'shares' => rand(1, 50),
                'url' => "https://facebook.com/posts/{$i}",
            ];
        }
        return $fallbackPosts;
    }
}
