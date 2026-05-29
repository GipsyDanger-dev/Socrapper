import re


class SentimentService:
    POSITIVE_KEYWORDS = [
        'bagus', 'mantap', 'hebat', 'keren', 'amazing', 'excellent',
        'love', 'suka', 'fantastic', 'wonderful', 'great', 'awesome',
        'luar biasa', 'sempurna', 'terbaik', 'sungguh',
    ]

    NEGATIVE_KEYWORDS = [
        'buruk', 'jelek', 'kecewa', 'marah', 'benci', 'hate', 'terrible',
        'awful', 'horrible', 'bad', 'worst', 'sucks', 'stupid', 'sampah',
        'mengecewakan', 'parah', 'tidak suka', 'sangat marah',
    ]

    NEGATION_WORDS = [
        'tidak', 'bukan', 'kurang', 'jangan', 'belum',
        'ga', 'gak', 'nggak', 'enggak', 'tanpa',
    ]

    def analyze_sentiments(self, texts):
        analysis = {
            'positive': 0,
            'negative': 0,
            'neutral': 0,
            'details': [],
        }

        for text in texts:
            sentiment = self._detect_sentiment(text)
            confidence = self._calculate_confidence(text, sentiment)

            analysis[sentiment] += 1
            analysis['details'].append({
                'text': text,
                'sentiment': sentiment,
                'confidence': round(confidence, 2),
            })

        total = len(texts)
        analysis['percentage'] = {
            'positive': round((analysis['positive'] / total) * 100, 2),
            'negative': round((analysis['negative'] / total) * 100, 2),
            'neutral': round((analysis['neutral'] / total) * 100, 2),
        }

        return analysis

    def _detect_sentiment(self, text):
        text_lower = text.lower()

        positive_count = 0
        negative_count = 0

        multi_word_positive = [k for k in self.POSITIVE_KEYWORDS if ' ' in k]
        single_word_positive = [k for k in self.POSITIVE_KEYWORDS if ' ' not in k]
        multi_word_negative = [k for k in self.NEGATIVE_KEYWORDS if ' ' in k]
        single_word_negative = [k for k in self.NEGATIVE_KEYWORDS if ' ' not in k]

        for keyword in multi_word_positive:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            positive_count += len(re.findall(pattern, text_lower))

        for keyword in multi_word_negative:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            negative_count += len(re.findall(pattern, text_lower))

        for keyword in single_word_positive:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            for match in re.finditer(pattern, text_lower):
                text_before = text_lower[:match.start()]
                if self._is_negated(text_before):
                    negative_count += 1
                else:
                    positive_count += 1

        for keyword in single_word_negative:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            for match in re.finditer(pattern, text_lower):
                text_before = text_lower[:match.start()]
                if self._is_negated(text_before):
                    positive_count += 1
                else:
                    negative_count += 1

        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        return 'neutral'

    def _is_negated(self, text_before_match):
        words = text_before_match.split()
        window = words[-3:] if len(words) >= 3 else words
        return any(w in self.NEGATION_WORDS for w in window)

    def _calculate_confidence(self, text, sentiment):
        text_lower = text.lower()
        matches = 0

        keywords = []
        if sentiment == 'positive':
            keywords = self.POSITIVE_KEYWORDS
        elif sentiment == 'negative':
            keywords = self.NEGATIVE_KEYWORDS

        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches += len(re.findall(pattern, text_lower))

        return min(matches * 15, 100)
