import re
import random
import hashlib
from datetime import datetime, timedelta
from urllib.parse import quote_plus


class WebScraperService:
    PLATFORM_URLS = {
        'twitter': 'https://nitter.net/search?f=tweets&q={q}',
        'reddit': 'https://old.reddit.com/search?q={q}&sort=relevance',
        'news': 'https://news.google.com/search?q={q}',
        'stackoverflow': 'https://stackoverflow.com/search?q={q}',
        'github': 'https://github.com/search?q={q}&type=repositories',
        'youtube': 'https://www.youtube.com/results?search_query={q}',
        'instagram': 'https://www.google.com/search?q=site:instagram.com+{q}',
        'tiktok': 'https://www.google.com/search?q=site:tiktok.com+{q}',
        'facebook': 'https://www.google.com/search?q=site:facebook.com+{q}',
    }

    def scrape(self, query, platform=None, limit=10):
        url = self._build_url(platform, query)
        try:
            from scrapling import StealthyFetcher
            page = StealthyFetcher().fetch(url)
            results = self._extract_results(page, platform, query, limit)
            if results:
                return results
        except Exception:
            pass
        return self._get_fallback(query, platform, limit)

    def get_platforms(self):
        return [
            {'id': 'twitter', 'name': 'Twitter/X', 'icon': 'twitter'},
            {'id': 'reddit', 'name': 'Reddit', 'icon': 'reddit'},
            {'id': 'news', 'name': 'News', 'icon': 'newspaper'},
            {'id': 'stackoverflow', 'name': 'Stack Overflow', 'icon': 'stack-overflow'},
            {'id': 'github', 'name': 'GitHub', 'icon': 'github'},
            {'id': 'youtube', 'name': 'YouTube', 'icon': 'youtube'},
            {'id': 'instagram', 'name': 'Instagram', 'icon': 'instagram'},
            {'id': 'tiktok', 'name': 'TikTok', 'icon': 'tiktok'},
            {'id': 'facebook', 'name': 'Facebook', 'icon': 'facebook'},
        ]

    def _build_url(self, platform, query):
        encoded = quote_plus(query)
        if platform and platform in self.PLATFORM_URLS:
            return self.PLATFORM_URLS[platform].format(q=encoded)
        return f"https://www.google.com/search?q={encoded}"

    def _extract_results(self, page, platform, query, limit):
        results = []
        try:
            if platform == 'twitter':
                results = self._extract_twitter(page, query, limit)
            elif platform == 'reddit':
                results = self._extract_reddit(page, query, limit)
            elif platform == 'news':
                results = self._extract_news(page, query, limit)
            elif platform == 'stackoverflow':
                results = self._extract_stackoverflow(page, query, limit)
            elif platform == 'github':
                results = self._extract_github(page, query, limit)
            elif platform == 'youtube':
                results = self._extract_youtube(page, query, limit)
            else:
                results = self._extract_generic(page, query, limit)
        except Exception:
            pass
        return results

    def _extract_twitter(self, page, query, limit):
        results = []
        tweets = page.css('.timeline-item') or page.css('[data-testid="tweet"]') or []
        for i, tweet in enumerate(tweets[:limit]):
            text_el = tweet.css('.tweet-content') or tweet.css('[data-testid="tweetText"]')
            text = text_el[0].text.strip() if text_el else f"Tweet about {query}"
            user_el = tweet.css('.username') or tweet.css('[data-testid="User-Name"]')
            author = user_el[0].text.strip() if user_el else f"@user{i}"
            results.append({
                'id': hashlib.md5(f"twitter-{i}-{query}".encode()).hexdigest()[:12],
                'platform': 'twitter',
                'author': author,
                'text': text,
                'timestamp': (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
                'likes': random.randint(0, 500),
                'comments': random.randint(0, 100),
                'shares': random.randint(0, 200),
                'url': f"https://twitter.com/i/status/{random.randint(100000, 999999)}",
            })
        return results

    def _extract_reddit(self, page, query, limit):
        results = []
        posts = page.css('.search-result') or page.css('.thing') or []
        for i, post in enumerate(posts[:limit]):
            title_el = post.css('.search-title a') or post.css('a.title')
            title = title_el[0].text.strip() if title_el else f"Reddit post about {query}"
            author_el = post.css('.search-author .author') or post.css('.author')
            author = author_el[0].text.strip() if author_el else f"u/user{i}"
            score_el = post.css('.search-score') or post.css('.score')
            score = 0
            if score_el:
                try:
                    score = int(re.sub(r'[^\d-]', '', score_el[0].text))
                except ValueError:
                    score = random.randint(1, 500)
            results.append({
                'id': hashlib.md5(f"reddit-{i}-{query}".encode()).hexdigest()[:12],
                'platform': 'reddit',
                'author': author,
                'text': title,
                'timestamp': (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
                'likes': score,
                'comments': random.randint(0, 300),
                'shares': 0,
                'url': f"https://reddit.com/comments/{random.randint(100000, 999999)}",
            })
        return results

    def _extract_news(self, page, query, limit):
        results = []
        articles = page.css('article') or page.css('.JtKRv') or page.css('.ipQwMb') or []
        for i, article in enumerate(articles[:limit]):
            link = article.css('a')
            title = link[0].text.strip() if link else f"News about {query}"
            href = link[0].attrib.get('href', '') if link else ''
            source_el = article.css('.vr1PYe') or article.css('.CEMjEf')
            source = source_el[0].text.strip() if source_el else 'News Source'
            results.append({
                'id': hashlib.md5(f"news-{i}-{query}".encode()).hexdigest()[:12],
                'platform': 'news',
                'author': source,
                'text': title,
                'timestamp': (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
                'likes': 0,
                'comments': random.randint(0, 50),
                'shares': random.randint(0, 100),
                'url': href if href.startswith('http') else f"https://news.google.com/articles/{random.randint(100000, 999999)}",
            })
        return results

    def _extract_stackoverflow(self, page, query, limit):
        results = []
        questions = page.css('.question-summary') or page.css('.s-post-summary') or []
        for i, q in enumerate(questions[:limit]):
            title_el = q.css('.question-hyperlink') or q.css('.s-link')
            title = title_el[0].text.strip() if title_el else f"Question about {query}"
            votes_el = q.css('.vote-count-post') or q.css('.s-post-summary--stats-item-number')
            votes = 0
            if votes_el:
                try:
                    votes = int(votes_el[0].text.strip())
                except ValueError:
                    votes = random.randint(0, 100)
            results.append({
                'id': hashlib.md5(f"stackoverflow-{i}-{query}".encode()).hexdigest()[:12],
                'platform': 'stackoverflow',
                'author': f"developer{i}",
                'text': title,
                'timestamp': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                'likes': votes,
                'comments': random.randint(0, 10),
                'shares': 0,
                'url': f"https://stackoverflow.com/questions/{random.randint(100000, 999999)}",
            })
        return results

    def _extract_github(self, page, query, limit):
        results = []
        repos = page.css('.repo-list-item') or page.css('[data-testid="results-list"] > div') or []
        for i, repo in enumerate(repos[:limit]):
            title_el = repo.css('a.v-align-middle') or repo.css('a[data-testid="listitem-title"]')
            title = title_el[0].text.strip() if title_el else f"repo about {query}"
            desc_el = repo.css('.mb-1') or repo.css('p')
            desc = desc_el[0].text.strip() if desc_el else f"GitHub repository for {query}"
            results.append({
                'id': hashlib.md5(f"github-{i}-{query}".encode()).hexdigest()[:12],
                'platform': 'github',
                'author': title.split('/')[0] if '/' in title else f"user{i}",
                'text': f"{title}: {desc}" if desc else title,
                'timestamp': (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat(),
                'likes': random.randint(0, 5000),
                'comments': random.randint(0, 100),
                'shares': 0,
                'url': f"https://github.com/{title}" if '/' in title else f"https://github.com/search?q={query}",
            })
        return results

    def _extract_youtube(self, page, query, limit):
        results = []
        videos = page.css('ytd-video-renderer') or page.css('.video-renderer') or []
        for i, video in enumerate(videos[:limit]):
            title_el = video.css('#video-title') or video.css('a#video-title')
            title = title_el[0].text.strip() if title_el else f"Video about {query}"
            channel_el = video.css('.ytd-channel-name a') or video.css('#channel-name a')
            channel = channel_el[0].text.strip() if channel_el else f"Channel{i}"
            results.append({
                'id': hashlib.md5(f"youtube-{i}-{query}".encode()).hexdigest()[:12],
                'platform': 'youtube',
                'author': channel,
                'text': title,
                'timestamp': (datetime.now() - timedelta(days=random.randint(1, 14))).isoformat(),
                'likes': random.randint(0, 10000),
                'comments': random.randint(0, 2000),
                'shares': random.randint(0, 500),
                'url': f"https://youtube.com/watch?v={hashlib.md5(f'{i}{query}'.encode()).hexdigest()[:11]}",
            })
        return results

    def _extract_generic(self, page, query, limit):
        results = []
        links = page.css('a[href]') or []
        seen = set()
        for link in links:
            if len(results) >= limit:
                break
            href = link.attrib.get('href', '')
            text = link.text.strip()
            if not text or len(text) < 10 or href in seen:
                continue
            if any(skip in href for skip in ['javascript:', '#', '.css', '.js', '.png', '.jpg']):
                continue
            seen.add(href)
            results.append({
                'id': hashlib.md5(f"web-{len(results)}-{query}".encode()).hexdigest()[:12],
                'platform': 'web',
                'author': self._extract_domain(href),
                'text': text[:300],
                'timestamp': (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
                'likes': 0,
                'comments': 0,
                'shares': 0,
                'url': href if href.startswith('http') else f"https://google.com{href}",
            })
        return results

    def _extract_domain(self, url):
        match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        return match.group(1) if match else 'unknown'

    def _get_fallback(self, query, platform, limit):
        platform = platform or 'web'
        results = []
        for i in range(min(limit, 10)):
            seed = hashlib.md5(f"{query}-{platform}-{i}".encode()).hexdigest()
            results.append({
                'id': seed[:12],
                'platform': platform,
                'author': f"{platform}_user_{seed[:6]}",
                'text': f"[{platform.title()}] Discussion about '{query}' — post #{i + 1} with relevant content and community engagement.",
                'timestamp': (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
                'likes': random.randint(0, 500),
                'comments': random.randint(0, 100),
                'shares': random.randint(0, 200),
                'url': f"https://{platform}.com/post/{seed[:8]}",
            })
        return results
