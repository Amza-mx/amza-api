from django.contrib import admin

from .models import StoreProduct, KeepaNotification


@admin.register(StoreProduct)
class StoreProductAdmin(admin.ModelAdmin):
    list_display = (
        'asin',
        'sku',
        'price_mxn',
        'tracking_type',
        'tracking_enabled',
        'keepa_marketplace',
        'keepa_available',
        'updated_at',
    )
    search_fields = ('asin', 'sku', 'title', 'brand')
    list_filter = ('tracking_type', 'tracking_enabled', 'keepa_marketplace', 'keepa_available')


@admin.register(KeepaNotification)
class KeepaNotificationAdmin(admin.ModelAdmin):
    list_display = ('asin', 'marketplace', 'event_type', 'is_read', 'created_at')
    search_fields = ('asin', 'event_type')
    list_filter = ('marketplace', 'event_type', 'is_read')
