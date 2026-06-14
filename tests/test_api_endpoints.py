"""
API Integration Tests for all Socrapper endpoints.
Tests request validation, response format, error handling.
"""
import json
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def client():
    return APIClient()


# ============================================================
# GET /api/platforms
# ============================================================
class TestGetPlatforms:
    def test_returns_platforms(self, client):
        response = client.get('/api/platforms')
        assert response.status_code == 200
        assert 'platforms' in response.data
        assert 'twitter' in response.data['platforms']
        assert 'reddit' in response.data['platforms']
        assert 'youtube' in response.data['platforms']

    def test_platforms_count(self, client):
        response = client.get('/api/platforms')
        platforms = response.data['platforms']
        assert len(platforms) == 9  # twitter, reddit, news, stackoverflow, github, youtube, instagram, tiktok, facebook


# ============================================================
# POST /api/scrape
# ============================================================
class TestScrapeEndpoint:
    def test_missing_platform(self, client):
        response = client.post('/api/scrape', {'keyword': 'test', 'limit': 10}, format='json')
        assert response.status_code == 400
        assert response.data['success'] is False

    def test_invalid_platform(self, client):
        response = client.post('/api/scrape', {
            'platform': 'invalid_platform',
            'keyword': 'test',
            'limit': 10,
        }, format='json')
        assert response.status_code == 400
        assert 'Invalid platform' in response.data['error']

    def test_missing_keyword(self, client):
        response = client.post('/api/scrape', {
            'platform': 'twitter',
            'limit': 10,
        }, format='json')
        assert response.status_code == 400
        assert 'Keyword is required' in response.data['error']

    def test_empty_keyword(self, client):
        response = client.post('/api/scrape', {
            'platform': 'twitter',
            'keyword': '',
            'limit': 10,
        }, format='json')
        assert response.status_code == 400

    def test_keyword_too_long(self, client):
        response = client.post('/api/scrape', {
            'platform': 'twitter',
            'keyword': 'x' * 501,
            'limit': 10,
        }, format='json')
        assert response.status_code == 400
        assert 'too long' in response.data['error'].lower()

    def test_limit_zero(self, client):
        response = client.post('/api/scrape', {
            'platform': 'twitter',
            'keyword': 'test',
            'limit': 0,
        }, format='json')
        assert response.status_code == 400

    def test_limit_over_1000(self, client):
        response = client.post('/api/scrape', {
            'platform': 'twitter',
            'keyword': 'test',
            'limit': 1001,
        }, format='json')
        assert response.status_code == 400

    def test_invalid_limit_string(self, client):
        response = client.post('/api/scrape', {
            'platform': 'twitter',
            'keyword': 'test',
            'limit': 'abc',
        }, format='json')
        assert response.status_code == 400

    def test_valid_scrape_request(self, client):
        """Test a valid scrape request — may return fallback data if scraping fails."""
        response = client.post('/api/scrape', {
            'platform': 'news',
            'keyword': 'python programming',
            'limit': 5,
        }, format='json')
        # Should succeed even if scraping returns fallback
        assert response.status_code == 200
        assert response.data['success'] is True
        assert 'data' in response.data
        assert 'total' in response.data

    def test_scrape_response_has_sentiment(self, client):
        """Response should include sentiment analysis."""
        response = client.post('/api/scrape', {
            'platform': 'news',
            'keyword': 'test',
            'limit': 3,
        }, format='json')
        assert response.status_code == 200
        assert 'analysis' in response.data


# ============================================================
# POST /api/analyze
# ============================================================
class TestAnalyzeEndpoint:
    def test_missing_texts(self, client):
        response = client.post('/api/analyze', {}, format='json')
        assert response.status_code == 400

    def test_empty_texts_array(self, client):
        response = client.post('/api/analyze', {'texts': []}, format='json')
        assert response.status_code == 400

    def test_texts_not_array(self, client):
        response = client.post('/api/analyze', {'texts': 'not a list'}, format='json')
        assert response.status_code == 400

    def test_too_many_texts(self, client):
        response = client.post('/api/analyze', {'texts': ['text'] * 101}, format='json')
        assert response.status_code == 400
        assert '100' in response.data['error']

    def test_valid_analyze(self, client):
        response = client.post('/api/analyze', {
            'texts': ['This is amazing!', 'This is terrible.']
        }, format='json')
        assert response.status_code == 200
        assert response.data['success'] is True
        assert 'analysis' in response.data

    def test_analyze_single_text(self, client):
        response = client.post('/api/analyze', {
            'texts': ['I love this product!']
        }, format='json')
        assert response.status_code == 200


# ============================================================
# POST /api/export
# ============================================================
class TestExportEndpoint:
    def test_missing_data(self, client):
        response = client.post('/api/export', {'type': 'scraping'}, format='json')
        assert response.status_code == 400

    def test_invalid_type(self, client):
        response = client.post('/api/export', {
            'data': [{'id': '1'}],
            'type': 'invalid',
        }, format='json')
        assert response.status_code == 400

    def test_valid_scraping_export(self, client):
        response = client.post('/api/export', {
            'data': [
                {'id': '1', 'platform': 'twitter', 'author': 'user', 'text': 'hello',
                 'timestamp': '2026-01-01', 'likes': 0, 'comments': 0, 'shares': 0, 'url': ''}
            ],
            'type': 'scraping',
            'filename': 'test_export.csv',
        }, format='json')
        assert response.status_code == 200
        assert response.get('Content-Type') == 'text/csv'


# ============================================================
# GET /api/exports
# ============================================================
class TestGetExports:
    def test_list_exports(self, client):
        response = client.get('/api/exports')
        assert response.status_code == 200
        assert response.data['success'] is True
        assert 'exports' in response.data


