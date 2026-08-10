from django.urls import path
from . import views

urlpatterns = [
    path("surf", views.surf),
    path("surf/start", views.start_surf),
    path("surf/events/<str:job_id>", views.surf_events),
    path("surf/status/<str:job_id>", views.surf_status),
    path("surf/compare", views.compare),
    path("surf/quick", views.quick_surf),
    path("surf/deep", views.deep_surf),
    path("surf/extract", views.extract_url),
    path("surf/ai-analyze", views.ai_analyze),
]
