from django.urls import path
from . import views

urlpatterns = [
    path("scrape", views.scrape),
    path("analyze", views.analyze),
    path("platforms", views.get_platforms),
    path("export", views.export_data),
    path("exports", views.get_exports),
    path("exports/<str:filename>/download", views.download_export),
    path("exports/<str:filename>", views.delete_export),
    path("scrape-history", views.get_history),
    path("scrape-history/<int:pk>", views.delete_history),
    path("popular-searches", views.get_popular_searches),
    path("cached-news", views.get_cached_news),
]
