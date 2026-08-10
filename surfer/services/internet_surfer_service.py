import re
import logging
import hashlib
from collections import Counter

logger = logging.getLogger(__name__)

STOPWORDS = {
    "the",
    "a",
    "an",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "shall",
    "can",
    "need",
    "dare",
    "ought",
    "used",
    "to",
    "of",
    "in",
    "for",
    "on",
    "with",
    "at",
    "by",
    "from",
    "up",
    "about",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "between",
    "out",
    "off",
    "over",
    "under",
    "again",
    "further",
    "then",
    "once",
    "here",
    "there",
    "when",
    "where",
    "why",
    "how",
    "all",
    "both",
    "each",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "nor",
    "not",
    "only",
    "own",
    "same",
    "so",
    "than",
    "too",
    "very",
    "just",
    "because",
    "but",
    "and",
    "or",
    "if",
    "while",
    "this",
    "that",
    "these",
    "those",
    "i",
    "me",
    "my",
    "we",
    "our",
    "you",
    "your",
    "he",
    "him",
    "his",
    "she",
    "her",
    "it",
    "its",
    "they",
    "them",
    "their",
    "what",
    "which",
    "who",
    "whom",
    "yang",
    "dan",
    "di",
    "ke",
    "dari",
    "ini",
    "itu",
    "untuk",
    "dengan",
    "pada",
    "adalah",
    "akan",
    "juga",
    "sudah",
    "belum",
    "bisa",
    "tidak",
    "ada",
    "oleh",
    "seperti",
    "setelah",
    "sebelum",
    "atau",
    "tapi",
    "karena",
    "jika",
    "maka",
    "serta",
    "antara",
    "lain",
    "lebih",
}


