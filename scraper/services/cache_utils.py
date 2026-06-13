import time
import threading
import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)


class TTLCache:
    """Thread-safe cache with TTL (time-to-live) expiration."""

    def __init__(self, max_size=100, ttl=300):
        """
        Args:
            max_size: Maximum number of cached items
            ttl: Time-to-live in seconds (default: 5 minutes)
        """
        self._cache = OrderedDict()
        self._lock = threading.Lock()
        self._max_size = max_size
        self._ttl = ttl

    def get(self, key):
        """Get value from cache if exists and not expired."""
        with self._lock:
            if key not in self._cache:
                return None

            value, timestamp = self._cache[key]
            if time.time() - timestamp > self._ttl:
                # Expired
                del self._cache[key]
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            return value

    def set(self, key, value):
        """Store value in cache with current timestamp."""
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = (value, time.time())

            # Evict oldest if over max size
            while len(self._cache) > self._max_size:
                self._cache.popitem(last=False)

    def clear(self):
        """Clear all cached items."""
        with self._lock:
            self._cache.clear()

    def size(self):
        """Return current cache size."""
        with self._lock:
            return len(self._cache)


# Global search results cache (5 minute TTL)
search_cache = TTLCache(max_size=200, ttl=300)

# Global content extraction cache (10 minute TTL)
content_cache = TTLCache(max_size=500, ttl=600)
