"""
Custom middleware for Socrapper.
"""

import logging
import time

logger = logging.getLogger("socrapper")


class RequestLoggingMiddleware:
    """Log every HTTP request with method, path, status and duration.

    Helps debugging production issues (see BUG_REPORT.md recommendation #6):
    without any auth, a slow or erroring endpoint is otherwise invisible.
    Logs at INFO level through the 'socrapper' logger.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()
        try:
            response = self.get_response(request)
        except Exception:
            # Log unhandled 500s too — they are the most important to debug.
            duration_ms = (time.perf_counter() - start) * 1000
            logger.exception("%s %s -> 500 (%.0f ms)", request.method, request.get_full_path(), duration_ms)
            raise

        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s -> %s (%.0f ms)",
            request.method,
            request.get_full_path(),
            response.status_code,
            duration_ms,
        )
        return response
