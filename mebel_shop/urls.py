"""
Asosiy URL konfiguratsiyasi — mebel_shop loyihasi.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from catalog.sitemaps import CategorySitemap, ProductSitemap, StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'categories': CategorySitemap,
    'products': ProductSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('boshqaruv/', include('dashboard.urls')),
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap',
    ),
    path(
        'robots.txt',
        TemplateView.as_view(template_name='robots.txt', content_type='text/plain'),
        name='robots',
    ),
    path('', include('catalog.urls')),
    path('savat/', include('cart.urls')),
    path('sevimlilar/', include('wishlist.urls')),
    path('buyurtmalar/', include('orders.urls')),
    path('hisob/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
