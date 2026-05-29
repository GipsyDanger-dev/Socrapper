<?php

namespace App\Services;

use Illuminate\Support\Facades\Log;
use GuzzleHttp\Client;

class SearchEngineService
{
    protected $httpClient;

    public function __construct()
    {
        $this->httpClient = new Client([
            'timeout' => 30,
            'verify' => false,
            'headers' => [
                'User-Agent' => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept' => 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language' => 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            ],
        ]);
    }

    /**
     * Search - pakai Google Search + Google News RSS (gratis, tanpa API key)
     */
    public function search(string $query, int $limit = 10): array
    {
        $results = [];

        // 1. Google News RSS (paling reliable, gratis)
        $newsResults = $this->googleNewsSearch($query, ceil($limit / 2));
        $results = array_merge($results, $newsResults);

        // 2. Google Web Search (scrape HTML)
        $webResults = $this->googleWebSearch($query, $limit - count($results));
        $results = array_merge($results, $webResults);

        // Deduplicate berdasarkan URL
        $seen = [];
        $unique = [];
        foreach ($results as $r) {
            $url = $r['url'] ?? '';
            if (!empty($url) && !in_array($url, $seen)) {
                $seen[] = $url;
                $unique[] = $r;
            }
        }

        return array_slice($unique, 0, $limit);
    }

    /**
     * Google News RSS - gratis, reliable, tanpa API key
     */
    protected function googleNewsSearch(string $query, int $limit): array
    {
        try {
            $url = 'https://news.google.com/rss/search?q=' . urlencode($query) . '&hl=id&gl=ID&ceid=ID:id';
            $response = $this->httpClient->get($url);
            $xml = $response->getBody()->getContents();

            $results = [];
            if (preg_match_all('/<item>(.*?)<\/item>/si', $xml, $items)) {
                foreach ($items[1] as $item) {
                    if (count($results) >= $limit) break;

                    $title = $this->extractXmlTag($item, 'title');
                    $link = $this->extractXmlTag($item, 'link');
                    $pubDate = $this->extractXmlTag($item, 'pubDate');
                    $source = $this->extractXmlTag($item, 'source');
                    $description = $this->extractXmlTag($item, 'description');

                    // Extract real article URL dari description HTML
                    $articleUrl = $this->extractArticleUrlFromDescription($description) ?: $link;

                    // Clean snippet - strip ALL HTML tags
                    $cleanSnippet = strip_tags($description);
                    $cleanSnippet = html_entity_decode($cleanSnippet, ENT_QUOTES, 'UTF-8');
                    // Remove Google News redirect links
                    $cleanSnippet = preg_replace('/https?:\/\/news\.google\.com[^\s]*/', '', $cleanSnippet);
                    // Remove any remaining HTML artifacts
                    $cleanSnippet = preg_replace('/<[^>]*>/', '', $cleanSnippet);
                    $cleanSnippet = trim(preg_replace('/\s+/', ' ', $cleanSnippet));

                    if (!empty($title) && !empty($link)) {
                        $results[] = [
                            'title' => html_entity_decode($title, ENT_QUOTES, 'UTF-8'),
                            'url' => $articleUrl,
                            'snippet' => $cleanSnippet,
                            'source' => $source ?: parse_url($articleUrl, PHP_URL_HOST),
                            'publish_date' => $pubDate,
                            'type' => 'news',
                        ];
                    }
                }
            }

            return $results;
        } catch (\Exception $e) {
            Log::error("Google News search error: " . $e->getMessage());
            return [];
        }
    }

