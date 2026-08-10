import logging
import os
from django.http import FileResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.db.models import F
from .models import ScrapeHistory, PopularSearch
from .services.sentiment_service import SentimentService
from .services.csv_export_service import CsvExportService
from .services.web_scraper_service import WebScraperService

logger = logging.getLogger(__name__)
sentiment_service = SentimentService()
web_scraper_service = WebScraperService()

VALID_PLATFORMS = ["twitter", "instagram", "tiktok", "facebook", "reddit", "youtube", "news", "stackoverflow", "github"]


@api_view(["POST"])
def scrape(request):
    platform = request.data.get("platform")
    keyword = request.data.get("keyword")
    limit = request.data.get("limit")
    method = request.data.get("method", "webscrape")

    if not platform or platform not in VALID_PLATFORMS:
        return Response({"success": False, "error": "Invalid platform"}, status=400)
    if not keyword:
        return Response({"success": False, "error": "Keyword is required"}, status=400)
    if len(keyword) > 500:
        return Response({"success": False, "error": "Keyword too long (max 500 chars)"}, status=400)

    # Track popular search
    track_search(keyword)
    try:
        limit = int(limit)
        if limit < 1 or limit > 1000:
            raise ValueError
    except (TypeError, ValueError):
        return Response({"success": False, "error": "Limit must be 1-1000"}, status=400)

    try:
        results = web_scraper_service.scrape(keyword, platform, limit)

        analysis = None

        # Sentiment analysis — separate from history saving
        try:
            sentiment_result = sentiment_service.analyze_sentiments([r.get("text", "") for r in results])

            # Handle both LLM and keyword-based response formats
            if "summary" in sentiment_result:
                summary = sentiment_result["summary"]
                pos = summary.get("positive", 0)
                neg = summary.get("negative", 0)
                neu = summary.get("neutral", 0)
                pct = summary.get("percentage", {})
            else:
                pos = sentiment_result.get("positive", 0)
                neg = sentiment_result.get("negative", 0)
                neu = sentiment_result.get("neutral", 0)
                pct = sentiment_result.get("percentage", {})

            # Merge sentiment details into each result item
            details = sentiment_result.get("results") or sentiment_result.get("details") or []
            for i, item in enumerate(results):
                if i < len(details):
                    item["sentiment"] = details[i].get("sentiment", "neutral")
                    item["sentiment_score"] = details[i].get("confidence", 0)
                    item["sentiment_reason"] = details[i].get("reason", "")
                else:
                    item["sentiment"] = "neutral"
                    item["sentiment_score"] = 0
                    item["sentiment_reason"] = ""

            analysis = sentiment_result
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")

        # Save history — separate from sentiment analysis
        try:
            pos = analysis.get("summary", {}).get("positive", 0) if analysis else 0
            neg = analysis.get("summary", {}).get("negative", 0) if analysis else 0
            neu = analysis.get("summary", {}).get("neutral", 0) if analysis else 0
            pct = analysis.get("summary", {}).get("percentage", {}) if analysis else {}

            ScrapeHistory.objects.create(
                platform=platform,
                keyword=keyword,
                limit=limit,
                results_count=len(results),
                sentiment_summary={
                    "positive": pos,
                    "negative": neg,
                    "neutral": neu,
                    "percentage": pct,
                },
                raw_data=results,
            )
        except Exception as e:
            logger.warning(f"Failed to save history: {e}")

        return Response(
            {
                "success": True,
                "data": results,
                "total": len(results),
                "platform": platform,
                "keyword": keyword,
                "method": method,
                "analysis": analysis,
            }
        )
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        return Response({"success": False, "error": "An internal error occurred"}, status=500)


@api_view(["POST"])
def analyze(request):
    texts = request.data.get("texts")
    if not texts or not isinstance(texts, list) or len(texts) < 1:
        return Response({"success": False, "error": "texts array is required"}, status=400)
    if len(texts) > 100:
        return Response({"success": False, "error": "Maximum 100 texts allowed"}, status=400)

    try:
        analysis = sentiment_service.analyze_sentiments(texts)
        return Response({"success": True, "analysis": analysis})
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        return Response({"success": False, "error": "An internal error occurred"}, status=500)


@api_view(["GET"])
def get_platforms(request):
    return Response(
        {
            "platforms": {
                "twitter": "Twitter/X",
                "reddit": "Reddit",
                "news": "Google News",
                "stackoverflow": "Stack Overflow",
                "github": "GitHub",
                "youtube": "YouTube",
                "instagram": "Instagram",
                "tiktok": "TikTok",
                "facebook": "Facebook",
            }
        }
    )


