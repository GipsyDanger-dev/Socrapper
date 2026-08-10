import re
import random
import hashlib
import logging
import os
from datetime import datetime, timedelta
from urllib.parse import quote_plus, urlencode, urlparse, parse_qs

logger = logging.getLogger(__name__)


class WebScraperService:
    PLATFORM_URLS = {
        "twitter": "https://nitter.net/search?f=tweets&q={q}",
        "reddit": "https://old.reddit.com/search?q={q}&sort=relevance",
        "news": "https://news.google.com/search?q={q}",
        "stackoverflow": "https://stackoverflow.com/search?q={q}",
        "github": "https://github.com/search?q={q}&type=repositories",
        "youtube": "https://www.youtube.com/results?search_query={q}",
        "instagram": "https://www.google.com/search?q=site:instagram.com+{q}",
        "tiktok": "https://www.google.com/search?q=site:tiktok.com+{q}",
        "facebook": "https://www.google.com/search?q=site:facebook.com+{q}",
    }

    def scrape(self, query, platform=None, limit=10):
        # YouTube: use API if key is available (paginated, so limit > 50 works)
        if platform == "youtube":
            api_key = os.getenv("YOUTUBE_API_KEY", "")
            if api_key:
                results = self._scrape_youtube_api(query, limit, api_key)
                if results:
                    return results

        # Twitter/X: search engines (Google/Bing/DDG) return real x.com post
        # URLs. Nitter is mostly dead, and fabricating status IDs yields
        # dead links, so this path comes first for clickable results.
        if platform == "twitter":
            results = self._scrape_twitter_via_search(query, limit)
            if results:
                return results

        # Try Google News RSS first (works for all platforms, gives real data)
        results = self._scrape_via_news_rss(query, platform, limit)
        if results:
            return results

        # Fallback to scrapling web scrape
        url = self._build_url(platform, query)
        try:
            from scrapling import StealthyFetcher

            page = StealthyFetcher().fetch(url)
            results = self._extract_results(page, platform, query, limit)
            if results:
                return results
        except Exception as e:
            logger.warning(f"Scrapling failed for {platform}: {e}")

        return self._get_fallback(query, platform, limit)

    def _scrape_youtube_api(self, query, limit, api_key):
        """Use YouTube Data API v3 for accurate results.

        The API caps maxResults at 50 per request, so larger limits are
        filled by following the nextPageToken returned by each page.
        """
        try:
            from .shared_client import fetch

            results = []
            page_token = ""

            while len(results) < limit:
                page_size = min(50, limit - len(results))
                search_url = (
                    f"https://www.googleapis.com/youtube/v3/search?"
                    f"part=snippet&q={quote_plus(query)}&maxResults={page_size}"
                    f"&type=video&key={api_key}"
                )
                if page_token:
                    search_url += f"&pageToken={page_token}"

                response = fetch(search_url)
                data = response.json()

                items = data.get("items", [])
                for item in items:
                    snippet = item.get("snippet", {})
                    video_id = item.get("id", {}).get("videoId", "")
                    if not video_id:
                        continue

                    # Get video statistics (views, likes, comments)
                    stats = self._get_youtube_video_stats(video_id, api_key)

                    results.append(
                        {
                            "id": f"yt-{video_id}",
                            "platform": "youtube",
                            "author": snippet.get("channelTitle", "Unknown"),
                            "text": f"{snippet.get('title', '')}. {snippet.get('description', '')[:200]}",
                            "timestamp": snippet.get("publishedAt", datetime.now().isoformat()),
                            "likes": stats.get("likeCount", 0),
                            "comments": stats.get("commentCount", 0),
                            "shares": 0,
                            "url": f"https://www.youtube.com/watch?v={video_id}",
                            "views": stats.get("viewCount", 0),
                            "thumbnail": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                        }
                    )
                    if len(results) >= limit:
                        break

                page_token = data.get("nextPageToken", "")
                if not page_token or not items:
                    break

            logger.info(f"YouTube API returned {len(results)} results for '{query}'")
            return results if results else None
        except Exception as e:
            logger.warning(f"YouTube API failed: {e}")
            return None

    def _scrape_twitter_via_search(self, query, limit):
        """Find real X/Twitter post URLs through search engines.

        Search for ``site:x.com OR site:twitter.com <query>`` and keep only
        results whose URL belongs to x.com/twitter.com, so every returned
        item links to an actual tweet instead of a fabricated status ID.
        """
        try:
            from surfer.services.search_engine_service import SearchEngineService

            searcher = SearchEngineService()
            found = searcher.search(f"{query} site:x.com OR site:twitter.com", limit)

            results = []
            seen = set()
            for item in found:
                url = item.get("url", "")
                host = (urlparse(url).hostname or "").lower()
                # Exact host match or subdomain — never loose substring (myx.com etc.)
                if not (
                    host == "x.com" or host.endswith(".x.com") or host == "twitter.com" or host.endswith(".twitter.com")
                ):
                    continue
                if url in seen:
                    continue
                seen.add(url)

                path_parts = urlparse(url).path.split("/")
                username = path_parts[1] if len(path_parts) > 1 else ""

                results.append(
                    {
                        "id": hashlib.md5(f"twitter-{url}".encode()).hexdigest()[:12],
                        "platform": "twitter",
                        "author": f"@{username}" if username else "Twitter/X",
                        "text": item.get("title") or item.get("snippet") or f"Tweet about {query}",
                        "timestamp": self._parse_date(item.get("publish_date")),
                        "likes": 0,
                        "comments": 0,
                        "shares": 0,
                        "url": url,
                    }
                )
                if len(results) >= limit:
                    break

            return results
        except Exception as e:
            logger.warning(f"Twitter search-engine scrape failed: {e}")
            return []

    def _resolve_url(self, href, base=""):
        """Convert a scraped href into a usable absolute URL (or '').

        Handles Google result redirects (``/url?q=...``), protocol-relative
        URLs (``//host/...``) and site-relative paths (``/path``).
        """
        if not href:
            return ""
        href = href.strip()
        if href.startswith("/url?q="):
            qs = parse_qs(href.split("?", 1)[1])
            decoded = qs.get("q", [""])[0]
            return decoded if decoded.startswith("http") else ""
        if href.startswith("http"):
            return href
        if href.startswith("//"):
            return "https:" + href
        if href.startswith("/") and base:
            return base + href
        return ""

    def _get_youtube_video_stats(self, video_id, api_key):
        """Get video statistics (views, likes, comments)."""
        try:
            from .shared_client import fetch

            stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={api_key}"
            response = fetch(stats_url)
            data = response.json()
            if "items" in data and data["items"]:
                stats = data["items"][0].get("statistics", {})
                return {
                    "viewCount": int(stats.get("viewCount", 0)),
                    "likeCount": int(stats.get("likeCount", 0)),
                    "commentCount": int(stats.get("commentCount", 0)),
                }
        except Exception as e:
            logger.debug(f"YouTube stats fetch failed: {e}")
        return {"viewCount": 0, "likeCount": 0, "commentCount": 0}

    def _scrape_via_news_rss(self, query, platform, limit):
        """Use Google News RSS to get real articles for any platform."""
        try:
            search_query = query
            if platform == "twitter":
                search_query = f"{query} site:twitter.com OR site:x.com"
            elif platform == "reddit":
                search_query = f"{query} site:reddit.com"
            elif platform == "github":
                search_query = f"{query} site:github.com"
            elif platform == "stackoverflow":
                search_query = f"{query} site:stackoverflow.com"
            elif platform == "youtube":
                search_query = f"{query} site:youtube.com"

            rss_url = f"https://news.google.com/rss/search?q={urlencode({'': search_query})[1:]}&hl=id&gl=ID&ceid=ID:id"

            from .shared_client import fetch
            from .rate_limiter import throttle

            throttle("news.google.com")
            response = fetch(rss_url)
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

                # Extract actual article URL from description
                article_url = self._extract_article_url(description) or link

                # Decode Google News URL to get actual article URL
                if "news.google.com" in article_url:
                    article_url = self._decode_google_news_url(article_url)

                # Parse bundled articles into clean format
                clean_snippet = self._parse_rss_description(description)
                clean_snippet = re.sub(r"https?://news\.google\.com[^\s]*", "", clean_snippet)
                clean_snippet = re.sub(r"\s+", " ", clean_snippet).strip()

                # Clean title too
                clean_title = self._strip_html(title)

                if clean_title and link:
                    results.append(
                        {
                            "id": hashlib.md5(f"{platform or 'news'}-{len(results)}-{query}".encode()).hexdigest()[:12],
                            "platform": platform or "news",
                            "author": source or self._extract_domain(article_url),
                            "text": f"{clean_title}. {clean_snippet}" if clean_snippet else clean_title,
                            "timestamp": self._parse_date(pub_date),
                            "likes": 0,
                            "comments": 0,
                            "shares": 0,
                            "url": article_url,
                        }
                    )

            return results if results else None
        except Exception as e:
            logger.warning(f"News RSS scrape failed: {e}")
            return None

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

    def _decode_google_news_url(self, url):
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

    def _parse_date(self, date_str):
        if not date_str:
            return (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat()
        try:
            from email.utils import parsedate_to_datetime

            return parsedate_to_datetime(date_str).isoformat()
        except Exception:
            return (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat()

    def _strip_html(self, text):
        """Remove all HTML tags and decode common entities."""
        if not text:
            return ""
        import html as html_mod

        # Decode entities first (handles double-encoded HTML like &lt;a&gt;)
        clean = html_mod.unescape(text)
        # Run twice for double-encoding
        clean = html_mod.unescape(clean)
        # Remove tags
        clean = re.sub(r"<[^>]*>", " ", clean)
        # Collapse whitespace
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

    def _parse_rss_description(self, html_desc):
        """Parse Google News RSS description into clean 'Title - Source' lines."""
        if not html_desc:
            return ""
        import html as html_mod

        decoded = html_mod.unescape(html_mod.unescape(html_desc))

        items = re.findall(r"<li[^>]*>(.*?)</li>", decoded, re.DOTALL)
        if not items:
            clean = re.sub(r"<[^>]*>", " ", decoded)
            clean = re.sub(r"\s+", " ", clean).strip()
            return clean

        articles = []
        for item_html in items:
            title_m = re.search(r"<a[^>]*>(.*?)</a>", item_html, re.DOTALL)
            title = re.sub(r"<[^>]*>", "", title_m.group(1)).strip() if title_m else ""
            source_m = re.search(r"<font[^>]*>(.*?)</font>", item_html, re.DOTALL)
            source = re.sub(r"<[^>]*>", "", source_m.group(1)).strip() if source_m else ""
            if title:
                articles.append(f"{title} - {source}" if source else title)

        return "\n".join(articles)

    def get_platforms(self):
        return [
            {"id": "twitter", "name": "Twitter/X", "icon": "twitter"},
            {"id": "reddit", "name": "Reddit", "icon": "reddit"},
            {"id": "news", "name": "News", "icon": "newspaper"},
            {"id": "stackoverflow", "name": "Stack Overflow", "icon": "stack-overflow"},
            {"id": "github", "name": "GitHub", "icon": "github"},
            {"id": "youtube", "name": "YouTube", "icon": "youtube"},
            {"id": "instagram", "name": "Instagram", "icon": "instagram"},
            {"id": "tiktok", "name": "TikTok", "icon": "tiktok"},
            {"id": "facebook", "name": "Facebook", "icon": "facebook"},
        ]

    def _build_url(self, platform, query):
        encoded = quote_plus(query)
        if platform and platform in self.PLATFORM_URLS:
            return self.PLATFORM_URLS[platform].format(q=encoded)
        return f"https://www.google.com/search?q={encoded}"

    def _extract_results(self, page, platform, query, limit):
        results = []
        try:
            if platform == "twitter":
                results = self._extract_twitter(page, query, limit)
            elif platform == "reddit":
                results = self._extract_reddit(page, query, limit)
            elif platform == "news":
                results = self._extract_news(page, query, limit)
            elif platform == "stackoverflow":
                results = self._extract_stackoverflow(page, query, limit)
            elif platform == "github":
                results = self._extract_github(page, query, limit)
            elif platform == "youtube":
                results = self._extract_youtube(page, query, limit)
            else:
                results = self._extract_generic(page, query, limit)
        except Exception:
            pass
        return results

    def _extract_twitter(self, page, query, limit):
        """Extract tweets from a nitter page using the real permalink href."""
        results = []
        tweets = page.css(".timeline-item") or page.css('[data-testid="tweet"]') or []
        for i, tweet in enumerate(tweets[:limit]):
            text_el = tweet.css(".tweet-content") or tweet.css('[data-testid="tweetText"]')
            text = text_el[0].text.strip() if text_el else f"Tweet about {query}"
            user_el = tweet.css(".username") or tweet.css('[data-testid="User-Name"]')
            author = user_el[0].text.strip() if user_el else f"@user{i}"
            # nitter renders the permalink as .tweet-link href="/user/status/123"
            link_el = tweet.css(".tweet-link") or tweet.css('a[href*="/status/"]')
            href = link_el[0].attrib.get("href", "") if link_el else ""
            # nitter relative permalink -> real X permalink
            url = self._resolve_url(href, base="https://x.com")
            results.append(
                {
                    "id": hashlib.md5(f"twitter-{i}-{query}".encode()).hexdigest()[:12],
                    "platform": "twitter",
                    "author": author,
                    "text": text,
                    "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "url": url,
                }
            )
        return results

    def _extract_reddit(self, page, query, limit):
        results = []
        posts = page.css(".search-result") or page.css(".thing") or []
        for i, post in enumerate(posts[:limit]):
            title_el = post.css(".search-title a") or post.css("a.title")
            title = title_el[0].text.strip() if title_el else f"Reddit post about {query}"
            author_el = post.css(".search-author .author") or post.css(".author")
            author = author_el[0].text.strip() if author_el else f"u/user{i}"
            score_el = post.css(".search-score") or post.css(".score")
            score = 0
            if score_el:
                try:
                    score = int(re.sub(r"[^\d-]", "", score_el[0].text))
                except ValueError:
                    score = 0
            href = title_el[0].attrib.get("href", "") if title_el else ""
            results.append(
                {
                    "id": hashlib.md5(f"reddit-{i}-{query}".encode()).hexdigest()[:12],
                    "platform": "reddit",
                    "author": author,
                    "text": title,
                    "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
                    "likes": score,
                    "comments": 0,
                    "shares": 0,
                    "url": self._resolve_url(href, base="https://old.reddit.com"),
                }
            )
        return results

    def _extract_news(self, page, query, limit):
        results = []
        articles = page.css("article") or page.css(".JtKRv") or page.css(".ipQwMb") or []
        for i, article in enumerate(articles[:limit]):
            link = article.css("a")
            title = link[0].text.strip() if link else f"News about {query}"
            href = link[0].attrib.get("href", "") if link else ""
            source_el = article.css(".vr1PYe") or article.css(".CEMjEf")
            source = source_el[0].text.strip() if source_el else "News Source"
            results.append(
                {
                    "id": hashlib.md5(f"news-{i}-{query}".encode()).hexdigest()[:12],
                    "platform": "news",
                    "author": source,
                    "text": title,
                    "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "url": self._resolve_url(href, base="https://news.google.com"),
                }
            )
        return results

    def _extract_stackoverflow(self, page, query, limit):
        results = []
        questions = page.css(".question-summary") or page.css(".s-post-summary") or []
        for i, q in enumerate(questions[:limit]):
            title_el = q.css(".question-hyperlink") or q.css(".s-link")
            title = title_el[0].text.strip() if title_el else f"Question about {query}"
            votes_el = q.css(".vote-count-post") or q.css(".s-post-summary--stats-item-number")
            votes = 0
            if votes_el:
                try:
                    votes = int(votes_el[0].text.strip())
                except ValueError:
                    votes = 0
            href = title_el[0].attrib.get("href", "") if title_el else ""
            results.append(
                {
                    "id": hashlib.md5(f"stackoverflow-{i}-{query}".encode()).hexdigest()[:12],
                    "platform": "stackoverflow",
                    "author": f"developer{i}",
                    "text": title,
                    "timestamp": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                    "likes": votes,
                    "comments": 0,
                    "shares": 0,
                    "url": self._resolve_url(href, base="https://stackoverflow.com"),
                }
            )
        return results

    def _extract_github(self, page, query, limit):
        results = []
        repos = page.css(".repo-list-item") or page.css('[data-testid="results-list"] > div') or []
        for i, repo in enumerate(repos[:limit]):
            title_el = repo.css("a.v-align-middle") or repo.css('a[data-testid="listitem-title"]')
            title = title_el[0].text.strip() if title_el else f"repo about {query}"
            desc_el = repo.css(".mb-1") or repo.css("p")
            desc = desc_el[0].text.strip() if desc_el else f"GitHub repository for {query}"
            href = title_el[0].attrib.get("href", "") if title_el else ""
            results.append(
                {
                    "id": hashlib.md5(f"github-{i}-{query}".encode()).hexdigest()[:12],
                    "platform": "github",
                    "author": title.split("/")[0] if "/" in title else f"user{i}",
                    "text": f"{title}: {desc}" if desc else title,
                    "timestamp": (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat(),
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "url": self._resolve_url(href, base="https://github.com"),
                }
            )
        return results

    def _extract_youtube(self, page, query, limit):
        results = []
        videos = page.css("ytd-video-renderer") or page.css(".video-renderer") or []
        for i, video in enumerate(videos[:limit]):
            title_el = video.css("#video-title") or video.css("a#video-title")
            title = title_el[0].text.strip() if title_el else f"Video about {query}"
            channel_el = video.css(".ytd-channel-name a") or video.css("#channel-name a")
            channel = channel_el[0].text.strip() if channel_el else f"Channel{i}"
            href = title_el[0].attrib.get("href", "") if title_el else ""
            results.append(
                {
                    "id": hashlib.md5(f"youtube-{i}-{query}".encode()).hexdigest()[:12],
                    "platform": "youtube",
                    "author": channel,
                    "text": title,
                    "timestamp": (datetime.now() - timedelta(days=random.randint(1, 14))).isoformat(),
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "url": self._resolve_url(href, base="https://www.youtube.com"),
                }
            )
        return results

    def _extract_generic(self, page, query, limit):
        results = []
        links = page.css("a[href]") or []
        seen = set()
        for link in links:
            if len(results) >= limit:
                break
            href = link.attrib.get("href", "")
            text = link.text.strip()
            if not text or len(text) < 10 or href in seen:
                continue
            if any(skip in href for skip in ["javascript:", "#", ".css", ".js", ".png", ".jpg"]):
                continue
            seen.add(href)
            results.append(
                {
                    "id": hashlib.md5(f"web-{len(results)}-{query}".encode()).hexdigest()[:12],
                    "platform": "web",
                    "author": self._extract_domain(href),
                    "text": text[:300],
                    "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "url": href if href.startswith("http") else f"https://google.com{href}",
                }
            )
        return results

    def _extract_domain(self, url):
        match = re.search(r"https?://(?:www\.)?([^/]+)", url)
        return match.group(1) if match else "unknown"

    def _get_fallback(self, query, platform, limit):
        """Generate placeholder results when scraping fails.

        These are clearly marked as fallback data, not real scraped content.
        Timestamps use a fixed sentinel value so they cannot be mistaken for
        real data.  Consumers should check ``is_fallback`` before displaying
        these results.
        """
        platform = platform or "web"
        results = []
        for i in range(min(limit, 10)):
            seed = hashlib.md5(f"{query}-{platform}-{i}".encode()).hexdigest()
            results.append(
                {
                    "id": seed[:12],
                    "platform": platform,
                    "author": f"{platform}_user_{seed[:6]}",
                    "text": f"[Fallback] Tidak dapat mengambil data real dari {platform.title()} untuk '{query}'. Coba gunakan platform atau keyword lain.",
                    "timestamp": None,  # Not a real timestamp — indicates fallback data
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "url": "",
                    "is_fallback": True,
                }
            )
        return results
