<?php

namespace App\Services\Platforms;

use GuzzleHttp\Client;
use GuzzleHttp\Exception\GuzzleException;
use Illuminate\Support\Facades\Log;

abstract class BasePlatformAPI
{
    protected $httpClient;
    protected $platformName;
    protected $apiKey;
    protected $timeout = 30;

    public function __construct()
    {
        $this->httpClient = new Client([
            'timeout' => $this->timeout,
            'verify' => false, // For development only - remove in production
        ]);
    }

    /**
     * Scrape posts from the platform
     * 
     * @param string $keyword
     * @param int $limit
     * @return array
     */
    abstract public function scrape(string $keyword, int $limit): array;

    /**
     * Format data from API response
     * 
     * @param array $rawData
     * @return array
     */
    abstract protected function formatResponse(array $rawData): array;

    /**
     * Make GET request to API
     * 
     * @param string $url
     * @param array $headers
     * @param array $query
     * @return array
     * @throws GuzzleException
     */
    protected function get(string $url, array $headers = [], array $query = []): array
    {
        try {
            $response = $this->httpClient->request('GET', $url, [
                'headers' => $headers,
                'query' => $query,
            ]);

            return json_decode($response->getBody()->getContents(), true) ?? [];
        } catch (GuzzleException $e) {
            Log::error("Error scraping {$this->platformName}: " . $e->getMessage());
            return [];
        }
    }

    /**
     * Make POST request to API
     * 
     * @param string $url
     * @param array $data
     * @param array $headers
     * @return array
     * @throws GuzzleException
     */
    protected function post(string $url, array $data = [], array $headers = []): array
    {
        try {
            $response = $this->httpClient->request('POST', $url, [
                'headers' => $headers,
                'json' => $data,
            ]);

            return json_decode($response->getBody()->getContents(), true) ?? [];
        } catch (GuzzleException $e) {
            Log::error("Error posting to {$this->platformName}: " . $e->getMessage());
            return [];
        }
    }

    /**
     * Get platform name
     * 
     * @return string
     */
    public function getPlatformName(): string
    {
        return $this->platformName;
    }
}
