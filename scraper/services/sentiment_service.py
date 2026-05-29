import re
from collections import Counter


class SentimentService:
    POSITIVE_KEYWORDS = [
        'bagus', 'baik', 'hebat', 'luar biasa', 'menakjubkan', 'sempurna',
        'love', 'great', 'awesome', 'excellent', 'amazing', 'wonderful',
        'fantastic', 'brilliant', 'outstanding', 'superb', 'good', 'nice',
        'happy', 'satisfied', 'recommended', 'terbaik', 'puas', 'senang',
        'suka', 'cinta', 'mantap', 'keren', 'joss', 'top',
    ]

    NEGATIVE_KEYWORDS = [
        'buruk', 'jelek', 'parah', 'mengecewakan', 'kacau', 'hancur',
        'bad', 'terrible', 'awful', 'horrible', 'worst', 'disgusting',
        'disappointing', 'poor', 'ugly', 'hate', 'angry', 'frustrated',
        'kecewa', 'marah', 'benci', 'bosan', 'gagal', 'rugi',
        'sampah', 'zonk', 'penipu', 'scam', 'hoax', 'bohong',
    ]

    NEGATION_WORDS = [
        'tidak', 'bukan', 'kurang', 'jangan', 'belum',
        'ga', 'gak', 'nggak', 'enggak', 'tanpa',
    ]

    def analyze(self, texts):
        if not texts:
            return {
                'summary': {'positive': 0, 'negative': 0, 'neutral': 0},
                'percentage': {'positive': 0, 'negative': 0, 'neutral': 0},
                'details': [],
            }

        details = [self._analyze_single(text) for text in texts]
        summary = Counter(d['sentiment'] for d in details)
        total = len(details)

        return {
            'summary': {
                'positive': summary.get('positive', 0),
                'negative': summary.get('negative', 0),
                'neutral': summary.get('neutral', 0),
            },
            'percentage': {
                'positive': round(summary.get('positive', 0) / total * 100, 1),
                'negative': round(summary.get('negative', 0) / total * 100, 1),
                'neutral': round(summary.get('neutral', 0) / total * 100, 1),
            },
            'details': details,
        }

    def _analyze_single(self, text):
        text_lower = text.lower()
        words = text_lower.split()

        positive_score = 0
        negative_score = 0

        # Check negation context
        negated_words = set()
        for i, word in enumerate(words):
            if word in self.NEGATION_WORDS:
                for j in range(max(0, i - 3), min(len(words), i + 4)):
                    negated_words.add(j)

        # Score positive keywords
        for keyword in self.POSITIVE_KEYWORDS:
            if ' ' in keyword:
                if keyword in text_lower:
                    positive_score += 2
            else:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                for match in re.finditer(pattern, text_lower):
                    idx = len(text_lower[:match.start()].split()) - 1
                    if idx not in negated_words:
                        positive_score += 1
                    else:
                        negative_score += 0.5

        # Score negative keywords
        for keyword in self.NEGATIVE_KEYWORDS:
            if ' ' in keyword:
                if keyword in text_lower:
                    negative_score += 2
            else:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                for match in re.finditer(pattern, text_lower):
                    idx = len(text_lower[:match.start()].split()) - 1
                    if idx not in negated_words:
                        negative_score += 1
                    else:
                        positive_score += 0.5

        # Determine sentiment
        if positive_score > negative_score and positive_score > 0:
            sentiment = 'positive'
            confidence = min(100, round(positive_score / (positive_score + negative_score + 1) * 100))
        elif negative_score > positive_score and negative_score > 0:
            sentiment = 'negative'
            confidence = min(100, round(negative_score / (positive_score + negative_score + 1) * 100))
        else:
            sentiment = 'neutral'
            confidence = 50

        return {
            'text': text,
            'sentiment': sentiment,
            'confidence': confidence,
        }
