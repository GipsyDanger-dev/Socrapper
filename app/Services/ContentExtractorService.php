<?php

namespace App\Services;

use Illuminate\Support\Facades\Log;
use GuzzleHttp\Client;
use GuzzleHttp\Promise;
use Symfony\Component\DomCrawler\Crawler;

class ContentExtractorService
{
    protected $httpClient;

    // Noise elements yang perlu dihapus
    protected $noiseSelectors = [
        'script', 'style', 'nav', 'footer', 'header',
        '.sidebar', '.advertisement', '.ad', '.ads',
        '.cookie-banner', '.popup', '.modal',
        '.social-share', '.related-posts', '.comments',
        '#sidebar', '#footer', '#header', '#nav',
        '.widget', '.newsletter', '.subscription',
    ];

    public function __construct()
    {
        $this->httpClient = new Client([
            'timeout' => 30,
            'verify' => false, // Disable SSL verification for dev
            'headers' => [
                'User-Agent' => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept' => 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language' => 'en-US,en;q=0.9,id;q=0.8',
            ],
        ]);
    }

    /**
     * Fetch dan extract konten dari satu URL
     */
    public function extract(string $url): array
    {
        try {
            $response = $this->httpClient->get($url);
            $html = $response->getBody()->getContents();
            $statusCode = $response->getStatusCode();

            if ($statusCode !== 200) {
                return $this->errorResult($url, "HTTP $statusCode");
            }

            return $this->parseContent($html, $url);
        } catch (\Exception $e) {
            Log::error("Content extraction error for $url: " . $e->getMessage());
            return $this->errorResult($url, $e->getMessage());
        }
    }

    /**
     * Fetch multiple URLs secara parallel
     */
    public function extractMultiple(array $urls, int $concurrency = 5): array
    {
        $promises = [];
        $results = [];

        foreach ($urls as $url) {
            $promises[$url] = $this->httpClient->getAsync($url)->then(
                function ($response) use ($url) {
                    $html = $response->getBody()->getContents();
                    return $this->parseContent($html, $url);
                },
                function ($exception) use ($url) {
                    return $this->errorResult($url, $exception->getMessage());
                }
            );
        }

        // Execute promises dengan concurrency limit
        $settled = Promise\Utils::settle($promises)->wait();

        foreach ($settled as $url => $result) {
            if ($result['state'] === 'fulfilled') {
                $results[] = $result['value'];
            } else {
                $results[] = $this->errorResult($url, 'Request failed');
            }
        }

        return $results;
    }

    /**
     * Parse HTML dan extract konten utama
     */
    protected function parseContent(string $html, string $url): array
    {
        $crawler = new Crawler($html, $url);

        // Extract metadata
        $title = $this->extractTitle($crawler);
        $description = $this->extractMetaDescription($crawler);
        $author = $this->extractAuthor($crawler);
        $publishDate = $this->extractDate($crawler);
        $siteName = $this->extractSiteName($crawler, $url);

        // Extract main content (readability mode)
        $mainContent = $this->extractMainContent($crawler);

        // Extract images
        $images = $this->extractImages($crawler, $url);

        // Hitung word count
        $wordCount = str_word_count($mainContent);

        return [
            'url' => $url,
            'title' => $title,
            'description' => $description,
            'author' => $author,
            'publish_date' => $publishDate,
            'site_name' => $siteName,
            'content' => $mainContent,
            'word_count' => $wordCount,
            'images' => $images,
            'success' => true,
        ];
    }

    /**
     * Extract title dari halaman
     */
    protected function extractTitle(Crawler $crawler): string
    {
        // Priority: og:title > h1 > <title>
        try {
            // og:title
            $ogTitle = $crawler->filter('meta[property="og:title"]');
            if ($ogTitle->count() > 0) {
                return trim($ogTitle->attr('content'));
            }

            // h1
            $h1 = $crawler->filter('h1');
            if ($h1->count() > 0) {
                return trim($h1->first()->text());
            }

            // <title>
            $title = $crawler->filter('title');
            if ($title->count() > 0) {
                return trim($title->text());
            }
        } catch (\Exception $e) {
            // ignore
        }

        return 'Untitled';
    }

    /**
     * Extract meta description
     */
    protected function extractMetaDescription(Crawler $crawler): string
    {
        try {
            // og:description
            $ogDesc = $crawler->filter('meta[property="og:description"]');
            if ($ogDesc->count() > 0) {
                return trim($ogDesc->attr('content'));
            }

            // meta description
            $metaDesc = $crawler->filter('meta[name="description"]');
            if ($metaDesc->count() > 0) {
                return trim($metaDesc->attr('content'));
            }
        } catch (\Exception $e) {
            // ignore
        }

        return '';
    }

    /**
     * Extract author
     */
    protected function extractAuthor(Crawler $crawler): string
    {
        try {
            // meta author
            $metaAuthor = $crawler->filter('meta[name="author"]');
            if ($metaAuthor->count() > 0) {
                return trim($metaAuthor->attr('content'));
            }

            // article:author
            $articleAuthor = $crawler->filter('meta[property="article:author"]');
            if ($articleAuthor->count() > 0) {
                return trim($articleAuthor->attr('content'));
            }

            // Schema.org author
            $schemaAuthor = $crawler->filter('[itemprop="author"]');
            if ($schemaAuthor->count() > 0) {
                return trim($schemaAuthor->first()->text());
            }

            // Common class names
            $authorSelectors = ['.author', '.byline', '.writer', '[rel="author"]'];
            foreach ($authorSelectors as $selector) {
                try {
                    $el = $crawler->filter($selector);
                    if ($el->count() > 0) {
                        return trim($el->first()->text());
                    }
                } catch (\Exception $e) {
                    continue;
                }
            }
        } catch (\Exception $e) {
            // ignore
        }

        return '';
    }

