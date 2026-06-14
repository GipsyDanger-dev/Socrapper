"""
Pytest configuration and fixtures for Socrapper test suite.
"""
import os

# Set test environment before Django loads
os.environ['DB_ENGINE'] = 'sqlite'
os.environ['SECRET_KEY'] = 'test-secret-key-not-for-production'
os.environ['ALLOWED_HOSTS'] = 'localhost,127.0.0.1,testserver'

import django
from django.conf import settings

# Configure Django before importing models
django.setup()

# Add testserver to ALLOWED_HOSTS for DRF test client
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

import pytest
from rest_framework.test import APIClient
from scraper.models import ScrapeHistory, PopularSearch


@pytest.fixture
def api_client():
    """DRF API client for testing endpoints."""
    return APIClient()


@pytest.fixture
def sample_scrape_history(db):
    """Create sample scrape history records."""
    items = []
    for i in range(5):
        item = ScrapeHistory.objects.create(
            platform='twitter',
            keyword=f'test_keyword_{i}',
            limit=10,
            results_count=8,
            sentiment_summary={
                'positive': 3,
                'negative': 2,
                'neutral': 3,
                'percentage': {'positive': 37.5, 'negative': 25.0, 'neutral': 37.5},
            },
            raw_data=[
                {'id': f'test-{i}', 'text': f'Sample text {i}', 'platform': 'twitter', 'author': f'user{i}'}
            ],
        )
        items.append(item)
    return items


@pytest.fixture
def sample_popular_searches(db):
    """Create sample popular search records."""
    searches = []
    for keyword, count in [('python', 100), ('django', 50), ('react', 30)]:
        s = PopularSearch.objects.create(keyword=keyword, count=count)
        searches.append(s)
    return searches


@pytest.fixture
def mock_scrape_results():
    """Sample scrape results for testing."""
    return [
        {
            'id': 'test-001',
            'platform': 'twitter',
            'author': '@testuser',
            'text': 'This is an amazing product!',
            'timestamp': '2026-06-14T10:00:00',
            'likes': 42,
            'comments': 5,
            'shares': 10,
            'url': 'https://twitter.com/test/123',
        },
        {
            'id': 'test-002',
            'platform': 'twitter',
            'author': '@anotheruser',
            'text': 'This is terrible, very disappointed.',
            'timestamp': '2026-06-14T11:00:00',
            'likes': 5,
            'comments': 20,
            'shares': 1,
            'url': 'https://twitter.com/test/456',
        },
        {
            'id': 'test-003',
            'platform': 'twitter',
            'author': '@neutraluser',
            'text': 'The weather today is okay.',
            'timestamp': '2026-06-14T12:00:00',
            'likes': 1,
            'comments': 0,
            'shares': 0,
            'url': 'https://twitter.com/test/789',
        },
    ]
