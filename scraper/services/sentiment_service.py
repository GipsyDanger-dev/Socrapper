import re
import json
import logging
import threading

logger = logging.getLogger(__name__)


class SentimentService:
    POSITIVE_KEYWORDS = [
        "bagus",
        "mantap",
        "hebat",
        "keren",
        "amazing",
        "excellent",
        "love",
        "suka",
        "fantastic",
        "wonderful",
        "great",
        "awesome",
        "luar biasa",
        "sempurna",
        "terbaik",
        "sungguh",
    ]

    NEGATIVE_KEYWORDS = [
        "buruk",
        "jelek",
        "kecewa",
        "marah",
        "benci",
        "hate",
        "terrible",
        "awful",
        "horrible",
        "bad",
        "worst",
        "sucks",
        "stupid",
        "sampah",
        "mengecewakan",
        "parah",
        "tidak suka",
        "sangat marah",
    ]

    NEGATION_WORDS = [
        "tidak",
        "bukan",
        "kurang",
        "jangan",
        "belum",
        "ga",
        "gak",
        "nggak",
        "enggak",
        "tanpa",
    ]

    def __init__(self):
        self._llm_service = None
        self._llm_lock = threading.Lock()

    def _get_llm(self):
        if self._llm_service is not None:
            return self._llm_service if self._llm_service is not False else None
        with self._llm_lock:
            if self._llm_service is not None:
                return self._llm_service if self._llm_service is not False else None
            try:
                from surfer.services.llm_analysis_service import LLMAnalysisService

                self._llm_service = LLMAnalysisService()
            except Exception:
                self._llm_service = False
        return self._llm_service if self._llm_service is not False else None

    def analyze_sentiments(self, texts):
        llm = self._get_llm()
        if llm and llm.is_configured():
            result = self._analyze_with_llm(llm, texts)
            if result:
                return result

        return self._analyze_with_keywords(texts)

    def _analyze_with_llm(self, llm, texts):
        try:
            system_prompt = """Kamu adalah analis sentimen profesional yang ahli dalam bahasa Indonesia dan Inggris. Analisis sentimen dari setiap teks yang diberikan secara mendalam.

Untuk setiap teks, tentukan:
- sentiment: "positive", "negative", atau "neutral"
- confidence: angka 0-100
- reason: alasan singkat mengapa sentimen tersebut (1-2 kalimat)

Untuk keseluruhan analisis, berikan:
- analysis: penjelasan lengkap tentang pola sentimen yang ditemukan (3-5 kalimat)
- key_insights: insight penting dari data (array of strings)
- dominant_emotion: emosi dominan yang terdeteksi (misal: antusiasme, kekhawatiran, harapan, kekecewaan)

Response HARUS dalam format JSON yang valid:
{
  "results": [
    {"text": "teks asli", "sentiment": "positive", "confidence": 85, "reason": "alasan"}
  ],
  "summary": {
    "positive": 5,
    "negative": 3,
    "neutral": 2,
    "percentage": {"positive": 50, "negative": 30, "neutral": 20},
    "overall": "positive",
    "overall_confidence": 78
  },
  "analysis": "Penjelasan lengkap tentang pola sentimen...",
  "key_insights": ["Insight 1", "Insight 2"],
  "dominant_emotion": "antusiasme"
}

Jangan tambahkan teks lain di luar JSON."""

            text_list = ""
            for i, text in enumerate(texts):
                text_list += f"{i + 1}. {text[:500]}\n\n"

            prompt = f"Analisis sentimen dari teks berikut:\n\n{text_list}"
            response = llm.analyze(prompt, system_prompt)

            if not response:
                return None

            parsed = self._parse_json(response)
            if parsed and "results" in parsed and "summary" in parsed:
                return parsed

            return None
        except Exception as e:
            logger.warning(f"LLM sentiment analysis failed: {e}")
            return None

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

    def _analyze_with_keywords(self, texts):
        analysis = {
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "results": [],
        }

        if not texts:
            analysis["percentage"] = {"positive": 0, "negative": 0, "neutral": 100}
            return analysis

        for text in texts:
            sentiment = self._detect_sentiment(text)
            confidence = self._calculate_confidence(text, sentiment)

            analysis[sentiment] += 1
            analysis["results"].append(
                {
                    "text": text,
                    "sentiment": sentiment,
                    "confidence": round(confidence, 2),
                }
            )

        total = len(texts)
        analysis["percentage"] = {
            "positive": round((analysis["positive"] / total) * 100, 2),
            "negative": round((analysis["negative"] / total) * 100, 2),
            "neutral": round((analysis["neutral"] / total) * 100, 2),
        }

        return analysis

    def _detect_sentiment(self, text):
        text_lower = text.lower()

        positive_count = 0
        negative_count = 0

        multi_word_positive = [k for k in self.POSITIVE_KEYWORDS if " " in k]
        single_word_positive = [k for k in self.POSITIVE_KEYWORDS if " " not in k]
        multi_word_negative = [k for k in self.NEGATIVE_KEYWORDS if " " in k]
        single_word_negative = [k for k in self.NEGATIVE_KEYWORDS if " " not in k]

        for keyword in multi_word_positive:
            pattern = r"\b" + re.escape(keyword) + r"\b"
            positive_count += len(re.findall(pattern, text_lower))

        for keyword in multi_word_negative:
            pattern = r"\b" + re.escape(keyword) + r"\b"
            negative_count += len(re.findall(pattern, text_lower))

        for keyword in single_word_positive:
            pattern = r"\b" + re.escape(keyword) + r"\b"
            for match in re.finditer(pattern, text_lower):
                text_before = text_lower[: match.start()]
                if self._is_negated(text_before):
                    negative_count += 1
                else:
                    positive_count += 1

        for keyword in single_word_negative:
            pattern = r"\b" + re.escape(keyword) + r"\b"
            for match in re.finditer(pattern, text_lower):
                text_before = text_lower[: match.start()]
                if self._is_negated(text_before):
                    positive_count += 1
                else:
                    negative_count += 1

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        return "neutral"

    def _is_negated(self, text_before_match):
        words = text_before_match.split()
        window = words[-3:] if len(words) >= 3 else words
        return any(w in self.NEGATION_WORDS for w in window)

    def _calculate_confidence(self, text, sentiment):
        text_lower = text.lower()
        matches = 0

        keywords = []
        if sentiment == "positive":
            keywords = self.POSITIVE_KEYWORDS
        elif sentiment == "negative":
            keywords = self.NEGATIVE_KEYWORDS

        for keyword in keywords:
            pattern = r"\b" + re.escape(keyword) + r"\b"
            matches += len(re.findall(pattern, text_lower))

        return min(matches * 15, 100)
