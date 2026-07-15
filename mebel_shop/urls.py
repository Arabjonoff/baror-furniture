"""
Asosiy URL konfiguratsiyasi — mebel_shop loyihasi.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('boshqaruv/', include('dashboard.urls')),
    path('', include('catalog.urls')),
    path('savat/', include('cart.urls')),
    path('sevimlilar/', include('wishlist.urls')),
    path('buyurtmalar/', include('orders.urls')),
    path('hisob/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
