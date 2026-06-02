import time
import random
import threading
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, min_delay=1.0, max_delay=3.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self._last_request = {}
        self._lock = threading.Lock()

    def _get_domain(self, url):
        try:
            return urlparse(url).hostname or url
        except Exception:
            return url

    def wait(self, url_or_domain):
        domain = self._get_domain(url_or_domain)
        with self._lock:
            now = time.time()
            last = self._last_request.get(domain, 0)
            elapsed = now - last
            delay = random.uniform(self.min_delay, self.max_delay)

            if elapsed < delay:
                sleep_time = delay - elapsed
                logger.debug(f"Rate limit: sleeping {sleep_time:.1f}s for {domain}")
                time.sleep(sleep_time)

            self._last_request[domain] = time.time()


_global_limiter = RateLimiter(min_delay=0.5, max_delay=2.0)


def throttle(url_or_domain):
    _global_limiter.wait(url_or_domain)
