"""Tests for the sentiment trend service (record_snapshot, get_trend) and
the GET /api/trend endpoint."""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from scraper.models import KeywordTrend
from scraper.services import trend_service


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
class TestRecordSnapshot:
    def test_records_flat_keyword_format(self):
        trend_service.record_snapshot("Harga BBM", {"positive": 2, "negative": 1, "neutral": 5})
        rows = KeywordTrend.objects.filter(keyword="harga bbm")
        assert rows.count() == 1
        assert rows[0].positive == 2
        assert rows[0].negative == 1
        assert rows[0].neutral == 5
        assert rows[0].total == 8

    def test_records_llm_summary_format(self):
        trend_service.record_snapshot("pertamax", {"summary": {"positive": 3, "negative": 0, "neutral": 7}})
        row = KeywordTrend.objects.get(keyword="pertamax")
        assert row.positive == 3
        assert row.total == 10

    def test_skips_zero_total(self):
        trend_service.record_snapshot("empty", {"positive": 0, "negative": 0, "neutral": 0})
        assert KeywordTrend.objects.filter(keyword="empty").count() == 0

    def test_skips_none_and_blank(self):
        trend_service.record_snapshot("x", None)
        trend_service.record_snapshot("", {"positive": 1, "negative": 0, "neutral": 0})
        assert KeywordTrend.objects.count() == 0


def create_with_created_at(keyword, positive, negative, neutral, total, when):
    """Create a snapshot, then backdate it (auto_now_add overrides create() values)."""
    row = KeywordTrend.objects.create(
        keyword=keyword, positive=positive, negative=negative, neutral=neutral, total=total
    )
    KeywordTrend.objects.filter(pk=row.pk).update(created_at=when)
    return row


@pytest.mark.django_db
class TestGetTrend:
    def test_groups_snapshots_by_day(self):
        today = timezone.now().date()
        KeywordTrend.objects.create(keyword="k", positive=2, negative=0, neutral=1, total=3)
        KeywordTrend.objects.create(keyword="k", positive=4, negative=1, neutral=0, total=5)

        result = trend_service.get_trend("k", days=30)
        assert result["total_snapshots"] == 2
        assert len(result["points"]) == 1  # same day grouped into one point
        point = result["points"][0]
        assert point["date"] == today.isoformat()
        assert point["positive"] == 6
        assert point["total"] == 8

    def test_ignores_snapshots_outside_window(self):
        create_with_created_at("old", 1, 0, 0, 1, timezone.now() - timedelta(days=400))
        result = trend_service.get_trend("old", days=30)
        assert result["total_snapshots"] == 0
        assert result["points"] == []
        assert result["summary"]["trend"] == "no-data"

    def test_improving_trend(self):
        today = timezone.now()
        create_with_created_at("k", 1, 9, 0, 10, today - timedelta(days=1))
        create_with_created_at("k", 9, 1, 0, 10, today)

        result = trend_service.get_trend("k", days=30)
        assert result["summary"]["trend"] == "improving"
        assert result["summary"]["positive_delta"] > 0

    def test_declining_trend(self):
        today = timezone.now()
        create_with_created_at("k", 9, 1, 0, 10, today - timedelta(days=1))
        create_with_created_at("k", 1, 9, 0, 10, today)

        result = trend_service.get_trend("k", days=30)
        assert result["summary"]["trend"] == "declining"
        assert result["summary"]["positive_delta"] < 0

    def test_stable_trend(self):
        today = timezone.now()
        KeywordTrend.objects.create(
            keyword="k", positive=5, negative=5, neutral=0, total=10, created_at=today - timedelta(days=1)
        )
        KeywordTrend.objects.create(keyword="k", positive=5, negative=5, neutral=0, total=10, created_at=today)

        result = trend_service.get_trend("k", days=30)
        assert result["summary"]["trend"] == "stable"


class TestTrendEndpoint:
    def test_missing_keyword(self, client):
        response = client.get("/api/trend")
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_returns_trend(self, client):
        KeywordTrend.objects.create(keyword="k", positive=2, negative=1, neutral=3, total=6)
        response = client.get("/api/trend?keyword=k&days=30")
        assert response.status_code == 200
        assert response.data["success"] is True
        assert response.data["keyword"] == "k"
        assert response.data["total_snapshots"] == 1
        assert response.data["points"][0]["positive"] == 2
        assert response.data["summary"]["trend"] in ("improving", "declining", "stable")

    @pytest.mark.django_db
    def test_out_of_range_days_defaults_to_30(self, client):
        KeywordTrend.objects.create(keyword="k", positive=1, negative=0, neutral=0, total=1)
        response = client.get("/api/trend?keyword=k&days=99999")
        assert response.status_code == 200
        assert response.data["days"] == 30
