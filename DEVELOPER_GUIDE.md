# Real API Integration - Developer Guide

This guide explains the architecture of the real API integration and how to extend it.

## Architecture Overview

### Design Pattern: Strategy Pattern + Factory Pattern

Each social media platform is treated as a separate "strategy" for data collection:

```
┌─────────────────────────────────────────┐
│         ScraperService                  │
│  (Factory & Orchestrator)               │
│                                         │
│  - Chooses correct platform API         │
│  - Handles errors & fallbacks           │
│  - Logs API calls                       │
└────────────┬────────────────────────────┘
             │
    ┌────────┴─────────┬──────────┬──────────┬────────────┐
    │                  │          │          │            │
    ▼                  ▼          ▼          ▼            ▼
┌────────────┐  ┌────────────┐  ┌────────┐  ┌──────────┐  ┌─────────┐
│ TwitterAPI │  │ InstagramAPI │ │TikTokAPI│ │FacebookAPI│ │RedditAPI│
│            │  │              │ │        │  │          │  │         │
│ + scrape() │  │  + scrape()  │ │+scrape()  │ + scrape() │ + scrape()
│ + format() │  │  + format()  │ │+format()  │ + format() │ + format()
└────────────┘  └────────────┘  └────────┘  └──────────┘  └─────────┘
    │                  │          │          │            │
    └────────────────────────────────────────┘
             │
    All inherit from BasePlatformAPI
    ┌────────────────────────────────┐
    │   BasePlatformAPI (abstract)   │
    │                                │
    │ + get() - HTTP GET requests    │
    │ + post() - HTTP POST requests  │
    │ + httpClient - Guzzle          │
    │ + timeout settings             │
    │ + abstract scrape()            │
    │ + abstract format()            │
    └────────────────────────────────┘
```

## File Structure

```
app/Services/
├── ScraperService.php              # Main orchestrator
└── Platforms/
    ├── BasePlatformAPI.php         # Base class (abstract)
    ├── TwitterAPI.php              # Twitter implementation
    ├── InstagramAPI.php            # Instagram implementation
    ├── TikTokAPI.php               # TikTok implementation
    ├── FacebookAPI.php             # Facebook implementation
    ├── RedditAPI.php               # Reddit implementation
    └── YouTubeAPI.php              # YouTube implementation
```

## Core Components

### 1. BasePlatformAPI (Abstract Base Class)

**Purpose:** Define common interface and utilities for all platform APIs

**Key Methods:**
```php
abstract class BasePlatformAPI {
    // HTTP utilities
    protected function get(string $url, array $headers, array $query): array
    protected function post(string $url, array $data, array $headers): array
    
    // Must implement in child classes
    abstract public function scrape(string $keyword, int $limit): array;
    abstract protected function formatResponse(array $rawData): array;
    
    // Common properties
    protected $platformName;
    protected $httpClient; // Guzzle\Client
}
```

**Features:**
- Guzzle HTTP client for API calls
- Error handling with try-catch blocks
- Timeout configuration (30s default)
- JSON response parsing

### 2. Individual Platform APIs

Each platform extends `BasePlatformAPI` and implements:

```php
class TwitterAPI extends BasePlatformAPI {
    protected $platformName = 'twitter';
    protected $bearerToken;
    protected $apiBaseUrl = 'https://api.twitter.com/2';
    
    // Implement required methods
    public function scrape(string $keyword, int $limit): array { ... }
    protected function formatResponse(array $response): array { ... }
    
    // Optional: Fallback data generator
    private function getFallbackData(string $keyword, int $limit): array { ... }
}
```

**Key Features:**
- Platform-specific API authentication
- Custom query parameter formatting
- Response parsing and normalization
- Fallback data generation
- Error logging

### 3. ScraperService (Factory/Orchestrator)

**Purpose:** Route requests to correct platform and handle errors

```php
class ScraperService {
    protected $platformApis = [
        'twitter' => new TwitterAPI(),
        'instagram' => new InstagramAPI(),
        // ... etc
    ];
    
    public function scrape(string $platform, string $keyword, int $limit): array {
        return $this->platformApis[$platform]->scrape($keyword, $limit);
    }
}
```

## Data Flow

### 1. User Request
```
User → Frontend Form
├─ Select Platform
├─ Enter Keyword
└─ Click "Mulai Scraping"
```

### 2. API Call
```
Frontend → POST /api/scrape
{
  "platform": "twitter",
  "keyword": "Laravel",
  "limit": 50
}
```

