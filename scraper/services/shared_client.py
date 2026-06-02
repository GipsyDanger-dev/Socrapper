import httpx
import logging

logger = logging.getLogger(__name__)

_client = None

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}


def get_client():
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.Client(
            timeout=30,
            follow_redirects=True,
            cookies=httpx.Cookies(),
            limits=httpx.Limits(
                max_connections=15,
                max_keepalive_connections=10,
                keepalive_expiry=30,
            ),
            http2=True,
        )
    return _client


def close_client():
    global _client
    if _client and not _client.is_closed:
        try:
            _client.close()
        except Exception:
            pass
    _client = None


def fetch(url, headers=None, timeout=None):
    client = get_client()
    merged_headers = {**HEADERS, **(headers or {})}
    kwargs = {'headers': merged_headers}
    if timeout:
        kwargs['timeout'] = timeout
    return client.get(url, **kwargs)
