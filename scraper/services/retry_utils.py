import time
import random
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def retry(max_attempts=3, base_delay=1.0, max_delay=30.0, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        delay *= random.uniform(0.8, 1.2)
                        logger.warning(f"Retry {attempt + 1}/{max_attempts} for {func.__name__}: {e}. Waiting {delay:.1f}s")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}: {e}")
            raise last_exception
        return wrapper
    return decorator
