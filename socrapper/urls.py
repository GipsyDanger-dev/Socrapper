from django.urls import path, include
from django.http import JsonResponse, HttpResponse

def api_root(request):
    return JsonResponse({'status': 'ok', 'message': 'Socrapper API v2.0'})

def robots_txt(request):
    content = "User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /admin/\n\nSitemap: https://socrapper.com/sitemap.xml\n"
    return HttpResponse(content, content_type='text/plain')

def sitemap_xml(request):
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://socrapper.com/</loc>
        <lastmod>2026-06-13</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>"""
    return HttpResponse(content, content_type='application/xml')

urlpatterns = [
    path('', api_root),
    path('robots.txt', robots_txt),
    path('sitemap.xml', sitemap_xml),
    path('api/', include('scraper.urls')),
    path('api/', include('surfer.urls')),
]
