import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

from .services.internet_surfer_service import InternetSurferService
from .services.content_extractor_service import ContentExtractorService
from .services.llm_analysis_service import LLMAnalysisService
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
        if search_limit < 1 or search_limit > 100:
            return Response({"success": False, "error": "search_limit must be 1-100"}, status=400)
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
        if limit < 1 or limit > 50:
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
