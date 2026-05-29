from django.urls import path, include

urlpatterns = [
    path('api/', include('scraper.urls')),
    path('api/', include('surfer.urls')),
]