class InternetSurferService:
    def __init__(self):
        from .search_engine_service import SearchEngineService
        from .content_extractor_service import ContentExtractorService
        from scraper.services.sentiment_service import SentimentService

        self.search_engine = SearchEngineService()
        self.content_extractor = ContentExtractorService()
        self.sentiment_service = SentimentService()

    @staticmethod
    def _strip_html(text):
        if not text:
            return ""
        import html as html_mod

        clean = html_mod.unescape(text)
        clean = html_mod.unescape(clean)
        clean = re.sub(r"<[^>]*>", " ", clean)
        # Collapse horizontal whitespace but preserve newlines
        clean = re.sub(r"[^\S\n]+", " ", clean)
        clean = re.sub(r"\n\s*\n", "\n", clean)
        return clean.strip()

    def surf(self, query, options=None):
        options = options or {}
        search_limit = options.get("search_limit", 5)
        extract_content = options.get("extract_content", True)
        analyze_sentiment = options.get("analyze_sentiment", True)

        # Generate cache key
        cache_key = hashlib.md5(
            f"surf:{query}:{search_limit}:{extract_content}:{analyze_sentiment}".encode()
        ).hexdigest()

        # Check cache
        from scraper.services.cache_utils import search_cache

        cached = search_cache.get(cache_key)
        if cached:
            logger.debug(f"Cache hit for surf query: {query}")
            return cached

        try:
            search_results = self.search_engine.search(query, search_limit)

            if not search_results:
                return {
                    "success": False,
                    "error": "No search results found",
                    "query": query,
                }

            fetchable_urls = [r["url"] for r in search_results if r.get("url", "").startswith("http")]

            extracted_data = []
            if extract_content and fetchable_urls:
                extracted_data = self.content_extractor.extract_multiple(fetchable_urls)

            merged_results = self._merge_results(search_results, extracted_data)

            sentiment_analysis = None
            if analyze_sentiment and merged_results:
                texts = []
                text_indices = []
                for i, item in enumerate(merged_results):
                    parts = [item.get("title", ""), item.get("snippet", ""), item.get("content_excerpt", "")]
                    text = ". ".join(self._strip_html(p) for p in parts if p)
                    if len(text) > 10:
                        texts.append(text)
                        text_indices.append(i)

                if texts:
                    sentiment_analysis = self.sentiment_service.analyze_sentiments(texts)
                    # Attach sentiment to each merged result that was analyzed
                    if sentiment_analysis and "results" in sentiment_analysis:
                        for j, idx in enumerate(text_indices):
                            if j < len(sentiment_analysis["results"]):
                                sent_item = sentiment_analysis["results"][j]
                                merged_results[idx]["sentiment"] = sent_item.get("sentiment", "neutral")
                                merged_results[idx]["sentiment_confidence"] = sent_item.get("confidence", 0)

            summary = self._generate_summary(query, merged_results, sentiment_analysis)

            result = {
                "success": True,
                "query": query,
                "search_results": search_results,
                "extracted_content": extracted_data,
                "merged_results": merged_results,
                "sentiment": sentiment_analysis,
                "summary": summary,
                "total_results": len(merged_results),
            }

            # Cache the result
            search_cache.set(cache_key, result)

            return result
        except Exception as e:
            logger.error(f"Internet surfing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
            }

    def deep_surf(self, query, pages=3):
        all_results = []
        per_query_limit = max(15, pages * 10)

        # Generate diverse query variations for broader coverage
        queries = [
            query,
            f"{query} terbaru",
            f"{query} analisis",
            f"{query} opini",
            f"{query} review",
            f"{query} diskusi",
        ][: pages + 3]  # Limit based on pages param

        for q in queries:
            try:
                results = self.surf(
                    q,
                    {
                        "search_limit": per_query_limit,
                        "extract_content": True,
                        "analyze_sentiment": False,
                    },
                )
                if results.get("success"):
                    all_results.extend(results.get("merged_results", []))
            except Exception as e:
                logger.warning(f"Deep surf query '{q}' failed: {e}")
                continue

        seen_urls = set()
        unique_results = []
        for result in all_results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)

        texts = []
        text_indices = []
        for i, item in enumerate(unique_results):
            text = self._strip_html(f"{item.get('title', '')}. {item.get('content_excerpt', '')}")
            if len(text.strip()) > 10:
                texts.append(text)
                text_indices.append(i)

        sentiment = None
        if texts:
            sentiment = self.sentiment_service.analyze_sentiments(texts)
            if sentiment and "results" in sentiment:
                for j, idx in enumerate(text_indices):
                    if j < len(sentiment["results"]):
                        sent_item = sentiment["results"][j]
                        unique_results[idx]["sentiment"] = sent_item.get("sentiment", "neutral")
                        unique_results[idx]["sentiment_confidence"] = sent_item.get("confidence", 0)

        return {
            "success": True,
            "query": query,
            "total_results": len(unique_results),
            "results": unique_results,
            "sentiment": sentiment,
            "summary": self._generate_summary(query, unique_results, sentiment),
        }

    def quick_surf(self, query, limit=5):
        # Check cache
        cache_key = hashlib.md5(f"quick:{query}:{limit}".encode()).hexdigest()
        from scraper.services.cache_utils import search_cache

        cached = search_cache.get(cache_key)
        if cached:
            return cached

        search_results = self.search_engine.search(query, limit)

        result = {
            "success": True,
            "query": query,
            "results": search_results,
            "total": len(search_results),
        }

        # Cache the result
        search_cache.set(cache_key, result)

        return result

    def _merge_results(self, search_results, extracted_data):
        merged = []

        for index, search_result in enumerate(search_results):
            item = {
                "title": self._strip_html(search_result.get("title", "")),
                "url": search_result.get("url", ""),
                "snippet": self._strip_html(search_result.get("snippet", "")),
                "source": search_result.get("source", ""),
                "content": "",
                "content_excerpt": "",
                "author": "",
                "publish_date": "",
                "word_count": 0,
                "images": [],
                "extraction_success": False,
            }

            if index < len(extracted_data) and extracted_data[index] and extracted_data[index].get("success"):
                extracted = extracted_data[index]
                item["content"] = self._strip_html(extracted.get("content", ""))
                item["content_excerpt"] = self._get_content_excerpt(extracted.get("content", ""), 500)
                item["author"] = extracted.get("author", "")
                item["publish_date"] = extracted.get("publish_date", "")
                item["word_count"] = extracted.get("word_count", 0)
                item["images"] = extracted.get("images", [])
                item["extraction_success"] = True

            merged.append(item)

        return merged

    def _get_content_excerpt(self, content, max_length=500):
        content = self._strip_html(content)
        if not content or len(content) <= max_length:
            return content or ""

        excerpt = content[:max_length]
        last_space = excerpt.rfind(" ")
        if last_space > 0:
            excerpt = excerpt[:last_space]

        return excerpt + "..."

    def _generate_summary(self, query, results, sentiment):
        total_results = len(results)
        total_words = sum(r.get("word_count", 0) for r in results)
        sources = list(set(r.get("source", "") for r in results if r.get("source")))

        summary = {
            "query": query,
            "total_sources": total_results,
            "total_words": total_words,
            "unique_sources": sources,
            "has_content": total_results > 0,
        }

        if sentiment:
            dominant = "neutral"
            pct = sentiment.get("percentage", {})
            if pct:
                dominant = max(pct, key=pct.get)

            summary["sentiment_overview"] = {
                "positive": pct.get("positive", 0),
                "negative": pct.get("negative", 0),
                "neutral": pct.get("neutral", 0),
                "dominant": dominant,
            }

        summary["key_topics"] = self._extract_key_topics(results)

        return summary

    def _extract_key_topics(self, results):
        all_text = ""
        for result in results:
            all_text += " " + (result.get("title", "") or "") + " " + (result.get("content_excerpt", "") or "")

        all_text = self._strip_html(all_text.lower())
        words = re.split(r"\s+", all_text)
        words = [w for w in words if len(w) > 3 and w not in STOPWORDS and not w.isdigit()]

        frequency = Counter(words)
        return [word for word, _ in frequency.most_common(10)]
