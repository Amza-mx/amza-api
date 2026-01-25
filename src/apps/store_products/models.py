from django.db import models


class StoreProduct(models.Model):
    class TrackingType(models.TextChoices):
        REGULAR = 'regular', 'Regular'
        MARKETPLACE = 'marketplace', 'Marketplace'

    asin = models.CharField(max_length=20, unique=True)
    sku = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=255, blank=True)
    brand = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=255, blank=True)

    price_mxn = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    tracking_type = models.CharField(
        max_length=20,
        choices=TrackingType.choices,
        default=TrackingType.REGULAR,
    )
    tracking_enabled = models.BooleanField(default=True)
    keepa_marketplace = models.CharField(max_length=2, default='US')
    keepa_tracking_id = models.CharField(max_length=100, blank=True)

    last_us_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    last_keepa_notification_at = models.DateTimeField(null=True, blank=True)
    keepa_available = models.BooleanField(default=True)
    keepa_unavailable_reason = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.asin}'


class KeepaNotification(models.Model):
    store_product = models.ForeignKey(
        StoreProduct,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='keepa_notifications',
    )
    asin = models.CharField(max_length=20, blank=True)
    marketplace = models.CharField(max_length=10, blank=True)
    event_type = models.CharField(max_length=50, blank=True)
    message = models.TextField(blank=True)
    payload = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'KeepaNotification {self.asin} {self.created_at:%Y-%m-%d %H:%M:%S}'