@api_view(["POST"])
def export_data(request):
    data = request.data.get("data")
    export_type = request.data.get("type")
    filename = request.data.get("filename")

    if not data:
        return Response({"success": False, "error": "data is required"}, status=400)
    if export_type not in ["scraping", "analysis", "statistics"]:
        return Response({"success": False, "error": "Invalid export type"}, status=400)

    try:
        if export_type == "scraping":
            filepath = CsvExportService.export_scraping_data(data, filename)
        elif export_type == "analysis":
            filepath = CsvExportService.export_analysis(
                data.get("data", []),
                data.get("analysis", {}),
                filename,
            )
        else:
            filepath = CsvExportService.export_statistics(data, filename)

        return FileResponse(
            open(filepath, "rb"),
            content_type="text/csv",
            as_attachment=True,
            filename=os.path.basename(filepath),
        )
    except Exception as e:
        logger.error(f"Export error: {e}")
        return Response({"success": False, "error": "An internal error occurred"}, status=500)


@api_view(["GET"])
def get_exports(request):
    try:
        exports = CsvExportService.list_exports()
        return Response({"success": True, "exports": exports})
    except Exception as e:
        logger.error(f"List exports error: {e}")
        return Response({"success": False, "error": "An internal error occurred"}, status=500)


@api_view(["GET"])
def download_export(request, filename):
    try:
        filepath = CsvExportService.get_filepath(filename)
        return FileResponse(
            open(filepath, "rb"),
            content_type="text/csv",
            as_attachment=True,
            filename=filename,
        )
    except FileNotFoundError:
        return Response({"success": False, "error": "File not found"}, status=404)
    except Exception as e:
        logger.error(f"Download export error: {e}")
        return Response({"success": False, "error": "An internal error occurred"}, status=500)


@api_view(["DELETE"])
def delete_export(request, filename):
    try:
        success = CsvExportService.delete_file(filename)
        if not success:
            return Response({"success": False, "error": "File not found"}, status=404)
        return Response({"success": True, "message": "Export file deleted"})
    except Exception as e:
        logger.error(f"Delete export error: {e}")
        return Response({"success": False, "error": "An internal error occurred"}, status=500)


@api_view(["GET"])
def get_history(request):
    try:
        page = int(request.query_params.get("page", 1))
        if page < 1:
            page = 1
    except (TypeError, ValueError):
        return Response({"success": False, "error": "page must be a positive integer"}, status=400)
    per_page = 15

    history_qs = ScrapeHistory.objects.all()
    total = history_qs.count()
    start = (page - 1) * per_page
    end = start + per_page
    items = history_qs[start:end]

    data = []
    for item in items:
        data.append(
            {
                "id": item.id,
                "platform": item.platform,
                "keyword": item.keyword,
                "limit": item.limit,
                "results_count": item.results_count,
                "sentiment_summary": item.sentiment_summary,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
            }
        )

    last_page = max(1, -(-total // per_page))

    return Response(
        {
            "success": True,
            "history": {
                "data": data,
                "current_page": page,
                "last_page": last_page,
                "per_page": per_page,
                "total": total,
            },
        }
    )


@api_view(["DELETE"])
def delete_history(request, pk):
    try:
        item = ScrapeHistory.objects.get(pk=pk)
        item.delete()
        return Response({"success": True, "message": "History deleted"})
    except ScrapeHistory.DoesNotExist:
        return Response({"success": False, "error": "Not found"}, status=404)


def track_search(keyword):
    """Track a search keyword for popular searches.

    Uses atomic F() expression to avoid race conditions under concurrent requests.
    get_or_create handles the first occurrence; F('count') + 1 handles increments
    without read-modify-write races.
    """
    if not keyword or len(keyword.strip()) < 2:
        return
    keyword = keyword.strip().lower()
    try:
        obj, created = PopularSearch.objects.get_or_create(keyword=keyword)
        if not created:
            # Atomic increment — no race condition even under concurrent requests
            PopularSearch.objects.filter(pk=obj.pk).update(count=F("count") + 1)
    except Exception as e:
        logger.warning(f"Failed to track search: {e}")


@api_view(["GET"])
def get_popular_searches(request):
    """Return top 10 popular search keywords."""
    try:
        limit = int(request.query_params.get("limit", 10))
        limit = min(limit, 20)
    except (TypeError, ValueError):
        limit = 10

    try:
        popular = PopularSearch.objects.order_by("-count", "-last_searched")[:limit]
        data = [{"keyword": p.keyword, "count": p.count} for p in popular]
        return Response({"success": True, "searches": data})
    except Exception as e:
        logger.error(f"Get popular searches error: {e}")
        return Response({"success": False, "error": "An internal error occurred"}, status=500)


@api_view(["GET"])
def get_cached_news(request):
    """Return pre-cached news for instant loading."""
    try:
        from .services.news_cache_service import news_cache

        return Response(
            {
                "success": True,
                "general": news_cache.get_general(),
                "trending": news_cache.get_trending(),
                "last_update": news_cache.get_last_update(),
            }
        )
    except Exception as e:
        logger.error(f"Get cached news error: {e}")
        return Response({"success": False, "error": "An internal error occurred"}, status=500)
