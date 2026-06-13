from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({'status': 'ok', 'message': 'Socrapper API v2.0'})

urlpatterns = [
    path('', api_root),
    path('api/', include('scraper.urls')),
    path('api/', include('surfer.urls')),
]
