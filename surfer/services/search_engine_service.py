import re
import logging
import time
import random
from urllib.parse import urlencode, urlparse, unquote

logger = logging.getLogger(__name__)


class SearchEngineService:
    def search(self, query, limit=10):
        results = []

        # Calculate pages needed (10 results per page max for Google)
        pages_needed = max(1, (limit + 9) // 10)

        # Fetch from Google News RSS. It is the most reliable source, so give
        # it the full quota instead of only half — this avoids returning a
        # tiny result set whenever Google Web Search blocks the server.
        news_results = self._google_news_search(query, limit)
        results.extend(news_results)

        # Fetch from Google Web Search with pagination for the remainder
        remaining = limit - len(results)
        if remaining > 0:
            for page in range(1, pages_needed + 1):
                if len(results) >= limit:
                    break
                page_results = self._google_web_search(query, min(remaining, 10), page=page)
                results.extend(page_results)
                remaining = limit - len(results)
                if page < pages_needed:
                    time.sleep(random.uniform(1.0, 2.5))

        # Backfill remaining quota with Bing, then DuckDuckGo.
        # These must run even when Google returned partial (not only empty)
        # results, otherwise the requested limit is never reached.
        remaining = limit - len(results)
        if remaining > 0:
            bing_results = self._bing_search(query, remaining)
            results.extend(bing_results)

        remaining = limit - len(results)
        if remaining > 0:
            ddg_results = self._duckduckgo_search(query, remaining)
            results.extend(ddg_results)

        # Deduplicate by URL
        seen = set()
        unique = []
        for r in results:
            url = r.get("url", "")
            if url and url not in seen:
                seen.add(url)
                unique.append(r)

        return unique[:limit]

    def _resolve_google_news_url(self, url):
        """Decode Google News URL to get the actual article URL."""
        if not url or "news.google.com" not in url:
            return url
        try:
            from googlenewsdecoder import new_decoderv1

            result = new_decoderv1(url)
            if result.get("status") and result.get("decoded_url"):
                return result["decoded_url"]
        except Exception as e:
            logger.debug(f"Google News URL decode failed: {e}")
        return url

    def _google_news_search(self, query, limit):
        try:
            from scraper.services.shared_client import fetch
            from scraper.services.rate_limiter import throttle

            url = f"https://news.google.com/rss/search?q={urlencode({'': query})[1:]}&hl=id&gl=ID&ceid=ID:id"
            throttle("news.google.com")
            response = fetch(url)

            if response.status_code != 200:
                logger.warning(f"Google News returned status {response.status_code}")
                return []

            xml_text = response.text
            results = []
            items = re.findall(r"<item>(.*?)</item>", xml_text, re.DOTALL)

            for item in items:
                if len(results) >= limit:
                    break

                title = self._extract_xml_tag(item, "title")
                link = self._extract_xml_tag(item, "link")
                pub_date = self._extract_xml_tag(item, "pubDate")
                source = self._extract_xml_tag(item, "source")
                description = self._extract_xml_tag(item, "description")

                article_url = self._extract_article_url(description) or link

                # Resolve Google News redirect to get actual article URL
                if "news.google.com" in article_url:
                    article_url = self._resolve_google_news_url(article_url)

                # Parse bundled articles from description into clean format
                clean_snippet = self._parse_rss_description(description)

                if title and link:
                    results.append(
                        {
                            "title": self._decode_html(title),
                            "url": article_url,
                            "snippet": clean_snippet,
                            "source": source or urlparse(article_url).hostname or "",
                            "publish_date": pub_date,
                            "type": "news",
                        }
                    )

            return results
        except Exception as e:
            logger.error(f"Google News search error: {e}")
            return []

    def _google_web_search(self, query, limit, page=1):
        try:
            from scraper.services.shared_client import fetch
            from scraper.services.rate_limiter import throttle

            start = (page - 1) * 10
            url = f"https://www.google.com/search?q={urlencode({'': query})[1:]}&hl=id&gl=ID&num={min(limit, 10)}&start={start}"

            throttle("www.google.com")
            response = fetch(url)

            if response.status_code == 429:
                logger.warning("Google rate limited us (429)")
                return []

            if response.status_code != 200:
                logger.warning(f"Google returned status {response.status_code}")
                return []

            html = response.text

            # Check for CAPTCHA
            if "captcha" in html.lower() or "unusual traffic" in html.lower():
                logger.warning("Google CAPTCHA detected")
                return []

            results = []

            # Pattern 1: /url?q=REAL_URL
            matches = re.findall(r'<a[^>]+href="/url\?q=([^&"]+)[^"]*"[^>]*>(.*?)</a>', html, re.DOTALL)
            for url_match, title_html in matches:
                if len(results) >= limit:
                    break
                clean_url = unquote(url_match)
                title = re.sub(r"<[^>]*>", "", title_html).strip()

                if "google.com" in clean_url:
                    continue
                if "youtube.com/results" in clean_url:
                    continue

                if title and clean_url.startswith("http"):
                    results.append(
                        {
                            "title": self._decode_html(title),
                            "url": clean_url,
                            "snippet": "",
                            "source": urlparse(clean_url).hostname or "",
                            "type": "web",
                        }
                    )

            # Pattern 2: <a href="https://..."><h3>...</h3></a>
            if not results:
                matches = re.findall(r'<a[^>]+href="(https?://[^"]+)"[^>]*>\s*<h3[^>]*>(.*?)</h3>', html, re.DOTALL)
                for url_match, title_html in matches:
                    if len(results) >= limit:
                        break
                    if "google.com" in url_match:
                        continue
                    title = re.sub(r"<[^>]*>", "", title_html).strip()
                    if title:
                        results.append(
                            {
                                "title": self._decode_html(title),
                                "url": url_match,
                                "snippet": "",
                                "source": urlparse(url_match).hostname or "",
                                "type": "web",
                            }
                        )

            return results
        except Exception as e:
            logger.error(f"Google web search error: {e}")
            return []

    def _bing_search(self, query, limit):
        """Fallback search using Bing."""
        try:
            from scraper.services.shared_client import fetch
            from scraper.services.rate_limiter import throttle

            url = f"https://www.bing.com/search?q={urlencode({'': query})[1:]}&count={min(limit, 10)}"
            throttle("www.bing.com")
            response = fetch(url)

            if response.status_code != 200:
                return []

            html = response.text
            results = []

            # Bing result pattern: <li class="b_algo"><h2><a href="URL">TITLE</a></h2>
            matches = re.findall(
                r'<li class="b_algo">\s*<h2>\s*<a href="(https?://[^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL
            )
            for url_match, title_html in matches:
                if len(results) >= limit:
                    break
                if "bing.com" in url_match or "microsoft.com" in url_match:
                    continue
                title = re.sub(r"<[^>]*>", "", title_html).strip()
                if title:
                    results.append(
                        {
                            "title": self._decode_html(title),
                            "url": url_match,
                            "snippet": "",
                            "source": urlparse(url_match).hostname or "",
                            "type": "web",
                        }
                    )

            return results
        except Exception as e:
            logger.error(f"Bing search error: {e}")
            return []

    def _duckduckgo_search(self, query, limit):
        """Fallback search using DuckDuckGo HTML."""
        try:
            from scraper.services.shared_client import fetch
            from scraper.services.rate_limiter import throttle

            url = f"https://html.duckduckgo.com/html/?q={urlencode({'': query})[1:]}"
            throttle("duckduckgo.com")
            response = fetch(url)

            if response.status_code != 200:
                return []

            html = response.text
            results = []

            # DuckDuckGo HTML result pattern
            matches = re.findall(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
            for url_match, title_html in matches:
                if len(results) >= limit:
                    break
                if "duckduckgo.com" in url_match:
                    continue
                title = re.sub(r"<[^>]*>", "", title_html).strip()
                # DuckDuckGo uses //duckduckgo.com/l/?uddg=REAL_URL format
                if "uddg=" in url_match:
                    from urllib.parse import parse_qs, urlparse as up

                    parsed = up(url_match)
                    qs = parse_qs(parsed.query)
                    url_match = qs.get("uddg", [url_match])[0]
                if title and url_match.startswith("http"):
                    results.append(
                        {
                            "title": self._decode_html(title),
                            "url": url_match,
                            "snippet": "",
                            "source": urlparse(url_match).hostname or "",
                            "type": "web",
                        }
                    )

            return results
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []

    def _extract_xml_tag(self, xml_text, tag):
        match = re.search(rf"<{tag}(?:[^>]*)>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{tag}>", xml_text, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _extract_article_url(self, html):
        match = re.search(r'href="(https?://(?!news\.google\.com)[^"]+)"', html, re.IGNORECASE)
        if match:
            return match.group(1)
        match = re.search(r'<a[^>]+href="([^"]+)"[^>]*>', html, re.IGNORECASE)
        if match:
            url = match.group(1)
            if "news.google.com" not in url and url.startswith("http"):
                return url
        return ""

    def _decode_html(self, text):
        import html

        return html.unescape(text)

    def _strip_html(self, text):
        if not text:
            return ""
        import html as html_mod

        clean = html_mod.unescape(text)
        clean = html_mod.unescape(clean)
        clean = re.sub(r"<[^>]*>", " ", clean)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

    def _parse_rss_description(self, html_desc):
        """Parse Google News RSS description into clean 'Title - Source' lines."""
        if not html_desc:
            return ""
        import html as html_mod

        decoded = html_mod.unescape(html_mod.unescape(html_desc))

        # Extract all <li> items
        items = re.findall(r"<li[^>]*>(.*?)</li>", decoded, re.DOTALL)
        if not items:
            # Single article (no <li>), just strip and return
            clean = re.sub(r"<[^>]*>", " ", decoded)
            clean = re.sub(r"\s+", " ", clean).strip()
            return clean

        articles = []
        for item_html in items:
            # Extract title from <a> tag
            title_m = re.search(r"<a[^>]*>(.*?)</a>", item_html, re.DOTALL)
            title = re.sub(r"<[^>]*>", "", title_m.group(1)).strip() if title_m else ""
            # Extract source from <font> tag
            source_m = re.search(r"<font[^>]*>(.*?)</font>", item_html, re.DOTALL)
            source = re.sub(r"<[^>]*>", "", source_m.group(1)).strip() if source_m else ""
            if title:
                articles.append(f"{title} - {source}" if source else title)

        return "\n".join(articles)
