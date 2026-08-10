"""
Unit tests for WebScraperService.
Tests URL building, XML parsing, fallback behavior.
"""

import pytest
from scraper.services.web_scraper_service import WebScraperService


@pytest.fixture
def service():
    return WebScraperService()


class TestBuildUrl:
    """Test URL construction for different platforms."""

    def test_twitter_url(self, service):
        url = service._build_url("twitter", "python")
        assert "nitter.net" in url
        assert "python" in url

    def test_reddit_url(self, service):
        url = service._build_url("reddit", "django")
        assert "old.reddit.com" in url
        assert "django" in url

    def test_youtube_url(self, service):
        url = service._build_url("youtube", "tutorial")
        assert "youtube.com" in url
        assert "tutorial" in url

    def test_unknown_platform_fallback(self, service):
        url = service._build_url("unknown", "test")
        assert "google.com" in url

    def test_none_platform_fallback(self, service):
        url = service._build_url(None, "test")
        assert "google.com" in url

    def test_special_characters_encoded(self, service):
        url = service._build_url("twitter", "hello world & more")
        assert "hello+world" in url or "hello%20world" in url

    def test_empty_query(self, service):
        url = service._build_url("twitter", "")
        assert "nitter.net" in url


class TestExtractXmlTag:
    """Test XML tag extraction."""

    def test_simple_tag(self, service):
        result = service._extract_xml_tag("<title>Test Title</title>", "title")
        assert result == "Test Title"

    def test_cdata_tag(self, service):
        result = service._extract_xml_tag("<title><![CDATA[CDATA Title]]></title>", "title")
        assert result == "CDATA Title"

    def test_missing_tag(self, service):
        result = service._extract_xml_tag("<other>content</other>", "title")
        assert result == ""

    def test_empty_tag(self, service):
        result = service._extract_xml_tag("<title></title>", "title")
        assert result == ""

    def test_tag_with_attributes(self, service):
        result = service._extract_xml_tag('<source url="http://example.com">CNN</source>', "source")
        assert result == "CNN"


class TestStripHtml:
    """Test HTML stripping."""

    def test_simple_html(self, service):
        result = service._strip_html("<p>Hello <b>world</b></p>")
        assert result == "Hello world"

    def test_entities_decoded(self, service):
        result = service._strip_html("&amp; &lt; &gt;")
        # Entities are decoded, then whitespace collapsed
        assert "&amp;" not in result  # Should be decoded
        assert "&lt;" not in result

    def test_double_encoded(self, service):
        result = service._strip_html("&amp;amp;")
        # Double unescape: &amp;amp; → &amp; → &
        assert result == "&"

    def test_empty_string(self, service):
        result = service._strip_html("")
        assert result == ""

    def test_none_input(self, service):
        result = service._strip_html(None)
        assert result == ""

    def test_no_html(self, service):
        result = service._strip_html("Plain text")
        assert result == "Plain text"


class TestParseRssDescription:
    """Test RSS description parsing."""

    def test_empty_description(self, service):
        result = service._parse_rss_description("")
        assert result == ""

    def test_none_description(self, service):
        result = service._parse_rss_description(None)
        assert result == ""

    def test_single_article_no_list(self, service):
        html = "<p>Some article text</p>"
        result = service._parse_rss_description(html)
        assert "Some article text" in result

    def test_list_items(self, service):
        html = '<ul><li><a href="#">Title 1</a> <font>CNN</font></li><li><a href="#">Title 2</a> <font>BBC</font></li></ul>'
        result = service._parse_rss_description(html)
        assert "Title 1" in result
        assert "Title 2" in result


class TestExtractDomain:
    """Test domain extraction."""

    def test_simple_domain(self, service):
        result = service._extract_domain("https://example.com/path")
        assert result == "example.com"

    def test_www_stripped(self, service):
        result = service._extract_domain("https://www.example.com/path")
        assert result == "example.com"

    def test_invalid_url(self, service):
        result = service._extract_domain("not-a-url")
        assert result == "unknown"


