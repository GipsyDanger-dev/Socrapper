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
        url = service._build_url('twitter', 'python')
        assert 'nitter.net' in url
        assert 'python' in url

    def test_reddit_url(self, service):
        url = service._build_url('reddit', 'django')
        assert 'old.reddit.com' in url
        assert 'django' in url

    def test_youtube_url(self, service):
        url = service._build_url('youtube', 'tutorial')
        assert 'youtube.com' in url
        assert 'tutorial' in url

    def test_unknown_platform_fallback(self, service):
        url = service._build_url('unknown', 'test')
        assert 'google.com' in url

    def test_none_platform_fallback(self, service):
        url = service._build_url(None, 'test')
        assert 'google.com' in url

    def test_special_characters_encoded(self, service):
        url = service._build_url('twitter', 'hello world & more')
        assert 'hello+world' in url or 'hello%20world' in url

    def test_empty_query(self, service):
        url = service._build_url('twitter', '')
        assert 'nitter.net' in url


class TestExtractXmlTag:
    """Test XML tag extraction."""

    def test_simple_tag(self, service):
        result = service._extract_xml_tag('<title>Test Title</title>', 'title')
        assert result == 'Test Title'

    def test_cdata_tag(self, service):
        result = service._extract_xml_tag('<title><![CDATA[CDATA Title]]></title>', 'title')
        assert result == 'CDATA Title'

    def test_missing_tag(self, service):
        result = service._extract_xml_tag('<other>content</other>', 'title')
        assert result == ''

    def test_empty_tag(self, service):
        result = service._extract_xml_tag('<title></title>', 'title')
        assert result == ''

    def test_tag_with_attributes(self, service):
        result = service._extract_xml_tag('<source url="http://example.com">CNN</source>', 'source')
        assert result == 'CNN'


class TestStripHtml:
    """Test HTML stripping."""

    def test_simple_html(self, service):
        result = service._strip_html('<p>Hello <b>world</b></p>')
        assert result == 'Hello world'

    def test_entities_decoded(self, service):
        result = service._strip_html('&amp; &lt; &gt;')
        # Entities are decoded, then whitespace collapsed
        assert '&amp;' not in result  # Should be decoded
        assert '&lt;' not in result

    def test_double_encoded(self, service):
        result = service._strip_html('&amp;amp;')
        # Double unescape: &amp;amp; → &amp; → &
        assert result == '&'

    def test_empty_string(self, service):
        result = service._strip_html('')
        assert result == ''

    def test_none_input(self, service):
        result = service._strip_html(None)
        assert result == ''

    def test_no_html(self, service):
        result = service._strip_html('Plain text')
        assert result == 'Plain text'


class TestParseRssDescription:
    """Test RSS description parsing."""

    def test_empty_description(self, service):
        result = service._parse_rss_description('')
        assert result == ''

    def test_none_description(self, service):
        result = service._parse_rss_description(None)
        assert result == ''

    def test_single_article_no_list(self, service):
        html = '<p>Some article text</p>'
        result = service._parse_rss_description(html)
        assert 'Some article text' in result

    def test_list_items(self, service):
        html = '<ul><li><a href="#">Title 1</a> <font>CNN</font></li><li><a href="#">Title 2</a> <font>BBC</font></li></ul>'
        result = service._parse_rss_description(html)
        assert 'Title 1' in result
        assert 'Title 2' in result


class TestExtractDomain:
    """Test domain extraction."""

    def test_simple_domain(self, service):
        result = service._extract_domain('https://example.com/path')
        assert result == 'example.com'

    def test_www_stripped(self, service):
        result = service._extract_domain('https://www.example.com/path')
        assert result == 'example.com'

    def test_invalid_url(self, service):
        result = service._extract_domain('not-a-url')
        assert result == 'unknown'


class TestGetFallback:
    """Test fallback result generation."""

    def test_fallback_returns_results(self, service):
        results = service._get_fallback('test', 'twitter', 5)
        assert len(results) == 5

    def test_fallback_marked(self, service):
        results = service._get_fallback('test', 'twitter', 3)
        for r in results:
            assert r.get('is_fallback') is True

    def test_fallback_limit_capped(self, service):
        results = service._get_fallback('test', 'twitter', 100)
        assert len(results) <= 10  # Fallback caps at 10

    def test_fallback_has_platform(self, service):
        results = service._get_fallback('test', 'reddit', 3)
        for r in results:
            assert r['platform'] == 'reddit'

    def test_fallback_none_platform(self, service):
        results = service._get_fallback('test', None, 3)
        for r in results:
            assert r['platform'] == 'web'


class TestGetPlatforms:
    """Test platform list."""

    def test_returns_all_platforms(self, service):
        platforms = service.get_platforms()
        ids = [p['id'] for p in platforms]
        assert 'twitter' in ids
        assert 'reddit' in ids
        assert 'youtube' in ids
        assert len(platforms) == 9


class TestParseDate:
    """Test date parsing."""

    def test_empty_date(self, service):
        result = service._parse_date('')
        assert result  # Should return a fallback date

    def test_none_date(self, service):
        result = service._parse_date(None)
        assert result  # Should return a fallback date

    def test_valid_rfc2822(self, service):
        result = service._parse_date('Sat, 14 Jun 2026 10:00:00 GMT')
        assert '2026' in result

    def test_invalid_date_fallback(self, service):
        result = service._parse_date('not a date')
        assert result  # Should return a fallback date