### 3. Backend Processing
```
ScraperController
  ↓
ScraperService::scrape($platform, $keyword, $limit)
  ↓
Platform API (e.g., TwitterAPI::scrape())
  ├─ Check if credentials configured
  ├─ Prepare API request
  ├─ Make HTTP call to platform
  ├─ Parse response
  ├─ Format to standard structure
  ├─ If error → Use fallback data
  └─ Return standardized data
```

### 4. Response Format
```json
{
  "success": true,
  "data": [
    {
      "id": "unique_id",
      "platform": "twitter",
      "author": "username",
      "text": "post content",
      "timestamp": "2026-05-09T13:00:00+00:00",
      "likes": 100,
      "comments": 50,
      "shares": 25,
      "url": "https://..."
    },
    // ... more posts
  ]
}
```

## Adding a New Platform

### Step 1: Create Platform API Class

Create `app/Services/Platforms/NewPlatformAPI.php`:

```php
<?php

namespace App\Services\Platforms;

use Carbon\Carbon;
use Illuminate\Support\Facades\Log;

class NewPlatformAPI extends BasePlatformAPI
{
    protected $platformName = 'newplatform';
    protected $apiKey; // Platform-specific credential
    protected $apiBaseUrl = 'https://api.newplatform.com/v1';

    public function __construct()
    {
        parent::__construct();
        $this->apiKey = env('NEWPLATFORM_API_KEY');
        
        if (!$this->apiKey) {
            Log::warning('New Platform API Key not configured');
        }
    }

    /**
     * Scrape data from platform
     */
    public function scrape(string $keyword, int $limit): array
    {
        if (!$this->apiKey) {
            return $this->getFallbackData($keyword, $limit);
        }

        try {
            // Make API call
            $url = "{$this->apiBaseUrl}/search";
            
            $headers = [
                'Authorization' => "Bearer {$this->apiKey}",
                'User-Agent' => 'Socrapper/1.0',
            ];

            $query = [
                'q' => $keyword,
                'limit' => min($limit, 100),
                // Platform-specific parameters
            ];

            $response = $this->get($url, $headers, $query);

            if (isset($response['data']) && is_array($response['data'])) {
                return $this->formatResponse($response['data']);
            }

            return $this->getFallbackData($keyword, $limit);
        } catch (\Exception $e) {
            Log::error("New Platform API error: " . $e->getMessage());
            return $this->getFallbackData($keyword, $limit);
        }
    }

    /**
     * Format platform response to standard format
     */
    protected function formatResponse(array $data): array
    {
        $posts = [];

        foreach ($data as $item) {
            $posts[] = [
                'id' => $item['id'] ?? '',
                'platform' => 'newplatform',
                'author' => $item['author_name'] ?? 'Unknown',
                'text' => $item['content'] ?? '',
                'timestamp' => isset($item['created_at'])
                    ? Carbon::parse($item['created_at'])->toIso8601String()
                    : Carbon::now()->toIso8601String(),
                'likes' => $item['likes_count'] ?? 0,
                'comments' => $item['comments_count'] ?? 0,
                'shares' => $item['shares_count'] ?? 0,
                'url' => $item['post_url'] ?? '',
            ];
        }

        return $posts;
    }

    /**
     * Fallback data when API unavailable
     */
    private function getFallbackData(string $keyword, int $limit): array
    {
        Log::info("Using fallback data for New Platform - API key not configured");
        
        $fallbackPosts = [];
        for ($i = 1; $i <= min($limit, 10); $i++) {
            $fallbackPosts[] = [
                'id' => 'newplat_' . $i,
                'platform' => 'newplatform',
                'author' => "user{$i}",
                'text' => "Post about {$keyword} [Fallback Data]",
                'timestamp' => Carbon::now()->subHours($i)->toIso8601String(),
                'likes' => rand(10, 1000),
                'comments' => rand(5, 200),
                'shares' => rand(2, 100),
                'url' => "https://newplatform.com/post/{$i}",
            ];
        }
        return $fallbackPosts;
    }
}
```

### Step 2: Update ScraperService

Edit `app/Services/ScraperService.php`:

```php
use App\Services\Platforms\NewPlatformAPI;

class ScraperService
{
    protected $supportedPlatforms = [
        'twitter', 'instagram', 'tiktok', 'facebook', 
        'reddit', 'youtube', 'newplatform' // Add here
    ];

    public function __construct()
    {
        $this->platformApis = [
            'twitter' => new TwitterAPI(),
            'instagram' => new InstagramAPI(),
            'tiktok' => new TikTokAPI(),
            'facebook' => new FacebookAPI(),
            'reddit' => new RedditAPI(),
            'youtube' => new YouTubeAPI(),
            'newplatform' => new NewPlatformAPI(), // Add here
        ];
    }
}
```

