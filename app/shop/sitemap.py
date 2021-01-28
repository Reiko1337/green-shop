from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product, Category


class StaticSitemap(Sitemap):
    priority = 1
    changefreq = 'daily'

    def items(self):
        return ['main_page']

    def location(self, item):
        return reverse(item)


class ItemSitemap(Sitemap):
    priority = 0.50
    changefreq = 'daily'

    def items(self):
        return Product.objects.all()


class CategorySitemap(Sitemap):
    priority = 0.75
    changefreq = 'daily'

    def items(self):
        return Category.objects.all()