    /**
     * Google Web Search - scrape HTML results
     */
    protected function googleWebSearch(string $query, int $limit): array
    {
        try {
            $url = 'https://www.google.com/search?q=' . urlencode($query) . '&hl=id&gl=ID&num=' . $limit;

            // Random delay to avoid rate limiting
            usleep(rand(500000, 2000000));

            $response = $this->httpClient->get($url, [
                'headers' => [
                    'User-Agent' => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
                    'Accept' => 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language' => 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept-Encoding' => 'gzip, deflate',
                    'Connection' => 'keep-alive',
                    'Cache-Control' => 'max-age=0',
                ],
            ]);
            $html = $response->getBody()->getContents();

            $results = [];

            // Pattern 1: <a href="/url?q=REAL_URL">
            if (preg_match_all('/<a[^>]+href="\/url\?q=([^&"]+)[^"]*"[^>]*>(.*?)<\/a>/si', $html, $matches)) {
                foreach ($matches[1] as $i => $url) {
                    if (count($results) >= $limit) break;

                    $cleanUrl = urldecode($url);
                    $title = strip_tags($matches[2][$i]);
                    $title = html_entity_decode($title, ENT_QUOTES, 'UTF-8');

                    // Skip Google internal links
                    if (strpos($cleanUrl, 'google.com') !== false) continue;
                    if (strpos($cleanUrl, 'youtube.com/results') !== false) continue;

                    if (!empty($title) && filter_var($cleanUrl, FILTER_VALIDATE_URL)) {
                        $results[] = [
                            'title' => trim($title),
                            'url' => $cleanUrl,
                            'snippet' => '',
                            'source' => parse_url($cleanUrl, PHP_URL_HOST),
                            'type' => 'web',
                        ];
                    }
                }
            }

            // Pattern 2: fallback - cari <h3> dalam <a>
            if (empty($results)) {
                if (preg_match_all('/<a[^>]+href="(https?:\/\/[^"]+)"[^>]*>\s*<h3[^>]*>(.*?)<\/h3>/si', $html, $matches)) {
                    foreach ($matches[1] as $i => $url) {
                        if (count($results) >= $limit) break;

                        if (strpos($url, 'google.com') !== false) continue;

                        $title = strip_tags($matches[2][$i]);
                        $title = html_entity_decode($title, ENT_QUOTES, 'UTF-8');

                        if (!empty($title)) {
                            $results[] = [
                                'title' => trim($title),
                                'url' => $url,
                                'snippet' => '',
                                'source' => parse_url($url, PHP_URL_HOST),
                                'type' => 'web',
                            ];
                        }
                    }
                }
            }

            return $results;
        } catch (\Exception $e) {
            Log::error("Google web search error: " . $e->getMessage());
            return [];
        }
    }

    /**
     * Helper: extract tag dari XML/HTML
     */
    protected function extractXmlTag(string $xml, string $tag): string
    {
        if (preg_match("/<$tag>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?<\/$tag>/si", $xml, $match)) {
            return trim($match[1]);
        }
        return '';
    }

    /**
     * Extract article URL dari Google News description HTML
     */
    protected function extractArticleUrlFromDescription(string $html): string
    {
        // Google News description kadang mengandung link ke artikel asli
        if (preg_match('/href="(https?:\/\/(?!news\.google\.com)[^"]+)"/i', $html, $match)) {
            return $match[1];
        }

        // Coba extract dari <a> tags
        if (preg_match('/<a[^>]+href="([^"]+)"[^>]*>/i', $html, $match)) {
            $url = $match[1];
            if (strpos($url, 'news.google.com') === false && filter_var($url, FILTER_VALIDATE_URL)) {
                return $url;
            }
        }

        return '';
    }

    /**
     * Decode Google News redirect URL ke URL asli
     */
    protected function decodeGoogleNewsUrl(string $url): string
    {
        try {
            // Follow redirect dengan curl
            $ch = curl_init($url);
            curl_setopt_array($ch, [
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_FOLLOWLOCATION => true,
                CURLOPT_MAXREDIRS => 5,
                CURLOPT_NOBODY => true,
                CURLOPT_TIMEOUT => 10,
                CURLOPT_SSL_VERIFYPEER => false,
            ]);
            curl_exec($ch);
            $finalUrl = curl_getinfo($ch, CURLINFO_EFFECTIVE_URL);
            curl_close($ch);

            if (!empty($finalUrl) && strpos($finalUrl, 'news.google.com') === false) {
                return $finalUrl;
            }
        } catch (\Exception $e) {
            // Ignore
        }

        // Fallback: return original URL
        return $url;
    }
}
