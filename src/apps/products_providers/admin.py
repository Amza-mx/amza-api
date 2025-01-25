from django.contrib import admin
from apps.products_providers.models import ProductProvider


@admin.register(ProductProvider)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name',]
    list_filter = ['is_active']