### Step 3: Update Frontend (Optional)

Edit `resources/js/components/InputSection.jsx`:

The platform list is fetched from API, so it will automatically include the new platform if you add it to the array in the controller.

### Step 4: Configure Environment Variables

Add to `.env`:

```bash
NEWPLATFORM_API_KEY=your_api_key_here
```

### Step 5: Test

```bash
php artisan cache:clear
php artisan config:clear
```

Navigate to application and test the new platform!

## Best Practices

### 1. Authentication
- Always use environment variables for credentials
- Never hardcode API keys
- Use most secure auth method available (OAuth > Bearer > API Key)

### 2. Error Handling
- Always wrap API calls in try-catch
- Log errors with sufficient detail
- Fall back gracefully to demo data
- Provide user-friendly error messages

### 3. Rate Limiting
- Check platform's rate limits
- Implement exponential backoff for retries
- Cache responses when possible
- Add request throttling middleware

### 4. Response Normalization
- Keep response format consistent across all platforms
- Always include all fields (with null/0 if unavailable)
- Use ISO 8601 for timestamps
- Use platform URLs in standard format

### 5. Documentation
- Document API authentication requirements
- List rate limits and quotas
- Explain fallback behavior
- Provide example API requests

### 6. Testing
- Test with real API keys in development
- Test fallback data generation
- Test error scenarios
- Test rate limit handling

## Configuration Best Practices

### Development Environment
```bash
# .env.example (commit to repo)
NEWPLATFORM_API_KEY=

# .env (local, don't commit)
NEWPLATFORM_API_KEY=your_real_key_here
```

### Production Environment
Use hosting provider's environment variables:
- Heroku Config Vars
- AWS Systems Manager
- Google Cloud Secret Manager
- Azure Key Vault
- Docker secrets

## Performance Optimization

### Current Implementation
- Single API call per platform
- Guzzle HTTP client (optimized)
- Response caching ready (future)

### Future Improvements
1. **Caching Layer**
   ```php
   Cache::remember("scrape_{$platform}_{$keyword}", 
       3600, // 1 hour
       fn() => $api->scrape($keyword, $limit)
   );
   ```

2. **Request Batching**
   ```php
   // Get multiple platforms at once
   $results = collect($platforms)->map(
       fn($p) => $this->scrape($p, $keyword, $limit)
   );
   ```

3. **Queue System**
   ```php
   // Async scraping for heavy loads
   dispatch(new ScrapePostsJob($platform, $keyword))
   ```

## Monitoring & Debugging

### Enable Debugging
```php
// In platform API class
Log::debug('API Request', [
    'platform' => $this->platformName,
    'keyword' => $keyword,
    'url' => $url,
    'headers' => $headers,
]);

Log::debug('API Response', [
    'status_code' => $response->getStatusCode(),
    'data_count' => count($response['data'] ?? []),
]);
```

### Monitor Logs
```bash
tail -f storage/logs/laravel.log | grep "Platform API"
```

### Track API Usage
```php
// Add to ScraperService
DB::table('api_usage')->insert([
    'platform' => $platform,
    'keyword' => $keyword,
    'timestamp' => now(),
    'response_time' => $endTime - $startTime,
]);
```

## Troubleshooting

### Common Issues

**401 Unauthorized**
- Regenerate API credentials
- Check token expiration
- Verify API key format

**503 Service Unavailable**
- Platform API may be down
- Implement retry logic with backoff
- Check platform status page

**Rate Limited**
- Reduce request frequency
- Cache responses
- Upgrade API tier

**Invalid Response Format**
- API response changed
- Platform updated their API
- Update formatResponse() method

## References

### Platform API Documentation
- [Twitter API v2](https://developer.twitter.com/en/docs/twitter-api)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api)
- [TikTok API](https://developers.tiktok.com)
- [Facebook API](https://developers.facebook.com/docs/graph-api)
- [Reddit API](https://www.reddit.com/dev/api)
- [YouTube API](https://developers.google.com/youtube/v3)

### Related Code Files
- Controller: `app/Http/Controllers/ScraperController.php`
- Routes: `routes/api.php`
- Frontend: `resources/js/pages/App.jsx`

---

**Happy Coding!** 🚀

