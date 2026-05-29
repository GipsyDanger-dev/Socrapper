from django.db import models


class ScrapeHistory(models.Model):
    platform = models.CharField(max_length=50)
    keyword = models.CharField(max_length=255)
    limit = models.IntegerField()
    results_count = models.IntegerField(default=0)
    sentiment_summary = models.JSONField(null=True, blank=True)
    raw_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'scrape_histories'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.platform} - {self.keyword}"
