from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from shop.sitemap import StaticSitemap, ItemSitemap, CategorySitemap
from django.contrib.staticfiles.views import serve
from django.views.static import serve as media_serve


sitemaps = {
    'static': StaticSitemap,
    'category': CategorySitemap,
    'item': ItemSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
    path('account/', include('account.urls')),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)

# if not settings.DEBUG:
#     urlpatterns.append(path('static/<path:path>', serve, {'insecure': True}))
#     urlpatterns.append(path('media/<path:path>', media_serve, {'document_root': settings .MEDIA_ROOT}))