import time
import random
import threading
import logging
from urllib.parse import urlparse
from collections import OrderedDict

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, min_delay=1.0, max_delay=3.0, max_domains=1000):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self._last_request = OrderedDict()
        self._lock = threading.Lock()
        self._max_domains = max_domains

    def _get_domain(self, url):
        try:
            return urlparse(url).hostname or url
        except Exception:
            return url

    def _cleanup_old_domains(self):
        """Remove domains not accessed in last 10 minutes."""
        cutoff = time.time() - 600
        to_remove = [d for d, t in self._last_request.items() if t < cutoff]
        for d in to_remove:
            del self._last_request[d]
        # Also enforce max domains
        while len(self._last_request) > self._max_domains:
            self._last_request.popitem(last=False)

    def wait(self, url_or_domain):
        domain = self._get_domain(url_or_domain)
        sleep_time = 0

        with self._lock:
            now = time.time()
            last = self._last_request.get(domain, 0)
            elapsed = now - last
            delay = random.uniform(self.min_delay, self.max_delay)

            if elapsed < delay:
                sleep_time = delay - elapsed

            self._last_request[domain] = now

            # Periodic cleanup
            if len(self._last_request) > 100:
                self._cleanup_old_domains()

        # Sleep OUTSIDE the lock so other threads can check their domains
        if sleep_time > 0:
            logger.debug(f"Rate limit: sleeping {sleep_time:.1f}s for {domain}")
            time.sleep(sleep_time)


_global_limiter = RateLimiter(min_delay=0.5, max_delay=2.0)


def throttle(url_or_domain):
    _global_limiter.wait(url_or_domain)
