<?php

namespace App\Services;

use App\Services\Platforms\TwitterAPI;
use App\Services\Platforms\InstagramAPI;
use App\Services\Platforms\TikTokAPI;
use App\Services\Platforms\FacebookAPI;
use App\Services\Platforms\RedditAPI;
use App\Services\Platforms\YouTubeAPI;
use Illuminate\Support\Facades\Log;

class ScraperService
{
    protected $supportedPlatforms = ['twitter', 'instagram', 'tiktok', 'facebook', 'reddit', 'youtube'];
    protected $platformApis = [];

    public function __construct()
    {
        // Initialize platform APIs
        $this->platformApis = [
            'twitter' => new TwitterAPI(),
            'instagram' => new InstagramAPI(),
            'tiktok' => new TikTokAPI(),
            'facebook' => new FacebookAPI(),
            'reddit' => new RedditAPI(),
            'youtube' => new YouTubeAPI(),
        ];
    }

    /**
     * Scrape data dari platform menggunakan API asli
     */
    public function scrape(string $platform, string $keyword, int $limit = 100): array
    {
        if (!in_array($platform, $this->supportedPlatforms)) {
            throw new \Exception("Platform tidak didukung: {$platform}");
        }

        try {
            $api = $this->platformApis[$platform];
            return $api->scrape($keyword, $limit);
        } catch (\Exception $e) {
            Log::error("Scraping error for {$platform}: " . $e->getMessage());
            return [];
        }
    }

    /**
     * Dapatkan platform yang didukung
     */
    public function getSupportedPlatforms(): array
    {
        return $this->supportedPlatforms;
    }
}
