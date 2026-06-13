import re
import logging
import threading
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class NewsCacheService:
    """Pre-fetch and cache news for instant loading."""

    def __init__(self):
        self._cache = {
            'general': [],
            'trending': [],
            'last_update': None,
        }
        self._lock = threading.Lock()
        self._started = False

    def start(self):
        """Start background news fetching."""
        if self._started:
            return
        self._started = True
        # Initial fetch in background
        threading.Thread(target=self._initial_fetch, daemon=True).start()
        # Start periodic refresh
        threading.Thread(target=self._periodic_refresh, daemon=True).start()

    def _initial_fetch(self):
        """Fetch news immediately on startup."""
        try:
            self._fetch_news()
            logger.info("Initial news cache populated")
        except Exception as e:
            logger.error(f"Initial news fetch failed: {e}")

    def _periodic_refresh(self):
        """Refresh news cache every 5 minutes."""
        while True:
            time.sleep(300)  # 5 minutes
            try:
                self._fetch_news()
                logger.debug("News cache refreshed")
            except Exception as e:
                logger.error(f"News refresh failed: {e}")

    def _fetch_news(self):
        """Fetch news from Google News RSS."""
        import httpx

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }

        queries = [
            ('general', 'berita terkini Indonesia'),
            ('trending', 'trending Indonesia hari ini'),
        ]

        results = {}

        for key, query in queries:
            try:
                from urllib.parse import urlencode
                url = f"https://news.google.com/rss/search?q={urlencode({'': query})[1:]}&hl=id&gl=ID&ceid=ID:id"

                response = httpx.get(url, headers=headers, timeout=15, follow_redirects=True)
                if response.status_code != 200:
                    continue

                items = re.findall(r'<item>(.*?)</item>', response.text, re.DOTALL)
                news_list = []

                for item in items[:10]:
                    title = self._extract_tag(item, 'title')
                    link = self._extract_tag(item, 'link')
                    source = self._extract_tag(item, 'source')
                    pub_date = self._extract_tag(item, 'pubDate')

                    if title and link:
                        # Decode Google News URL
                        decoded_url = self._decode_url(link)
                        news_list.append({
                            'title': self._clean_html(title),
                            'url': decoded_url,
                            'source': source or 'News',
                            'publish_date': pub_date,
                        })

                results[key] = news_list

            except Exception as e:
                logger.error(f"Failed to fetch {key} news: {e}")

        # Update cache atomically
        with self._lock:
            if results.get('general'):
                self._cache['general'] = results['general']
            if results.get('trending'):
                self._cache['trending'] = results['trending']
            self._cache['last_update'] = datetime.now().isoformat()

    def _extract_tag(self, xml_text, tag):
        match = re.search(rf'<{tag}(?:[^>]*)>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{tag}>', xml_text, re.DOTALL)
        return match.group(1).strip() if match else ''

    def _clean_html(self, text):
        if not text:
            return ''
        import html as html_mod
        text = html_mod.unescape(text)
        text = html_mod.unescape(text)
        text = re.sub(r'<[^>]*>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _decode_url(self, url):
        """Decode Google News URL to actual article URL."""
        if not url or 'news.google.com' not in url:
            return url
        try:
            from googlenewsdecoder import new_decoderv1
            result = new_decoderv1(url)
            if result.get('status') and result.get('decoded_url'):
                return result['decoded_url']
        except Exception:
            pass
        return url

    def get_general(self):
        """Get cached general news."""
        with self._lock:
            return list(self._cache['general'])

    def get_trending(self):
        """Get cached trending news."""
        with self._lock:
            return list(self._cache['trending'])

    def get_last_update(self):
        """Get last cache update time."""
        with self._lock:
            return self._cache['last_update']


# Global singleton
news_cache = NewsCacheService()