# ============================================================
# GET /api/scrape-history
# ============================================================
class TestScrapeHistory:
    @pytest.mark.django_db
    def test_get_history(self, client):
        response = client.get('/api/scrape-history')
        assert response.status_code == 200
        assert response.data['success'] is True
        assert 'history' in response.data

    @pytest.mark.django_db
    def test_history_pagination(self, client):
        response = client.get('/api/scrape-history?page=1')
        assert response.status_code == 200
        history = response.data['history']
        assert 'current_page' in history
        assert 'last_page' in history
        assert 'per_page' in history
        assert 'total' in history

    @pytest.mark.django_db
    def test_history_invalid_page(self, client):
        response = client.get('/api/scrape-history?page=abc')
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_history_negative_page(self, client):
        response = client.get('/api/scrape-history?page=-1')
        # Should be corrected to page 1
        assert response.status_code == 200


# ============================================================
# DELETE /api/scrape-history/<pk>
# ============================================================
class TestDeleteHistory:
    @pytest.mark.django_db
    def test_delete_nonexistent(self, client):
        response = client.delete('/api/scrape-history/99999')
        assert response.status_code == 404


# ============================================================
# GET /api/popular-searches
# ============================================================
class TestPopularSearches:
    @pytest.mark.django_db
    def test_get_popular(self, client):
        response = client.get('/api/popular-searches')
        assert response.status_code == 200
        assert response.data['success'] is True
        assert 'searches' in response.data

    @pytest.mark.django_db
    def test_popular_with_limit(self, client):
        response = client.get('/api/popular-searches?limit=5')
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_popular_limit_over_20(self, client):
        """Limit should be capped at 20."""
        response = client.get('/api/popular-searches?limit=100')
        assert response.status_code == 200


# ============================================================
# GET /api/cached-news
# ============================================================
class TestCachedNews:
    def test_get_cached_news(self, client):
        response = client.get('/api/cached-news')
        assert response.status_code == 200
        assert response.data['success'] is True
        assert 'general' in response.data
        assert 'trending' in response.data


# ============================================================
# POST /api/surf
# ============================================================
class TestSurfEndpoint:
    def test_missing_query(self, client):
        response = client.post('/api/surf', {}, format='json')
        assert response.status_code == 400
        assert 'query' in response.data['error'].lower()

    def test_query_too_long(self, client):
        response = client.post('/api/surf', {'query': 'x' * 501}, format='json')
        assert response.status_code == 400

    def test_valid_surf(self, client):
        response = client.post('/api/surf', {'query': 'python programming'}, format='json')
        assert response.status_code == 200
        assert response.data['success'] is True


# ============================================================
# POST /api/surf/quick
# ============================================================
class TestQuickSurfEndpoint:
    def test_missing_query(self, client):
        response = client.post('/api/surf/quick', {}, format='json')
        assert response.status_code == 400

    def test_valid_quick_surf(self, client):
        response = client.post('/api/surf/quick', {'query': 'django rest framework'}, format='json')
        assert response.status_code == 200
        assert response.data['success'] is True


# ============================================================
# POST /api/surf/deep
# ============================================================
class TestDeepSurfEndpoint:
    def test_missing_query(self, client):
        response = client.post('/api/surf/deep', {}, format='json')
        assert response.status_code == 400

    def test_valid_deep_surf(self, client):
        response = client.post('/api/surf/deep', {'query': 'machine learning', 'pages': 1}, format='json')
        assert response.status_code == 200


# ============================================================
# POST /api/surf/extract
# ============================================================
class TestExtractUrlEndpoint:
    def test_missing_url(self, client):
        response = client.post('/api/surf/extract', {}, format='json')
        assert response.status_code == 400
        assert 'url' in response.data['error'].lower()

    def test_ssrf_blocked(self, client):
        """SSRF protection should block internal URLs."""
        response = client.post('/api/surf/extract', {'url': 'http://localhost:8000'}, format='json')
        assert response.status_code == 200
        assert response.data.get('success') is False

    def test_ssrf_blocked_private_ip(self, client):
        """SSRF protection should block private IPs."""
        response = client.post('/api/surf/extract', {'url': 'http://192.168.1.1'}, format='json')
        assert response.status_code == 200
        assert response.data.get('success') is False


# ============================================================
# POST /api/surf/ai-analyze
# ============================================================
class TestAiAnalyzeEndpoint:
    def test_missing_query(self, client):
        response = client.post('/api/surf/ai-analyze', {
            'articles': [{'title': 'test'}],
        }, format='json')
        assert response.status_code == 400

    def test_missing_articles(self, client):
        response = client.post('/api/surf/ai-analyze', {
            'query': 'test',
        }, format='json')
        assert response.status_code == 400

    def test_empty_articles(self, client):
        response = client.post('/api/surf/ai-analyze', {
            'query': 'test',
            'articles': [],
        }, format='json')
        assert response.status_code == 400

    def test_too_many_articles(self, client):
        response = client.post('/api/surf/ai-analyze', {
            'query': 'test',
            'articles': [{'title': 't'}] * 51,
        }, format='json')
        assert response.status_code == 400


# ============================================================
# Root endpoint
# ============================================================
class TestRootEndpoint:
    def test_api_root(self, client):
        response = client.get('/')
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['status'] == 'ok'

    def test_robots_txt(self, client):
        response = client.get('/robots.txt')
        assert response.status_code == 200

    def test_sitemap_xml(self, client):
        response = client.get('/sitemap.xml')
        assert response.status_code == 200
