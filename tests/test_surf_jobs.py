"""
Tests for the background surf job endpoints (start/status/events) and the
keyword comparison endpoint.

The surf service is monkeypatched so no real network requests happen.
"""

import time

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def client():
    return APIClient()


def fake_surf(query, options=None, progress_cb=None):
    if progress_cb:
        progress_cb("collecting", "searching...")
        progress_cb("extracting", "extracting 2 articles...")
        progress_cb("analyzing", "1 positive, 1 negative")
        progress_cb("done", "done!")
    return {
        "success": True,
        "query": query,
        "total_results": 2,
        "merged_results": [{"title": "result-a"}, {"title": "result-b"}],
        "summary": {},
    }


def wait_for_status(client, job_id, timeout=5):
    deadline = time.time() + timeout
    resp = None
    while time.time() < deadline:
        resp = client.get(f"/api/surf/status/{job_id}")
        if resp.status_code == 200 and resp.data["status"] in ("done", "error"):
            return resp
        time.sleep(0.1)
    return resp


class TestStartSurf:
    def test_missing_query(self, client):
        response = client.post("/api/surf/start", {}, format="json")
        assert response.status_code == 400

    def test_query_too_long(self, client):
        response = client.post("/api/surf/start", {"query": "x" * 501}, format="json")
        assert response.status_code == 400

    def test_invalid_limit(self, client):
        # Cap was raised 100 -> 200; 201 is now the first invalid value
        response = client.post("/api/surf/start", {"query": "test", "search_limit": 201}, format="json")
        assert response.status_code == 400

    def test_start_returns_job_and_completes(self, client, monkeypatch):
        import surfer.views as views

        monkeypatch.setattr(views.surfer_service, "surf", fake_surf)
        response = client.post(
            "/api/surf/start",
            {"query": "python django", "search_limit": 5, "extract_content": False, "analyze_sentiment": True},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["success"] is True
        job_id = response.data["job_id"]
        assert job_id

        status_resp = wait_for_status(client, job_id)
        assert status_resp is not None
        assert status_resp.data["status"] == "done"
        assert status_resp.data["result"]["total_results"] == 2
        assert status_resp.data["last_event"]["stage"] == "done"


class TestStartSurfModes:
    def test_quick_mode_routes_to_quick_surf(self, client, monkeypatch):
        import surfer.views as views

        calls = {}

        def fake_quick(query, limit=15, progress_cb=None):
            calls["limit"] = limit
            if progress_cb:
                progress_cb("collecting", "quick search...")
                progress_cb("done", "done!")
            return {"success": True, "query": query, "results": [], "total": 0}

        monkeypatch.setattr(views.surfer_service, "quick_surf", fake_quick)
        response = client.post("/api/surf/start", {"query": "x", "mode": "quick", "limit": 7}, format="json")
        assert response.status_code == 200
        status_resp = wait_for_status(client, response.data["job_id"])
        assert status_resp.data["status"] == "done"
        assert calls.get("limit") == 7

    def test_deep_mode_routes_to_deep_surf(self, client, monkeypatch):
        import surfer.views as views

        calls = {}

        def fake_deep(query, pages=3, progress_cb=None):
            calls["pages"] = pages
            if progress_cb:
                progress_cb("collecting", "deep...")
                progress_cb("done", "done!")
            return {"success": True, "query": query, "total_results": 0, "results": []}

        monkeypatch.setattr(views.surfer_service, "deep_surf", fake_deep)
        response = client.post("/api/surf/start", {"query": "x", "mode": "deep", "pages": 2}, format="json")
        assert response.status_code == 200
        status_resp = wait_for_status(client, response.data["job_id"])
        assert status_resp.data["status"] == "done"
        assert calls.get("pages") == 2

    def test_default_mode_routes_to_surf(self, client, monkeypatch):
        import surfer.views as views

        monkeypatch.setattr(views.surfer_service, "surf", fake_surf)
        response = client.post("/api/surf/start", {"query": "x"}, format="json")
        assert response.status_code == 200
        status_resp = wait_for_status(client, response.data["job_id"])
        assert status_resp.data["status"] == "done"
        assert status_resp.data["result"]["total_results"] == 2


class TestSurfEvents:
    def test_events_stream_final_event(self, client, monkeypatch):
        import surfer.views as views

        monkeypatch.setattr(views.surfer_service, "surf", fake_surf)
        response = client.post("/api/surf/start", {"query": "ai 2026"}, format="json")
        job_id = response.data["job_id"]
        wait_for_status(client, job_id)

        stream = client.get(f"/api/surf/events/{job_id}")
        assert stream.status_code == 200
        assert "text/event-stream" in stream["Content-Type"]

        body = b"".join(stream.streaming_content).decode("utf-8")
        # SSE frames: id + data per event
        assert "data:" in body
        assert "collecting" in body
        # Final frame carries the done status
        assert "done" in body
        assert '"final": true' in body

    def test_events_unknown_job(self, client):
        stream = client.get("/api/surf/events/does-not-exist")
        assert stream.status_code == 200
        body = b"".join(stream.streaming_content).decode("utf-8")
        assert "Job not found" in body


class TestSurfStatus:
    def test_status_not_found(self, client):
        response = client.get("/api/surf/status/nope")
        assert response.status_code == 404


class TestCompare:
    def test_missing_queries(self, client):
        response = client.post("/api/surf/compare", {}, format="json")
        assert response.status_code == 400

    def test_less_than_two_queries(self, client):
        response = client.post("/api/surf/compare", {"queries": ["only-one"]}, format="json")
        assert response.status_code == 400

    def test_more_than_four_queries(self, client):
        response = client.post(
            "/api/surf/compare",
            {"queries": ["a", "b", "c", "d", "e"]},
            format="json",
        )
        assert response.status_code == 400

    def test_compare_returns_per_keyword_stats(self, client, monkeypatch):
        import surfer.views as views

        def fake_quick(query, limit=15):
            return {
                "success": True,
                "results": [
                    {"title": "Amazing growth for X", "snippet": "great news everyone loves it", "source": "detik.com"},
                    {"title": "Terrible decline for Y", "snippet": "bad awful horrible news", "source": "kompas.com"},
                ],
            }

        def fake_sentiment(texts):
            return {"positive": 1, "negative": 1, "neutral": 0, "results": []}

        monkeypatch.setattr(views.surfer_service, "quick_surf", fake_quick)
        monkeypatch.setattr(views.surfer_service.sentiment_service, "_analyze_with_keywords", fake_sentiment)

        response = client.post("/api/surf/compare", {"queries": ["keyword-a", "keyword-b"]}, format="json")
        assert response.status_code == 200
        assert response.data["success"] is True
        comparisons = response.data["comparisons"]
        assert len(comparisons) == 2

        for item in comparisons:
            assert item["query"]
            assert item["total"] == 2
            assert item["sentiment"]["positive"] == 1
            assert item["sentiment"]["negative"] == 1
            assert item["sentiment"]["overall"] in ("positive", "negative", "neutral")
            assert "top_sources" in item
            assert "top_topics" in item
