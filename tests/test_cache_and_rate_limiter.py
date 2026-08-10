"""
Unit tests for TTLCache and RateLimiter.
Tests caching behavior, TTL expiration, thread safety, rate limiting.
"""

import time
import threading
from scraper.services.cache_utils import TTLCache
from scraper.services.rate_limiter import RateLimiter


class TestTTLCache:
    """Test TTLCache behavior."""

    def test_set_and_get(self):
        cache = TTLCache(max_size=10, ttl=60)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_missing_key(self):
        cache = TTLCache(max_size=10, ttl=60)
        assert cache.get("nonexistent") is None

    def test_ttl_expiration(self):
        cache = TTLCache(max_size=10, ttl=0.1)  # 100ms TTL
        cache.set("key1", "value1")
        time.sleep(0.2)
        assert cache.get("key1") is None

    def test_max_size_eviction(self):
        cache = TTLCache(max_size=3, ttl=60)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        cache.set("d", 4)  # Should evict 'a'
        assert cache.get("a") is None
        assert cache.get("d") == 4

    def test_lru_ordering(self):
        cache = TTLCache(max_size=3, ttl=60)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        cache.get("a")  # Access 'a' to make it recently used
        cache.set("d", 4)  # Should evict 'b' (least recently used)
        assert cache.get("a") == 1
        assert cache.get("b") is None

    def test_update_existing_key(self):
        cache = TTLCache(max_size=10, ttl=60)
        cache.set("key1", "old")
        cache.set("key1", "new")
        assert cache.get("key1") == "new"

    def test_clear(self):
        cache = TTLCache(max_size=10, ttl=60)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert cache.size() == 0
        assert cache.get("a") is None

    def test_size(self):
        cache = TTLCache(max_size=10, ttl=60)
        assert cache.size() == 0
        cache.set("a", 1)
        assert cache.size() == 1
        cache.set("b", 2)
        assert cache.size() == 2

    def test_thread_safety(self):
        """Test concurrent access doesn't crash."""
        cache = TTLCache(max_size=100, ttl=60)
        errors = []

        def writer(start):
            try:
                for i in range(100):
                    cache.set(f"key-{start}-{i}", i)
            except Exception as e:
                errors.append(e)

        def reader():
            try:
                for _ in range(100):
                    cache.get("key-0-50")
            except Exception as e:
                errors.append(e)

        threads = []
        for i in range(5):
            threads.append(threading.Thread(target=writer, args=(i,)))
            threads.append(threading.Thread(target=reader))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Thread safety errors: {errors}"


class TestRateLimiter:
    """Test RateLimiter behavior."""

    def test_first_request_no_delay(self):
        limiter = RateLimiter(min_delay=0.1, max_delay=0.2)
        start = time.time()
        limiter.wait("example.com")
        elapsed = time.time() - start
        assert elapsed < 0.1  # First request should be instant

    def test_second_request_delayed(self):
        limiter = RateLimiter(min_delay=0.1, max_delay=0.2)
        limiter.wait("example.com")
        start = time.time()
        limiter.wait("example.com")
        elapsed = time.time() - start
        assert elapsed >= 0.05  # Should have some delay

    def test_different_domains_independent(self):
        limiter = RateLimiter(min_delay=0.5, max_delay=1.0)
        limiter.wait("domain1.com")
        start = time.time()
        limiter.wait("domain2.com")
        elapsed = time.time() - start
        assert elapsed < 0.1  # Different domain, no delay

    def test_url_extracted_to_domain(self):
        limiter = RateLimiter(min_delay=0.1, max_delay=0.2)
        limiter.wait("https://example.com/path1")
        start = time.time()
        limiter.wait("https://example.com/path2")
        elapsed = time.time() - start
        assert elapsed >= 0.05  # Same domain, should be delayed
