import re
import json
import logging
import threading
from django.conf import settings

logger = logging.getLogger(__name__)


class LLMAnalysisService:
    _client = None
    _client_lock = threading.Lock()

    def __init__(self):
        self.api_key = getattr(settings, "LLM_API_KEY", "")
        self.base_url = getattr(settings, "LLM_BASE_URL", "https://api.openai.com/v1")
        self.model = getattr(settings, "LLM_MODEL", "gpt-4o-mini")
        # LLM_MODEL may be a comma-separated fallback chain, e.g.
        # "google/gemma-4-31b-it:free,openai/gpt-oss-20b:free". Free-tier
        # endpoints are often rate-limited or temporarily unavailable, so
        # trying the next model keeps AI analysis working.
        self.models = [m.strip() for m in self.model.split(",") if m.strip()]
        self.last_model = None

    def _get_client(self):
        if LLMAnalysisService._client is not None:
            return LLMAnalysisService._client
        with LLMAnalysisService._client_lock:
            if LLMAnalysisService._client is not None:
                return LLMAnalysisService._client
            from openai import OpenAI

            default_headers = None
            if "openrouter.ai" in self.base_url:
                # Recommended by OpenRouter so requests are attributed to the site
                default_headers = {
                    "HTTP-Referer": "https://www.socrapper.my.id",
                    "X-Title": "Socrapper",
                }
            LLMAnalysisService._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                default_headers=default_headers,
            )
        return LLMAnalysisService._client

    def is_configured(self):
        return bool(self.api_key) and bool(self.base_url)

    def analyze(self, prompt, system_prompt=""):
        if not self.is_configured():
            logger.warning("LLM not configured. Set LLM_API_KEY and LLM_BASE_URL in .env")
            return None

        client = self._get_client()

        # Reset before trying, so a total failure doesn't leave the previous
        # request's model on this (module-level singleton) service.
        self.last_model = None

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        for model in self.models:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=2000,
                )
                self.last_model = model
                return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"LLM analysis error with {model}: {e}")

        return None

    def analyze_sentiment(self, texts):
        system_prompt = """Kamu adalah analis sentimen profesional. Analisis sentimen dari teks-teks yang diberikan.

Untuk setiap teks, berikan:
1. Sentimen: positive/negative/neutral
2. Confidence: 0-100%
3. Alasan singkat (1 kalimat)

Response dalam format JSON:
{
  "results": [
    {
      "text": "teks asli",
      "sentiment": "positive/negative/neutral",
      "confidence": 85,
      "reason": "alasan singkat"
    }
  ],
  "summary": {
    "positive": 5,
    "negative": 3,
    "neutral": 2,
    "overall": "positive",
    "overall_confidence": 78
  }
}"""

        text_list = ""
        for i, text in enumerate(texts):
            text_list += f"{i + 1}. {text[:500]}\n\n"

        prompt = f"Analisis sentimen dari teks berikut:\n\n{text_list}"
        response = self.analyze(prompt, system_prompt)

        if not response:
            return self._fallback_sentiment(texts)

        parsed = self._parse_json(response)
        if parsed:
            return parsed

        return self._fallback_sentiment(texts)

    def analyze_market(self, query, articles):
        system_prompt = """Kamu adalah analis pasar finansial profesional. Analisis data pasar yang diberikan dan berikan insight yang actionable.

Response dalam format JSON:
{
  "query": "query asli",
  "sentiment": {
    "overall": "bullish/bearish/neutral",
    "confidence": 0-100,
    "score": -100 to 100
  },
  "summary": "Ringkasan analisis 2-3 kalimat",
  "key_points": [
    "Poin penting 1",
    "Poin penting 2"
  ],
  "risk_factors": [
    "Risiko 1",
    "Risiko 2"
  ],
  "opportunities": [
    "Peluang 1",
    "Peluang 2"
  ],
  "recommendation": "Rekomendasi singkat",
  "timeframe": "short-term/medium-term/long-term"
}"""

        article_texts = self._format_articles(articles, 800)
        prompt = f'Query: "{query}"\n\nBerikut artikel-artikel terkait:\n\n{article_texts}\n\nBerikan analisis pasar yang komprehensif berdasarkan data di atas.'

        response = self.analyze(prompt, system_prompt)

        if not response:
            return self._fallback_market(query)

        parsed = self._parse_json(response)
        if parsed:
            return parsed

        return self._fallback_market(query)

    def analyze_general(self, query, articles):
        system_prompt = """Kamu adalah asisten AI yang ahli menganalisis informasi dari berbagai sumber. Berikan analisis yang komprehensif, objektif, dan terstruktur.

Response dalam format JSON:
{
  "query": "query asli",
  "analysis": "Analisis lengkap 3-5 paragraf",
  "key_findings": [
    "Temuan penting 1",
    "Temuan penting 2"
  ],
  "sentiment": {
    "overall": "positive/negative/neutral/mixed",
    "confidence": 0-100
  },
  "entities": {
    "people": ["nama orang"],
    "organizations": ["nama organisasi"],
    "locations": ["lokasi"],
    "topics": ["topik utama"]
  },
  "related_topics": ["topik terkait"],
  "credibility": {
    "score": 0-100,
    "factors": ["faktor yang mempengaruhi kredibilitas"]
  }
}"""

        article_texts = self._format_articles(articles, 600)
        prompt = f'Query: "{query}"\n\nInformasi dari berbagai sumber:\n\n{article_texts}\n\nBerikan analisis komprehensif berdasarkan data di atas.'

        response = self.analyze(prompt, system_prompt)

        if not response:
            return self._fallback_general(query)

        parsed = self._parse_json(response)
        if parsed:
            return parsed

        return {
            "query": query,
            "analysis": response,
            "key_findings": [],
            "sentiment": {"overall": "neutral", "confidence": 50},
            "entities": {"people": [], "organizations": [], "locations": [], "topics": []},
            "related_topics": [],
            "credibility": {"score": 50, "factors": []},
        }

    def _format_articles(self, articles, max_content=600):
        text = ""
        for i, article in enumerate(articles):
            title = article.get("title", "")
            snippet = article.get("snippet", "") or article.get("content_excerpt", "")
            source = article.get("source", "")
            date = article.get("publish_date", "")

            text += f"--- Artikel {i + 1} ---\n"
            text += f"Judul: {title}\n"
            text += f"Sumber: {source}\n"
            text += f"Tanggal: {date}\n"
            text += f"Konten: {snippet[:max_content]}\n\n"

        return text

    def _parse_json(self, response):
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass

        match = re.search(r"\{[\s\S]*\}", response)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return None

    def _fallback_sentiment(self, texts):
        from scraper.services.sentiment_service import SentimentService

        service = SentimentService()
        result = service.analyze_sentiments(texts)

        overall = (
            "positive"
            if result["percentage"]["positive"] > result["percentage"]["negative"]
            else ("negative" if result["percentage"]["negative"] > result["percentage"]["positive"] else "neutral")
        )

        return {
            "results": [
                {
                    "text": d["text"],
                    "sentiment": d["sentiment"],
                    "confidence": d["confidence"],
                    "reason": "Keyword-based analysis",
                }
                for d in result.get("results") or result.get("details", [])
            ],
            "summary": {
                "positive": result["positive"],
                "negative": result["negative"],
                "neutral": result["neutral"],
                "overall": overall,
                "overall_confidence": 50,
            },
        }

    def _fallback_market(self, query):
        return {
            "query": query,
            "sentiment": {"overall": "neutral", "confidence": 0, "score": 0},
            "summary": "LLM tidak tersedia. Menampilkan data mentah tanpa analisis AI.",
            "key_points": [],
            "risk_factors": [],
            "opportunities": [],
            "recommendation": "Konfigurasi LLM API untuk analisis otomatis.",
            "timeframe": "N/A",
        }

    def _fallback_general(self, query):
        return {
            "query": query,
            "analysis": "LLM tidak tersedia. Konfigurasi LLM_API_KEY dan LLM_BASE_URL di .env untuk analisis AI.",
            "key_findings": [],
            "sentiment": {"overall": "neutral", "confidence": 0},
            "entities": {"people": [], "organizations": [], "locations": [], "topics": []},
            "related_topics": [],
            "credibility": {"score": 0, "factors": []},
        }