class TestGetFallback:
    """Test fallback result generation."""

    def test_fallback_returns_results(self, service):
        results = service._get_fallback("test", "twitter", 5)
        assert len(results) == 5

    def test_fallback_marked(self, service):
        results = service._get_fallback("test", "twitter", 3)
        for r in results:
            assert r.get("is_fallback") is True

    def test_fallback_limit_capped(self, service):
        results = service._get_fallback("test", "twitter", 100)
        assert len(results) <= 10  # Fallback caps at 10

    def test_fallback_has_platform(self, service):
        results = service._get_fallback("test", "reddit", 3)
        for r in results:
            assert r["platform"] == "reddit"

    def test_fallback_none_platform(self, service):
        results = service._get_fallback("test", None, 3)
        for r in results:
            assert r["platform"] == "web"


class TestGetPlatforms:
    """Test platform list."""

    def test_returns_all_platforms(self, service):
        platforms = service.get_platforms()
        ids = [p["id"] for p in platforms]
        assert "twitter" in ids
        assert "reddit" in ids
        assert "youtube" in ids
        assert len(platforms) == 9


class TestParseDate:
    """Test date parsing."""

    def test_empty_date(self, service):
        result = service._parse_date("")
        assert result  # Should return a fallback date

    def test_none_date(self, service):
        result = service._parse_date(None)
        assert result  # Should return a fallback date

    def test_valid_rfc2822(self, service):
        result = service._parse_date("Sat, 14 Jun 2026 10:00:00 GMT")
        assert "2026" in result

    def test_invalid_date_fallback(self, service):
        result = service._parse_date("not a date")
        assert result  # Should return a fallback date


class _FakeAttrib:
    """Minimal stand-in for scrapling element attrib dict."""

    def __init__(self, href):
        self._href = href

    def get(self, key, default=""):
        return self._href if key == "href" else default


class _FakeEl:
    """Minimal stand-in for a scrapling element with .css() and .attrib.

    ``_FakeEl(href="/realuser/status/123")`` simulates a tweet that carries a
    real permalink href; ``_FakeEl(text="...")`` simulates text/username
    nodes found inside a tweet.
    """

    def __init__(self, text="", href=None):
        self.text = text
        self.attrib = _FakeAttrib(href) if href is not None else {}
        self._has_text = bool(text)
        self._href = href

    def css(self, selector):
        if "tweet-content" in selector or "tweetText" in selector:
            return [_FakeEl(text="Real tweet text")] if self._has_text else []
        if "username" in selector or "User-Name" in selector:
            return [_FakeEl(text="@realuser")] if self._has_text else []
        if "tweet-link" in selector or "status/" in selector:
            return [_FakeEl(href=self._href)] if self._href else []
        return []


class TestResolveUrl:
    """Test URL resolution (real links, no fabricated URLs)."""

    def test_absolute_url_passthrough(self, service):
        assert service._resolve_url("https://x.com/user/status/123") == "https://x.com/user/status/123"

    def test_protocol_relative_url(self, service):
        assert service._resolve_url("//x.com/user/status/1") == "https://x.com/user/status/1"

    def test_site_relative_url_with_base(self, service):
        assert (
            service._resolve_url("/watch?v=abc", base="https://www.youtube.com")
            == "https://www.youtube.com/watch?v=abc"
        )

    def test_google_redirect_decoded(self, service):
        href = "/url?q=https%3A%2F%2Fx.com%2Fuser%2Fstatus%2F99&sa=U"
        assert service._resolve_url(href) == "https://x.com/user/status/99"

    def test_empty_href_returns_empty(self, service):
        assert service._resolve_url("") == ""
        assert service._resolve_url(None) == ""

    def test_relative_url_without_base_returns_empty(self, service):
        assert service._resolve_url("/some/path") == ""


class TestExtractTwitterRealUrl:
    """Twitter extraction must use real permalinks, never fabricated IDs."""

    def test_uses_real_permalink_from_page(self, service):
        tweet = _FakeEl(href="/realuser/status/1234567890", text="tweet")
        page = type("Page", (), {"css": lambda self, s: [tweet] if "timeline-item" in s else []})()

        results = service._extract_twitter(page, "query", 5)

        assert len(results) == 1
        assert results[0]["url"] == "https://x.com/realuser/status/1234567890"
        assert "random" not in results[0]["url"]

    def test_no_url_when_href_missing(self, service):
        # A tweet with text but NO permalink -> url stays empty (no dead link)
        tweet = _FakeEl(text="tweet without link")
        page = type("Page", (), {"css": lambda self, s: [tweet] if "timeline-item" in s else []})()

        results = service._extract_twitter(page, "query", 5)

        assert len(results) == 1
        assert results[0]["url"] == ""


