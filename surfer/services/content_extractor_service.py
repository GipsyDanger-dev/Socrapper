import re
import logging
import ipaddress
import socket
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

NOISE_SELECTORS = [
    'script', 'style', 'nav', 'footer', 'header',
    '.sidebar', '.advertisement', '.ad', '.ads',
    '.cookie-banner', '.popup', '.modal',
    '.social-share', '.related-posts', '.comments',
    '#sidebar', '#footer', '#header', '#nav',
    '.widget', '.newsletter', '.subscription',
]


class ContentExtractorService:
    @staticmethod
    def _is_safe_url(url):
        """Block internal/private IPs to prevent SSRF."""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ('http', 'https'):
                return False
            hostname = parsed.hostname
            if not hostname:
                return False
            # Block localhost
            if hostname in ('localhost', '127.0.0.1', '::1', '0.0.0.0'):
                return False
            # Resolve and check IP
            try:
                addr = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC)
                for family, _, _, _, sockaddr in addr:
                    ip = ipaddress.ip_address(sockaddr[0])
                    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                        return False
            except (socket.gaierror, ValueError):
                pass
            # Block cloud metadata
            if '169.254.169.254' in hostname or 'metadata.google' in hostname:
                return False
            return True
        except Exception:
            return False

    def extract(self, url):
        if not self._is_safe_url(url):
            return self._error_result(url, 'URL not allowed')
        try:
            from scraper.services.shared_client import fetch
            from scraper.services.rate_limiter import throttle
            throttle(url)
            response = fetch(url)

            if response.status_code != 200:
                return self._error_result(url, f"HTTP {response.status_code}")

            return self._parse_content(response.text, url)
        except Exception as e:
            logger.error(f"Content extraction error for {url}: {e}")
            return self._error_result(url, str(e))

    def extract_multiple(self, urls, max_workers=5):
        results = [None] * len(urls)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {executor.submit(self.extract, url): i for i, url in enumerate(urls)}
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    results[idx] = self._error_result(urls[idx], str(e))

        return results

    def _parse_content(self, html, url):
        try:
            from lxml import html as lxml_html
            doc = lxml_html.fromstring(html)
        except Exception:
            return self._error_result(url, "Failed to parse HTML")

        # Remove noise elements before extraction
        self._remove_noise(doc)

        title = self._extract_title(doc, html)
        description = self._extract_meta_description(doc, html)
        author = self._extract_author(doc, html)
        publish_date = self._extract_date(doc, html)
        site_name = self._extract_site_name(doc, html, url)
        main_content = self._extract_main_content(doc, html)
        images = self._extract_images(doc, html, url)
        word_count = len(main_content.split()) if main_content else 0

        return {
            'url': url,
            'title': title,
            'description': description,
            'author': author,
            'publish_date': publish_date,
            'site_name': site_name,
            'content': main_content,
            'word_count': word_count,
            'images': images,
            'success': True,
        }

    def _remove_noise(self, doc):
        """Remove noise elements (ads, nav, footer, etc.) from the DOM."""
        for selector in NOISE_SELECTORS:
            try:
                elements = doc.cssselect(selector)
                for el in elements:
                    parent = el.getparent()
                    if parent is not None:
                        parent.remove(el)
            except Exception:
                continue

    def _extract_title(self, doc, html):
        try:
            # og:title
            match = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', html, re.IGNORECASE)
            if match:
                return match.group(1).strip()

            # h1
            try:
                h1 = doc.find('.//h1')
                if h1 is not None and h1.text:
                    return h1.text.strip()
            except Exception:
                pass

            # <title>
            match = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL | re.IGNORECASE)
            if match:
                return re.sub(r'<[^>]*>', '', match.group(1)).strip()
        except Exception:
            pass
        return 'Untitled'

    def _extract_meta_description(self, doc, html):
        try:
            match = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\'](.*?)["\']', html, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            match = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', html, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        except Exception:
            pass
        return ''

    def _extract_author(self, doc, html):
        try:
            for pattern in [
                r'<meta[^>]+name=["\']author["\'][^>]+content=["\'](.*?)["\']',
                r'<meta[^>]+property=["\']article:author["\'][^>]+content=["\'](.*?)["\']',
            ]:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    return match.group(1).strip()

            try:
                el = doc.find('.//*[@itemprop="author"]')
                if el is not None and el.text:
                    return el.text.strip()
            except Exception:
                pass

            for selector in ['.author', '.byline', '.writer']:
                try:
                    els = doc.cssselect(selector)
                    if els and els[0].text:
                        return els[0].text.strip()
                except Exception:
                    continue
        except Exception:
            pass
        return ''

    def _extract_date(self, doc, html):
        try:
            for pattern in [
                r'<meta[^>]+property=["\']article:published_time["\'][^>]+content=["\'](.*?)["\']',
            ]:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    return match.group(1).strip()

            try:
                el = doc.find('.//*[@itemprop="datePublished"]')
                if el is not None:
                    return (el.get('content') or el.text or '').strip()
            except Exception:
                pass

            try:
                time_el = doc.find('.//time')
                if time_el is not None:
                    return (time_el.get('datetime') or time_el.text or '').strip()
            except Exception:
                pass
        except Exception:
            pass
        return ''

    def _extract_site_name(self, doc, html, url):
        try:
            match = re.search(r'<meta[^>]+property=["\']og:site_name["\'][^>]+content=["\'](.*?)["\']', html, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        except Exception:
            pass
        return urlparse(url).hostname or ''

    def _extract_main_content(self, doc, html):
        try:
            # Try <article> first
            try:
                articles = doc.cssselect('article')
                if articles:
                    text = self._get_text(articles[0])
                    if len(text) > 200:
                        return text
            except Exception:
                pass

            # Try content selectors
            for selector in ['.post-content', '.article-content', '.entry-content',
                            '.content', '.main-content', '#content', '#main',
                            '[role="main"]', 'main']:
                try:
                    els = doc.cssselect(selector)
                    if els:
                        text = self._get_text(els[0])
                        if len(text) > 200:
                            return text
                except Exception:
                    continue

            # Fallback: all <p> tags
            try:
                paragraphs = doc.cssselect('p')
                text_parts = []
                for p in paragraphs:
                    p_text = (p.text_content() if hasattr(p, 'text_content') else (p.text or '')).strip()
                    if len(p_text) > 30:
                        text_parts.append(p_text)
                text = '\n\n'.join(text_parts)
                if len(text) > 100:
                    return self._clean_text(text)
            except Exception:
                pass

            # Last fallback: body text
            try:
                body = doc.find('.//body')
                if body is not None:
                    return self._get_text(body)
            except Exception:
                pass
        except Exception as e:
            logger.error(f"Content extraction error: {e}")

        return ''

    def _extract_images(self, doc, html, url):
        images = []
        try:
            match = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\'](.*?)["\']', html, re.IGNORECASE)
            if match:
                images.append(match.group(1))

            for selector in ['article', '.post-content', '.article-content', '.content', 'main']:
                try:
                    els = doc.cssselect(selector)
                    if els:
                        for img in els[0].cssselect('img'):
                            src = img.get('src', '')
                            if src:
                                if not src.startswith('http'):
                                    src = url.rstrip('/') + '/' + src.lstrip('/')
                                images.append(src)
                        if images:
                            break
                except Exception:
                    continue
        except Exception:
            pass

        seen = set()
        unique = []
        for img in images:
            if img not in seen:
                seen.add(img)
                unique.append(img)
        return unique[:10]

    def _get_text(self, element):
        try:
            if hasattr(element, 'text_content'):
                text = element.text_content()
            else:
                text = element.text or ''
                for child in element:
                    text += ' ' + self._get_text(child)
            return self._clean_text(text)
        except Exception:
            return ''

    def _clean_text(self, text):
        import html as html_mod
        text = html_mod.unescape(text)
        text = html_mod.unescape(text)
        text = re.sub(r'<[^>]*>', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def _error_result(self, url, error):
        return {
            'url': url,
            'title': '',
            'description': '',
            'author': '',
            'publish_date': '',
            'site_name': urlparse(url).hostname or '',
            'content': '',
            'word_count': 0,
            'images': [],
            'success': False,
            'error': error,
        }
