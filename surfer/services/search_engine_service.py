import re
import logging
import time
import random
from urllib.parse import urlencode, urlparse, parse_qs, unquote
from xml.etree import ElementTree

import httpx

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
}


class SearchEngineService:
    def search(self, query, limit=10):
        results = []

        news_results = self._google_news_search(query, (limit + 1) // 2)
        results.extend(news_results)

        web_results = self._google_web_search(query, limit - len(results))
        results.extend(web_results)

        seen = set()
        unique = []
        for r in results:
            url = r.get('url', '')
            if url and url not in seen:
                seen.add(url)
                unique.append(r)

        return unique[:limit]

    def _google_news_search(self, query, limit):
        try:
            url = f"https://news.google.com/rss/search?q={urlencode({'': query})[1:]}&hl=id&gl=ID&ceid=ID:id"
            with httpx.Client(timeout=30, follow_redirects=True) as client:
                response = client.get(url, headers=HEADERS)
                xml_text = response.text

            results = []
            items = re.findall(r'<item>(.*?)</item>', xml_text, re.DOTALL)

            for item in items:
                if len(results) >= limit:
                    break

                title = self._extract_xml_tag(item, 'title')
                link = self._extract_xml_tag(item, 'link')
                pub_date = self._extract_xml_tag(item, 'pubDate')
                source = self._extract_xml_tag(item, 'source')
                description = self._extract_xml_tag(item, 'description')

                article_url = self._extract_article_url(description) or link

                # Parse bundled articles from description into clean format
                clean_snippet = self._parse_rss_description(description)

                if title and link:
                    results.append({
                        'title': self._decode_html(title),
                        'url': article_url,
                        'snippet': clean_snippet,
                        'source': source or urlparse(article_url).hostname or '',
                        'publish_date': pub_date,
                        'type': 'news',
                    })

            return results
        except Exception as e:
            logger.error(f"Google News search error: {e}")
            return []

    def _google_web_search(self, query, limit):
        try:
            time.sleep(random.uniform(0.5, 2.0))
            url = f"https://www.google.com/search?q={urlencode({'': query})[1:]}&hl=id&gl=ID&num={limit}"

            with httpx.Client(timeout=30, follow_redirects=True) as client:
                response = client.get(url, headers=HEADERS)
                html = response.text

            results = []

            # Pattern 1: /url?q=REAL_URL
            matches = re.findall(r'<a[^>]+href="/url\?q=([^&"]+)[^"]*"[^>]*>(.*?)</a>', html, re.DOTALL)
            for url_match, title_html in matches:
                if len(results) >= limit:
                    break
                clean_url = unquote(url_match)
                title = re.sub(r'<[^>]*>', '', title_html).strip()

                if 'google.com' in clean_url:
                    continue
                if 'youtube.com/results' in clean_url:
                    continue

                if title and clean_url.startswith('http'):
                    results.append({
                        'title': self._decode_html(title),
                        'url': clean_url,
                        'snippet': '',
                        'source': urlparse(clean_url).hostname or '',
                        'type': 'web',
                    })

            # Pattern 2: <a href="https://..."><h3>...</h3></a>
            if not results:
                matches = re.findall(r'<a[^>]+href="(https?://[^"]+)"[^>]*>\s*<h3[^>]*>(.*?)</h3>', html, re.DOTALL)
                for url_match, title_html in matches:
                    if len(results) >= limit:
                        break
                    if 'google.com' in url_match:
                        continue
                    title = re.sub(r'<[^>]*>', '', title_html).strip()
                    if title:
                        results.append({
                            'title': self._decode_html(title),
                            'url': url_match,
                            'snippet': '',
                            'source': urlparse(url_match).hostname or '',
                            'type': 'web',
                        })

            return results
        except Exception as e:
            logger.error(f"Google web search error: {e}")
            return []

    def _extract_xml_tag(self, xml_text, tag):
        match = re.search(rf'<{tag}(?:[^>]*)>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{tag}>', xml_text, re.DOTALL)
        return match.group(1).strip() if match else ''

    def _extract_article_url(self, html):
        match = re.search(r'href="(https?://(?!news\.google\.com)[^"]+)"', html, re.IGNORECASE)
        if match:
            return match.group(1)
        match = re.search(r'<a[^>]+href="([^"]+)"[^>]*>', html, re.IGNORECASE)
        if match:
            url = match.group(1)
            if 'news.google.com' not in url and url.startswith('http'):
                return url
        return ''

    def _decode_html(self, text):
        import html
        return html.unescape(text)

    def _strip_html(self, text):
        if not text:
            return ''
        import html as html_mod
        clean = html_mod.unescape(text)
        clean = html_mod.unescape(clean)
        clean = re.sub(r'<[^>]*>', ' ', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

    def _parse_rss_description(self, html_desc):
        """Parse Google News RSS description into clean 'Title - Source' lines."""
        if not html_desc:
            return ''
        import html as html_mod
        decoded = html_mod.unescape(html_mod.unescape(html_desc))

        # Extract all <li> items
        items = re.findall(r'<li[^>]*>(.*?)</li>', decoded, re.DOTALL)
        if not items:
            # Single article (no <li>), just strip and return
            clean = re.sub(r'<[^>]*>', ' ', decoded)
            clean = re.sub(r'\s+', ' ', clean).strip()
            return clean

        articles = []
        for item_html in items:
            # Extract title from <a> tag
            title_m = re.search(r'<a[^>]*>(.*?)</a>', item_html, re.DOTALL)
            title = re.sub(r'<[^>]*>', '', title_m.group(1)).strip() if title_m else ''
            # Extract source from <font> tag
            source_m = re.search(r'<font[^>]*>(.*?)</font>', item_html, re.DOTALL)
            source = re.sub(r'<[^>]*>', '', source_m.group(1)).strip() if source_m else ''
            if title:
                articles.append(f"{title} - {source}" if source else title)

        return '\n'.join(articles)
