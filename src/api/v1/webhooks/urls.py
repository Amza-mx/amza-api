"""
Webhooks API URLs

Este módulo define los endpoints de webhooks para integraciones externas.
"""

from django.urls import path

from .views import KeepaWebhookView

app_name = 'webhooks'

urlpatterns = [
    # Keepa Webhook
    # Recibe notificaciones push de Keepa API cuando se disparan eventos de tracking
    # (cambios de precio, stock, etc.)
    path('keepa', KeepaWebhookView.as_view(), name='keepa'),
]
