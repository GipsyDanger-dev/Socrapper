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
