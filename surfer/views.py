import json
import time
import logging
import threading
from collections import Counter

from django.conf import settings
from django.http import StreamingHttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services.internet_surfer_service import InternetSurferService
from .services.content_extractor_service import ContentExtractorService
from .services.llm_analysis_service import LLMAnalysisService
from .services.job_manager import job_manager
from scraper.views import track_search

logger = logging.getLogger(__name__)
surfer_service = InternetSurferService()
content_extractor = ContentExtractorService()
llm_service = LLMAnalysisService()


@api_view(["POST"])
def surf(request):
    query = request.data.get("query")
    if not query:
        return Response({"success": False, "error": "query is required"}, status=400)
    if len(query) > 500:
        return Response({"success": False, "error": "Query too long (max 500 chars)"}, status=400)

    # Track popular search
    track_search(query)

    search_limit = request.data.get("search_limit", 20)
    extract_content = request.data.get("extract_content", True)
    analyze_sentiment = request.data.get("analyze_sentiment", True)

    try:
        search_limit = int(search_limit)
        if search_limit < 1 or search_limit > 200:
            return Response({"success": False, "error": "search_limit must be 1-200"}, status=400)
    except (TypeError, ValueError):
        return Response({"success": False, "error": "search_limit must be a valid integer"}, status=400)

    results = surfer_service.surf(
        query,
        {
            "search_limit": search_limit,
            "extract_content": extract_content,
            "analyze_sentiment": analyze_sentiment,
        },
    )

    if not results.get("success"):
        return Response(results, status=500)

    return Response(results)


@api_view(["POST"])
def quick_surf(request):
    query = request.data.get("query")
    if not query:
        return Response({"success": False, "error": "query is required"}, status=400)
    if len(query) > 500:
        return Response({"success": False, "error": "Query too long (max 500 chars)"}, status=400)

    # Track popular search
    track_search(query)

    limit = request.data.get("limit", 15)
    try:
        limit = int(limit)
        if limit < 1 or limit > 200:
            limit = 15
    except (TypeError, ValueError):
        limit = 15

    results = surfer_service.quick_surf(query, limit)
    return Response(results)


@api_view(["POST"])
def deep_surf(request):
    query = request.data.get("query")
    if not query:
        return Response({"success": False, "error": "query is required"}, status=400)
    if len(query) > 500:
        return Response({"success": False, "error": "Query too long (max 500 chars)"}, status=400)

    pages = request.data.get("pages", 3)
    try:
        pages = int(pages)
        if pages < 1 or pages > 5:
            pages = 3
    except (TypeError, ValueError):
        pages = 3

    results = surfer_service.deep_surf(query, pages)
    return Response(results)


@api_view(["POST"])
def extract_url(request):
    url = request.data.get("url")
    if not url:
        return Response({"success": False, "error": "url is required"}, status=400)

    try:
        result = content_extractor.extract(url)
        return Response(result)
    except Exception as e:
        logger.error(f"Extract URL error: {e}")
        return Response({"success": False, "error": "An internal error occurred"}, status=500)


@api_view(["POST"])
def start_surf(request):
    """Start a surf job in the background; returns a job_id to stream from."""
    query = request.data.get("query")
    if not query:
        return Response({"success": False, "error": "query is required"}, status=400)
    if len(query) > 500:
        return Response({"success": False, "error": "Query too long (max 500 chars)"}, status=400)

    mode = request.data.get("mode", "full")
    search_limit = request.data.get("search_limit", 20)
    extract_content = request.data.get("extract_content", True)
    analyze_sentiment = request.data.get("analyze_sentiment", True)

    try:
        search_limit = int(search_limit)
        if search_limit < 1 or search_limit > 200:
            return Response({"success": False, "error": "search_limit must be 1-200"}, status=400)
    except (TypeError, ValueError):
        return Response({"success": False, "error": "search_limit must be a valid integer"}, status=400)

    try:
        limit = int(request.data.get("limit", 15))
        if limit < 1 or limit > 200:
            limit = 15
    except (TypeError, ValueError):
        limit = 15

    try:
        pages = int(request.data.get("pages", 3))
        if pages < 1 or pages > 5:
            pages = 3
    except (TypeError, ValueError):
        pages = 3

    track_search(query)

    job_id = job_manager.create("surf")
    emit = lambda stage, message, data=None: job_manager.emit(job_id, stage, message, data)  # noqa: E731

    def run():
        try:
            if mode == "quick":
                result = surfer_service.quick_surf(query, limit, progress_cb=emit)
            elif mode == "deep":
                result = surfer_service.deep_surf(query, pages, progress_cb=emit)
            else:
                result = surfer_service.surf(
                    query,
                    {
                        "search_limit": search_limit,
                        "extract_content": extract_content,
                        "analyze_sentiment": analyze_sentiment,
                    },
                    progress_cb=emit,
                )
            if result.get("success"):
                job_manager.finish(job_id, result)
            else:
                job_manager.fail(job_id, result.get("error", "Surf failed"))
        except Exception as e:
            logger.error(f"Surf job {job_id} crashed: {e}")
            job_manager.fail(job_id, str(e))

    threading.Thread(target=run, daemon=True).start()

    return Response({"success": True, "job_id": job_id, "status": "running"})


