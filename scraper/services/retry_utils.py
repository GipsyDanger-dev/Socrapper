import time
import random
import logging
from functools import wraps

logger = logging.getLogger(__name__)

# HTTP status codes that should trigger a retry
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class RetryableHTTPError(Exception):
    """Exception for HTTP responses that should be retried."""

    def __init__(self, status_code, response=None):
        self.status_code = status_code
        self.response = response
        super().__init__(f"HTTP {status_code}")


def retry(
    max_attempts=3, base_delay=1.0, max_delay=30.0, exceptions=(Exception,), retry_on_status=False, status_codes=None
):
    """
    Retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds between retries
        max_delay: Maximum delay in seconds
        exceptions: Tuple of exception types to catch
        retry_on_status: If True, check response.status_code for retryable codes
        status_codes: Set of HTTP status codes to retry on (default: RETRYABLE_STATUS_CODES)
    """
    retryable = status_codes or RETRYABLE_STATUS_CODES

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    result = func(*args, **kwargs)

                    # Check HTTP status if enabled
                    if retry_on_status and hasattr(result, "status_code"):
                        if result.status_code in retryable:
                            # Check for Retry-After header
                            retry_after = result.headers.get("Retry-After")
                            if retry_after:
                                try:
                                    delay = float(retry_after)
                                except ValueError:
                                    delay = min(base_delay * (2**attempt), max_delay)
                            else:
                                delay = min(base_delay * (2**attempt), max_delay)
                                delay *= random.uniform(0.8, 1.2)

                            if attempt < max_attempts - 1:
                                logger.warning(
                                    f"Retry {attempt + 1}/{max_attempts} for {func.__name__}: "
                                    f"HTTP {result.status_code}. Waiting {delay:.1f}s"
                                )
                                time.sleep(delay)
                                continue
                            else:
                                logger.error(
                                    f"All {max_attempts} attempts failed for {func.__name__}: HTTP {result.status_code}"
                                )
                                return result

                    return result

                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        delay = min(base_delay * (2**attempt), max_delay)
                        delay *= random.uniform(0.8, 1.2)
                        logger.warning(
                            f"Retry {attempt + 1}/{max_attempts} for {func.__name__}: {e}. Waiting {delay:.1f}s"
                        )
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}: {e}")
            raise last_exception

        return wrapper

    return decorator
