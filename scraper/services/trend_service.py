"""Sentiment trend snapshots.

Records one row per scrape/surf (per keyword) and aggregates them by day so
the frontend can render a time-series sentiment chart.
"""

import logging
from collections import OrderedDict
from datetime import timedelta

from django.utils import timezone

from scraper.models import KeywordTrend

logger = logging.getLogger(__name__)


def normalize_counts(sentiment):
    """Extract {positive, negative, neutral, total} from either sentiment format.

    The keyword-based pipeline returns flat keys; the LLM pipeline returns the
    same counts nested under ``summary``.
    """
    if not sentiment:
        return {"positive": 0, "negative": 0, "neutral": 0, "total": 0}
    summary = sentiment.get("summary") or {}
    positive = sentiment.get("positive", summary.get("positive", 0)) or 0
    negative = sentiment.get("negative", summary.get("negative", 0)) or 0
    neutral = sentiment.get("neutral", summary.get("neutral", 0)) or 0
    return {
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "total": positive + negative + neutral,
    }


def record_snapshot(keyword, sentiment):
    """Persist a sentiment snapshot for a keyword (safe to call anywhere)."""
    if not keyword or not keyword.strip():
        return
    counts = normalize_counts(sentiment)
    if counts["total"] <= 0:
        return
    try:
        KeywordTrend.objects.create(keyword=keyword.strip().lower(), **counts)
    except Exception as e:
        logger.warning(f"Failed to record trend snapshot: {e}")


def _avg_positive_pct(points):
    total = sum(p["total"] for p in points)
    positive = sum(p["positive"] for p in points)
    return round(positive / total * 100, 1) if total else 0.0


def compute_summary(points):
    if not points:
        return {
            "total_results": 0,
            "avg_positive_pct": 0.0,
            "avg_negative_pct": 0.0,
            "trend": "no-data",
            "positive_delta": 0.0,
        }

    total = sum(p["total"] for p in points)
    positive = sum(p["positive"] for p in points)
    negative = sum(p["negative"] for p in points)
    avg_pos = round(positive / total * 100, 1) if total else 0.0
    avg_neg = round(negative / total * 100, 1) if total else 0.0

    # Direction: compare the positive % of the second half vs the first half.
    if len(points) >= 2:
        half = len(points) // 2
        first = points[:half]
        second = points[half:]
        first_pct = _avg_positive_pct(first)
        second_pct = _avg_positive_pct(second)
        delta = round(second_pct - first_pct, 1)
        if delta > 5.0:
            trend = "improving"
        elif delta < -5.0:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"
        delta = 0.0

    return {
        "total_results": total,
        "avg_positive_pct": avg_pos,
        "avg_negative_pct": avg_neg,
        "trend": trend,
        "positive_delta": delta,
    }


def get_trend(keyword, days=30):
    """Return daily sentiment points for a keyword within the last `days`."""
    keyword = keyword.strip().lower()
    since = timezone.now() - timedelta(days=days)

    from .trend_service import KeywordTrend  # local import to avoid cycles

    snapshots = KeywordTrend.objects.filter(keyword=keyword, created_at__gte=since).order_by("created_at")

    grouped = OrderedDict()
    for snapshot in snapshots:
        date_key = snapshot.created_at.date().isoformat()
        entry = grouped.setdefault(date_key, {"date": date_key, "positive": 0, "negative": 0, "neutral": 0, "total": 0})
        entry["positive"] += snapshot.positive
        entry["negative"] += snapshot.negative
        entry["neutral"] += snapshot.neutral
        entry["total"] += snapshot.total

    points = list(grouped.values())
    return {
        "keyword": keyword,
        "days": days,
        "total_snapshots": len(snapshots),
        "points": points,
        "summary": compute_summary(points),
    }
