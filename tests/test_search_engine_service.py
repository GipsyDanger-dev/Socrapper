"""
Unit tests for SearchEngineService.search() fallback/backfill logic.
All network calls are stubbed so the tests run offline and fast.
"""

import pytest
from surfer.services.search_engine_service import SearchEngineService


@pytest.fixture
def service():
    return SearchEngineService()


def _item(i):
    return {
        "title": f"Title {i}",
        "url": f"https://example{i}.com/article",
        "snippet": "",
        "source": f"example{i}.com",
        "type": "web",
    }


class TestSearchBackfill:
    """Test that the requested limit is filled even on partial Google results."""

    def test_news_fills_full_quota(self, service, monkeypatch):
        """Google News should receive the full quota, not half."""
        captured = {}

        def fake_news(query, lim):
            captured["news_limit"] = lim
            return [_item(i) for i in range(lim)]

        monkeypatch.setattr(service, "_google_news_search", fake_news)
        monkeypatch.setattr(service, "_google_web_search", lambda q, lim, page=1: [])
        monkeypatch.setattr(service, "_bing_search", lambda q, lim: [])
        monkeypatch.setattr(service, "_duckduckgo_search", lambda q, lim: [])

        results = service.search("query", 15)

        assert captured["news_limit"] == 15  # was previously (15+1)//2 = 8
        assert len(results) == 15

    def test_bing_backfills_partial_results(self, service, monkeypatch):
        """Bing must run even when Google returned some (not zero) results."""
        monkeypatch.setattr(service, "_google_news_search", lambda q, lim: [_item(1)])
        monkeypatch.setattr(service, "_google_web_search", lambda q, lim, page=1: [])
        monkeypatch.setattr(service, "_bing_search", lambda q, lim: [_item(i) for i in range(2, 6)])
        monkeypatch.setattr(service, "_duckduckgo_search", lambda q, lim: [])

        results = service.search("query", 5)

        assert len(results) == 5  # 1 news + 4 bing

    def test_duckduckgo_backfills_remaining(self, service, monkeypatch):
        """DuckDuckGo should fill what Bing could not."""
        monkeypatch.setattr(service, "_google_news_search", lambda q, lim: [_item(1)])
        monkeypatch.setattr(service, "_google_web_search", lambda q, lim, page=1: [])
        monkeypatch.setattr(service, "_bing_search", lambda q, lim: [_item(2)])
        monkeypatch.setattr(service, "_duckduckgo_search", lambda q, lim: [_item(i) for i in range(3, 6)])

        results = service.search("query", 5)

        assert len(results) == 5  # 1 news + 1 bing + 3 ddg

    def test_deduplicates_by_url(self, service, monkeypatch):
        """Duplicate URLs across sources should be removed."""
        dup = _item(1)
        monkeypatch.setattr(service, "_google_news_search", lambda q, lim: [dict(dup)])
        monkeypatch.setattr(service, "_google_web_search", lambda q, lim, page=1: [])
        monkeypatch.setattr(service, "_bing_search", lambda q, lim: [dict(dup), _item(2)])
        monkeypatch.setattr(service, "_duckduckgo_search", lambda q, lim: [])

        results = service.search("query", 5)

        urls = [r["url"] for r in results]
        assert len(urls) == len(set(urls))  # no duplicates
        assert len(results) == 2

    def test_web_fills_remainder_before_fallback(self, service, monkeypatch):
        """If Google Web Search fills the quota, Bing/DDG must NOT be called."""
        called = {"bing": False, "ddg": False}

        def bing(q, lim):
            called["bing"] = True
            return []

        def ddg(q, lim):
            called["ddg"] = True
            return []

        monkeypatch.setattr(service, "_google_news_search", lambda q, lim: [_item(i) for i in range(1, 6)])
        monkeypatch.setattr(service, "_google_web_search", lambda q, lim, page=1: [_item(i) for i in range(6, 11)])
        monkeypatch.setattr(service, "_bing_search", bing)
        monkeypatch.setattr(service, "_duckduckgo_search", ddg)

        results = service.search("query", 10)

        assert len(results) == 10  # 5 news + 5 web, no overlap
        assert called["bing"] is False
        assert called["ddg"] is False

    def test_empty_everywhere_returns_empty(self, service, monkeypatch):
        monkeypatch.setattr(service, "_google_news_search", lambda q, lim: [])
        monkeypatch.setattr(service, "_google_web_search", lambda q, lim, page=1: [])
        monkeypatch.setattr(service, "_bing_search", lambda q, lim: [])
        monkeypatch.setattr(service, "_duckduckgo_search", lambda q, lim: [])

        results = service.search("query", 5)

        assert results == []
