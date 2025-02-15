from django.contrib import admin
from apps.sellers.models import Seller


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = [
        'name',
    ]
    list_filter = ['is_active']
