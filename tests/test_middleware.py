"""
Unit tests for socrapper.middleware.RequestLoggingMiddleware.
"""

import logging

import pytest
from django.test import RequestFactory
from socrapper.middleware import RequestLoggingMiddleware


class FakeResponse:
    status_code = 200


class FakeView:
    """get_response callable returning a fake response."""

    def __init__(self):
        self.called = False

    def __call__(self, request):
        self.called = True
        return FakeResponse()


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def captured_logs():
    """Capture records emitted by the 'socrapper' logger.

    caplog hooks the root logger, but 'socrapper' is configured with
    propagate=False in settings, so we attach a handler directly.
    """
    logger = logging.getLogger("socrapper")
    records = []
    handler = logging.Handler()
    handler.emit = lambda record: records.append(record)
    logger.addHandler(handler)
    try:
        yield records
    finally:
        logger.removeHandler(handler)


def test_logs_request_line(request_factory, captured_logs):
    """The middleware logs method, path, status and duration."""
    view = FakeView()
    middleware = RequestLoggingMiddleware(view)

    request = request_factory.get("/api/platforms")
    response = middleware(request)

    assert response.status_code == 200
    assert view.called
    assert any("GET /api/platforms -> 200" in r.message for r in captured_logs)


def test_passes_through_post_request(request_factory, captured_logs):
    """POST requests pass through and are logged too."""
    middleware = RequestLoggingMiddleware(FakeView())
    request = request_factory.post("/api/scrape")

    response = middleware(request)

    assert response.status_code == 200
    assert any("POST /api/scrape -> 200" in r.message for r in captured_logs)


def test_logs_exceptions_as_500_and_reraised(request_factory, captured_logs):
    """A view exception is logged as 500 and re-raised (not swallowed)."""

    def exploding_view(request):
        raise RuntimeError("boom")

    middleware = RequestLoggingMiddleware(exploding_view)
    request = request_factory.get("/api/broken")

    with pytest.raises(RuntimeError, match="boom"):
        middleware(request)

    assert any("GET /api/broken -> 500" in r.message for r in captured_logs)
