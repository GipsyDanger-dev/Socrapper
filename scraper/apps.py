from django.apps import AppConfig


class ScraperConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scraper'

    def ready(self):
        """Start background services when Django starts."""
        import threading
        from .services.news_cache_service import news_cache

        # Start news cache in background (delayed to avoid import issues)
        def start_cache():
            import time
            time.sleep(2)  # Wait for Django to fully initialize
            news_cache.start()

        threading.Thread(target=start_cache, daemon=True).start()