    /**
     * Extract publish date
     */
    protected function extractDate(Crawler $crawler): string
    {
        try {
            // article:published_time
            $articleDate = $crawler->filter('meta[property="article:published_time"]');
            if ($articleDate->count() > 0) {
                return trim($articleDate->attr('content'));
            }

            // Schema.org datePublished
            $schemaDate = $crawler->filter('[itemprop="datePublished"]');
            if ($schemaDate->count() > 0) {
                return trim($schemaDate->attr('content') ?? $schemaDate->text());
            }

            // time element
            $timeEl = $crawler->filter('time');
            if ($timeEl->count() > 0) {
                return trim($timeEl->first()->attr('datetime') ?? $timeEl->first()->text());
            }
        } catch (\Exception $e) {
            // ignore
        }

        return '';
    }

    /**
     * Extract site name
     */
    protected function extractSiteName(Crawler $crawler, string $url): string
    {
        try {
            // og:site_name
            $ogSite = $crawler->filter('meta[property="og:site_name"]');
            if ($ogSite->count() > 0) {
                return trim($ogSite->attr('content'));
            }
        } catch (\Exception $e) {
            // ignore
        }

        return parse_url($url, PHP_URL_HOST) ?? '';
    }

    /**
     * Extract main content (readability mode)
     */
    protected function extractMainContent(Crawler $crawler): string
    {
        try {
            // Clone crawler supaya gak mengubah original
            $contentCrawler = clone $crawler;

            // Hapus noise elements
            foreach ($this->noiseSelectors as $selector) {
                try {
                    $contentCrawler->filter($selector)->each(function (Crawler $node) {
                        // Skip kalau gak ada parent
                    });
                } catch (\Exception $e) {
                    continue;
                }
            }

            // Coba extract dari <article> dulu
            $articles = $contentCrawler->filter('article');
            if ($articles->count() > 0) {
                $text = $this->cleanText($articles->first()->text());
                if (strlen($text) > 200) {
                    return $text;
                }
            }

            // Coba dari .content, .post-content, .article-content, .entry-content
            $contentSelectors = [
                '.post-content', '.article-content', '.entry-content',
                '.content', '.main-content', '#content', '#main',
                '[role="main"]', 'main',
            ];

            foreach ($contentSelectors as $selector) {
                try {
                    $el = $contentCrawler->filter($selector);
                    if ($el->count() > 0) {
                        $text = $this->cleanText($el->first()->text());
                        if (strlen($text) > 200) {
                            return $text;
                        }
                    }
                } catch (\Exception $e) {
                    continue;
                }
            }

            // Fallback: ambil semua <p> tags
            $paragraphs = $contentCrawler->filter('p');
            $text = '';
            $paragraphs->each(function (Crawler $p) use (&$text) {
                $pText = trim($p->text());
                if (strlen($pText) > 30) {
                    $text .= $pText . "\n\n";
                }
            });

            $text = $this->cleanText($text);
            if (strlen($text) > 100) {
                return $text;
            }

            // Last fallback: ambil body text
            $body = $contentCrawler->filter('body');
            if ($body->count() > 0) {
                return $this->cleanText($body->first()->text());
            }

            return '';
        } catch (\Exception $e) {
            Log::error("Content extraction error: " . $e->getMessage());
            return '';
        }
    }

    /**
     * Clean extracted text
     */
    protected function cleanText(string $text): string
    {
        // Remove extra whitespace
        $text = preg_replace('/\s+/', ' ', $text);
        // Remove multiple newlines
        $text = preg_replace('/\n{3,}/', "\n\n", $text);
        // Trim
        $text = trim($text);

        return $text;
    }

    /**
     * Extract images dari halaman
     */
    protected function extractImages(Crawler $crawler, string $baseUrl): array
    {
        $images = [];

        try {
            // og:image
            $ogImage = $crawler->filter('meta[property="og:image"]');
            if ($ogImage->count() > 0) {
                $images[] = $ogImage->attr('content');
            }

            // Images dalam article/content
            $contentSelectors = ['article', '.post-content', '.article-content', '.content', 'main'];
            foreach ($contentSelectors as $selector) {
                try {
                    $el = $crawler->filter($selector);
                    if ($el->count() > 0) {
                        $el->filter('img')->each(function (Crawler $img) use (&$images, $baseUrl) {
                            $src = $img->attr('src');
                            if (!empty($src)) {
                                // Resolve relative URLs
                                if (strpos($src, 'http') !== 0) {
                                    $src = rtrim($baseUrl, '/') . '/' . ltrim($src, '/');
                                }
                                $images[] = $src;
                            }
                        });
                        if (!empty($images)) break;
                    }
                } catch (\Exception $e) {
                    continue;
                }
            }
        } catch (\Exception $e) {
            // ignore
        }

        return array_unique(array_slice($images, 0, 10));
    }

    /**
     * Error result helper
     */
    protected function errorResult(string $url, string $error): array
    {
        return [
            'url' => $url,
            'title' => '',
            'description' => '',
            'author' => '',
            'publish_date' => '',
            'site_name' => parse_url($url, PHP_URL_HOST) ?? '',
            'content' => '',
            'word_count' => 0,
            'images' => [],
            'success' => false,
            'error' => $error,
        ];
    }
}
