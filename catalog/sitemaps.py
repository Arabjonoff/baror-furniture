"""Qidiruv tizimlari (Google, Yandex) uchun sitemap.xml manbalari."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Category, Product


class StaticViewSitemap(Sitemap):
    """Statik sahifalar — bosh sahifa va katalog."""

    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return ['catalog:home', 'catalog:product_list']

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    """Faol kategoriyalar."""

    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return Category.objects.filter(is_active=True)


class ProductSitemap(Sitemap):
    """Sotuvdagi mahsulotlar."""

    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return Product.objects.filter(is_available=True)

    def lastmod(self, obj):
        return obj.updated_at