class TestScrapeTwitterViaSearch:
    """Search-engine path returns only real x.com/twitter.com URLs."""

    def test_filters_to_twitter_hosts(self, service, monkeypatch):
        fake_items = [
            {"url": "https://x.com/elon/status/1", "title": "Tweet A", "publish_date": ""},
            {"url": "https://twitter.com/someone/status/2", "title": "Tweet B", "publish_date": ""},
            {"url": "https://example.com/article", "title": "Not a tweet", "publish_date": ""},
        ]
        monkeypatch.setattr(
            "surfer.services.search_engine_service.SearchEngineService.search",
            lambda self, q, lim: fake_items,
        )

        results = service._scrape_twitter_via_search("query", 5)

        assert len(results) == 2
        urls = [r["url"] for r in results]
        assert "https://x.com/elon/status/1" in urls
        assert "https://twitter.com/someone/status/2" in urls
        assert all(any(h in u for h in ["x.com", "twitter.com"]) for u in urls)
        assert results[0]["platform"] == "twitter"

    def test_empty_when_no_twitter_results(self, service, monkeypatch):
        monkeypatch.setattr(
            "surfer.services.search_engine_service.SearchEngineService.search",
            lambda self, q, lim: [{"url": "https://example.com/a", "title": "x"}],
        )

        assert service._scrape_twitter_via_search("query", 5) == []

    def test_respects_limit(self, service, monkeypatch):
        fake_items = [
            {"url": f"https://x.com/u{str(i)}/status/{i}", "title": f"T{i}", "publish_date": ""} for i in range(10)
        ]
        monkeypatch.setattr(
            "surfer.services.search_engine_service.SearchEngineService.search",
            lambda self, q, lim: fake_items,
        )

        results = service._scrape_twitter_via_search("query", 3)
        assert len(results) == 3


class TestYouTubeApiPagination:
    """YouTube API must paginate past the 50-per-request cap."""

    class _FakeResponse:
        def __init__(self, data):
            self._data = data

        def json(self):
            return self._data

    def test_paginates_past_50(self, service, monkeypatch):
        page1_items = [
            {
                "snippet": {
                    "channelTitle": f"ch{i}",
                    "title": f"Video {i}",
                    "description": "d",
                    "publishedAt": "2026-01-01T00:00:00Z",
                },
                "id": {"videoId": f"vid{i}"},
            }
            for i in range(50)
        ]
        page2_items = [
            {
                "snippet": {
                    "channelTitle": "ch50",
                    "title": "Video 50",
                    "description": "d",
                    "publishedAt": "2026-01-01T00:00:00Z",
                },
                "id": {"videoId": "vid50"},
            }
        ]
        urls = []

        def fake_fetch(url):
            urls.append(url)
            if "pageToken=TOKEN2" in url:
                return self._FakeResponse({"items": page2_items})
            return self._FakeResponse({"items": page1_items, "nextPageToken": "TOKEN2"})

        monkeypatch.setattr("scraper.services.shared_client.fetch", fake_fetch)
        monkeypatch.setattr(service, "_get_youtube_video_stats", lambda vid, key: {})

        results = service._scrape_youtube_api("query", 51, "test-key")

        assert len(results) == 51
        assert len(urls) == 2
        assert "maxResults=50" in urls[0]  # first page requests the 50 cap
        assert "pageToken=TOKEN2" in urls[1]  # second page follows the cursor
        assert results[50]["url"] == "https://www.youtube.com/watch?v=vid50"

    def test_stops_when_no_next_page(self, service, monkeypatch):
        def fake_fetch(url):
            return self._FakeResponse({"items": []})

        monkeypatch.setattr("scraper.services.shared_client.fetch", fake_fetch)
        monkeypatch.setattr(service, "_get_youtube_video_stats", lambda vid, key: {})

        assert service._scrape_youtube_api("query", 100, "key") is None
