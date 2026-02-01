"""
Webhooks API URLs

Este módulo define los endpoints de webhooks para integraciones externas.
"""

from django.urls import path

from apps.store_products.views import keepa_webhook

app_name = 'webhooks'

urlpatterns = [
    # Keepa Webhook
    # Recibe notificaciones push de Keepa API cuando se disparan eventos de tracking
    # (cambios de precio, stock, etc.)
    path('keepa', keepa_webhook, name='keepa'),
]
