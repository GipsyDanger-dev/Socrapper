from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='http://localhost:5178/', permanent=False)),
    path('api/', include('scraper.urls')),
    path('api/', include('surfer.urls')),
]
