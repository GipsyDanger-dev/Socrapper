<?php

namespace App\Services\Platforms;

use Carbon\Carbon;
use Illuminate\Support\Facades\Log;

class RedditAPI extends BasePlatformAPI
{
    protected $platformName = 'reddit';
    protected $clientId;
    protected $clientSecret;
    protected $userAgent;
    protected $accessToken;
    protected $apiBaseUrl = 'https://oauth.reddit.com';

    public function __construct()
    {
        parent::__construct();
        $this->clientId = env('REDDIT_CLIENT_ID');
        $this->clientSecret = env('REDDIT_CLIENT_SECRET');
        $this->userAgent = env('REDDIT_USER_AGENT', 'Socrapper/1.0');
        $this->accessToken = env('REDDIT_ACCESS_TOKEN');
        
        if (!$this->clientId) {
            Log::warning('Reddit credentials not configured');
        }
    }

    /**
     * Search Reddit posts
     * 
     * @param string $keyword
     * @param int $limit
     * @return array
     */
    public function scrape(string $keyword, int $limit): array
    {
        if (!$this->accessToken && !$this->canGetAccessToken()) {
            return $this->getFallbackData($keyword, $limit);
        }

        try {
            // Ensure we have access token
            if (!$this->accessToken) {
                $this->refreshAccessToken();
            }

            // Search endpoint
            $url = "{$this->apiBaseUrl}/r/all/search";
            
            $headers = [
                'Authorization' => "Bearer {$this->accessToken}",
                'User-Agent' => $this->userAgent,
            ];

            $query = [
                'q' => $keyword,
                'limit' => min($limit, 100),
                'sort' => 'relevance',
                'type' => 'link',
            ];

            $response = $this->get($url, $headers, $query);

            if (isset($response['data']['children']) && is_array($response['data']['children'])) {
                return $this->formatResponse($response['data']['children']);
            }

            return $this->getFallbackData($keyword, $limit);
        } catch (\Exception $e) {
            Log::error("Reddit API error: " . $e->getMessage());
            return $this->getFallbackData($keyword, $limit);
        }
    }

    /**
     * Check if we can get access token
     * 
     * @return bool
     */
    private function canGetAccessToken(): bool
    {
        return !empty($this->clientId) && !empty($this->clientSecret);
    }

    /**
     * Get new access token using client credentials
     * 
     * @return void
     */
    private function refreshAccessToken(): void
    {
        try {
            $url = 'https://www.reddit.com/api/v1/access_token';
            
            $headers = [
                'User-Agent' => $this->userAgent,
            ];

            $auth = [
                $this->clientId,
                $this->clientSecret,
            ];

            $data = [
                'grant_type' => 'client_credentials',
            ];

            // Make request with basic auth
            $response = $this->httpClient->request('POST', $url, [
                'auth' => $auth,
                'headers' => $headers,
                'form_params' => $data,
            ]);

            $result = json_decode($response->getBody()->getContents(), true);
            
            if (isset($result['access_token'])) {
                $this->accessToken = $result['access_token'];
            }
        } catch (\Exception $e) {
            Log::error("Reddit token refresh error: " . $e->getMessage());
        }
    }

    /**
     * Format Reddit API response
     * 
     * @param array $posts
     * @return array
     */
    protected function formatResponse(array $posts): array
    {
        $formatted = [];

        foreach ($posts as $postWrapper) {
            $post = $postWrapper['data'] ?? [];

            $formatted[] = [
                'id' => $post['id'] ?? '',
                'platform' => 'reddit',
                'author' => $post['author'] ?? '[deleted]',
                'text' => $post['title'] ?? '',
                'timestamp' => isset($post['created_utc'])
                    ? Carbon::createFromTimestamp($post['created_utc'])->toIso8601String()
                    : Carbon::now()->toIso8601String(),
                'likes' => $post['ups'] ?? 0,
                'comments' => $post['num_comments'] ?? 0,
                'shares' => 0, // Reddit doesn't track shares
                'url' => 'https://reddit.com' . ($post['permalink'] ?? ''),
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
        Log::info("Using fallback data for Reddit - Credentials not configured");
        
        $fallbackPosts = [];
        $subreddits = ['indonesia', 'AskReddit', 'worldnews', 'technology', 'news'];
        
        for ($i = 1; $i <= min($limit, 10); $i++) {
            $subreddit = $subreddits[$i % count($subreddits)];
            
            $fallbackPosts[] = [
                'id' => 'reddit_' . $i,
                'platform' => 'reddit',
                'author' => "redditor_{$i}",
                'text' => "Discussion about {$keyword} in r/{$subreddit} [Fallback Data]",
                'timestamp' => Carbon::now()->subDays($i)->toIso8601String(),
                'likes' => rand(10, 10000),
                'comments' => rand(5, 500),
                'shares' => 0,
                'url' => "https://reddit.com/r/{$subreddit}/comments/{$i}/",
            ];
        }
        return $fallbackPosts;
    }
}