def surf_events(request, job_id):
    """Server-Sent Events stream of progress for a surf job."""

    def sse(payload, seq):
        return f"id: {seq}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"

    def event_stream():
        last_index = 0
        seq = 0
        elapsed = 0.0
        poll_interval = 0.5
        max_wait = 300.0

        while elapsed < max_wait:
            job = job_manager.get(job_id)
            if job is None:
                payload = {
                    "stage": "error",
                    "message": "Job tidak ditemukan",
                    "final": True,
                    "status": {"status": "error", "error": "Job not found"},
                }
                yield sse(payload, seq)
                return

            for event in job["events"][last_index:]:
                last_index += 1
                payload = dict(event)
                payload["final"] = False
                payload["status"] = None
                yield sse(payload, seq)
                seq += 1

            if job["status"] in ("done", "error"):
                payload = {
                    "stage": "done" if job["status"] == "done" else "error",
                    "message": "Selesai!" if job["status"] == "done" else (job["error"] or "Gagal"),
                    "final": True,
                    "status": {"status": job["status"], "result": job["result"], "error": job["error"]},
                }
                yield sse(payload, seq)
                return

            time.sleep(poll_interval)
            elapsed += poll_interval

        payload = {
            "stage": "error",
            "message": "Timeout",
            "final": True,
            "status": {"status": "error", "error": "timeout"},
        }
        yield sse(payload, seq)

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


@api_view(["GET"])
def surf_status(request, job_id):
    """JSON snapshot of a surf job (polling fallback for EventSource)."""
    job = job_manager.get(job_id)
    if job is None:
        return Response({"success": False, "status": "error", "error": "Job not found"}, status=404)
    return Response(
        {
            "success": True,
            "status": job["status"],
            "error": job["error"],
            "result": job["result"],
            "last_event": job["events"][-1] if job["events"] else None,
        }
    )


@api_view(["POST"])
def compare(request):
    """Compare sentiment across 2-4 keywords (search only, no extraction)."""
    queries = request.data.get("queries")
    if not queries or not isinstance(queries, list):
        return Response({"success": False, "error": "queries array is required"}, status=400)

    queries = [str(q).strip() for q in queries if str(q).strip()]
    if len(queries) < 2:
        return Response({"success": False, "error": "Minimal 2 keyword untuk dibandingkan"}, status=400)
    if len(queries) > 4:
        return Response({"success": False, "error": "Maksimal 4 keyword"}, status=400)

    comparisons = []
    for query in queries:
        item = {"query": query}
        try:
            quick = surfer_service.quick_surf(query, 15)
            results = quick.get("results", [])
            item["total"] = len(results)

            texts = [
                f"{r.get('title', '')}. {r.get('snippet', '')}" for r in results if r.get("title") or r.get("snippet")
            ]
            # Keyword-based analysis keeps compare fast & deterministic (no LLM
            # latency per keyword) and always returns the flat count format.
            sentiment = surfer_service.sentiment_service._analyze_with_keywords(texts) if texts else None
            counts = {
                "positive": sentiment.get("positive", 0) if sentiment else 0,
                "negative": sentiment.get("negative", 0) if sentiment else 0,
                "neutral": sentiment.get("neutral", 0) if sentiment else 0,
            }
            dominant = max(counts, key=counts.get) if any(counts.values()) else "neutral"
            item["sentiment"] = {**counts, "overall": dominant}

            sources = Counter(r.get("source", "") for r in results if r.get("source"))
            item["top_sources"] = [{"source": s, "count": c} for s, c in sources.most_common(5)]
            item["top_topics"] = surfer_service._extract_key_topics(results)
        except Exception as e:
            logger.warning(f"Compare '{query}' failed: {e}")
            item["total"] = 0
            item["sentiment"] = {"positive": 0, "negative": 0, "neutral": 0, "overall": "neutral"}
            item["top_sources"] = []
            item["top_topics"] = []
        comparisons.append(item)

    return Response({"success": True, "comparisons": comparisons})


@api_view(["POST"])
def ai_analyze(request):
    query = request.data.get("query")
    articles = request.data.get("articles")
    analysis_type = request.data.get("type", "general")

    if not query:
        return Response({"success": False, "error": "query is required"}, status=400)
    if len(query) > 500:
        return Response({"success": False, "error": "Query too long (max 500 chars)"}, status=400)
    if not articles or not isinstance(articles, list) or len(articles) < 1:
        return Response({"success": False, "error": "articles array is required"}, status=400)
    if len(articles) > 50:
        return Response({"success": False, "error": "Maximum 50 articles allowed"}, status=400)

    if not llm_service.is_configured():
        return Response(
            {
                "success": False,
                "error": "LLM not configured. Set LLM_API_KEY and LLM_BASE_URL in .env",
                "configured": False,
            }
        )

    try:
        if analysis_type == "market":
            result = llm_service.analyze_market(query, articles)
        else:
            result = llm_service.analyze_general(query, articles)

        # Report the model that actually produced the analysis. With a
        # fallback chain (LLM_MODEL="model-a,model-b"), the primary model may
        # have failed and last_model holds the one that succeeded.
        primary_model = llm_service.models[0] if llm_service.models else getattr(settings, "LLM_MODEL", "")
        model_used = llm_service.last_model or primary_model
        return Response(
            {
                "success": True,
                "ai_analysis": result,
                "type": analysis_type,
                "model": model_used,
            }
        )
    except Exception as e:
        logger.error(f"AI analyze error: {e}")
        return Response({"success": False, "error": "An internal error occurred"}, status=500)
