from django.contrib import admin
from apps.products.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'product_title']
    search_fields = ['sku', 'product_title']
