from django.db import models


class ScrapeHistory(models.Model):
    platform = models.CharField(max_length=50, db_index=True)
    keyword = models.CharField(max_length=255, db_index=True)
    limit = models.IntegerField()
    results_count = models.IntegerField(default=0)
    sentiment_summary = models.JSONField(null=True, blank=True)
    raw_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "scrape_histories"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.platform} - {self.keyword}"


class PopularSearch(models.Model):
    keyword = models.CharField(max_length=255, unique=True, db_index=True)
    count = models.IntegerField(default=1)
    last_searched = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "popular_searches"
        ordering = ["-count", "-last_searched"]

    def __str__(self):
        return f"{self.keyword} ({self.count})"


class KeywordTrend(models.Model):
    """Per-search sentiment snapshot used to build time-series trends.

    A row is recorded every time a keyword is scraped or surfed with sentiment
    analysis, so the trend endpoint can group snapshots by day.
    """

    keyword = models.CharField(max_length=255, db_index=True)
    positive = models.IntegerField(default=0)
    negative = models.IntegerField(default=0)
    neutral = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "keyword_trends"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["keyword", "created_at"], name="trend_keyword_date_idx"),
        ]

    def __str__(self):
        return f"{self.keyword} ({self.created_at:%Y-%m-%d})"
