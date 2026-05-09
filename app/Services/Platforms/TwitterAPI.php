<?php

namespace App\Services\Platforms;

use Carbon\Carbon;
use Illuminate\Support\Facades\Log;

class TwitterAPI extends BasePlatformAPI
{
    protected $platformName = 'twitter';
    protected $bearerToken;
    protected $apiBaseUrl = 'https://api.twitter.com/2';

    public function __construct()
    {
        parent::__construct();
        $this->bearerToken = env('TWITTER_BEARER_TOKEN');
        
        if (!$this->bearerToken) {
            Log::warning('Twitter Bearer Token not configured');
        }
    }

    /**
     * Scrape tweets from Twitter using API v2
     * 
     * @param string $keyword
     * @param int $limit
     * @return array
     */
    public function scrape(string $keyword, int $limit): array
    {
        if (!$this->bearerToken) {
            return $this->getFallbackData($keyword, $limit);
        }

        try {
            $headers = [
                'Authorization' => "Bearer {$this->bearerToken}",
                'User-Agent' => 'Socrapper/1.0',
            ];

            // Twitter API v2 endpoint for searching tweets
            $url = "{$this->apiBaseUrl}/tweets/search/recent";
            
            $query = [
                'query' => $keyword . ' -is:retweet',
                'max_results' => min($limit, 100),
                'tweet.fields' => 'created_at,public_metrics,author_id',
                'expansions' => 'author_id',
                'user.fields' => 'username,name,verified',
            ];

            $response = $this->get($url, $headers, $query);

            if (isset($response['data']) && is_array($response['data'])) {
                return $this->formatResponse($response);
            }

            return $this->getFallbackData($keyword, $limit);
        } catch (\Exception $e) {
            Log::error("Twitter API error: " . $e->getMessage());
            return $this->getFallbackData($keyword, $limit);
        }
    }

    /**
     * Format Twitter API response to standard format
     * 
     * @param array $response
     * @return array
     */
    protected function formatResponse(array $response): array
    {
        $posts = [];
        $usersMap = [];

        // Build user map from includes
        if (isset($response['includes']['users'])) {
            foreach ($response['includes']['users'] as $user) {
                $usersMap[$user['id']] = $user['username'];
            }
        }

        // Format tweets
        foreach ($response['data'] ?? [] as $tweet) {
            $username = $usersMap[$tweet['author_id']] ?? 'Unknown';
            $metrics = $tweet['public_metrics'] ?? [];

            $posts[] = [
                'id' => $tweet['id'],
                'platform' => 'twitter',
                'author' => $username,
                'text' => $tweet['text'] ?? '',
                'timestamp' => isset($tweet['created_at']) 
                    ? Carbon::parse($tweet['created_at'])->toIso8601String()
                    : Carbon::now()->toIso8601String(),
                'likes' => $metrics['like_count'] ?? 0,
                'comments' => $metrics['reply_count'] ?? 0,
                'shares' => $metrics['retweet_count'] ?? 0,
                'url' => "https://twitter.com/{$username}/status/{$tweet['id']}",
            ];
        }

        return $posts;
    }

    /**
     * Return fallback data when API is not available
     * 
     * @param string $keyword
     * @param int $limit
     * @return array
     */
    private function getFallbackData(string $keyword, int $limit): array
    {
        Log::info("Using fallback data for Twitter - API token not configured");
        
        $fallbackPosts = [];
        for ($i = 1; $i <= min($limit, 10); $i++) {
            $fallbackPosts[] = [
                'id' => 'fallback_' . $i,
                'platform' => 'twitter',
                'author' => "TwitterUser{$i}",
                'text' => "Tweet tentang {$keyword} #Indonesia [Fallback Data]",
                'timestamp' => Carbon::now()->subHours($i)->toIso8601String(),
                'likes' => rand(10, 500),
                'comments' => rand(5, 100),
                'shares' => rand(2, 50),
                'url' => "https://twitter.com/user{$i}/status/fallback{$i}",
            ];
        }
        return $fallbackPosts;
    }
}
