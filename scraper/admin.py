from django.contrib import admin

from .models import PopularSearch, ScrapeHistory


@admin.register(ScrapeHistory)
class ScrapeHistoryAdmin(admin.ModelAdmin):
    list_display = ("keyword", "platform", "results_count", "created_at", "updated_at")
    list_filter = ("platform", "created_at")
    search_fields = ("keyword", "platform")
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 50


@admin.register(PopularSearch)
class PopularSearchAdmin(admin.ModelAdmin):
    list_display = ("keyword", "count", "last_searched")
    search_fields = ("keyword",)
    ordering = ("-count",)
