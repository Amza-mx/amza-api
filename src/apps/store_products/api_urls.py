from django.urls import path

from api.v1.webhooks.views import KeepaWebhookView

urlpatterns = [
    # Redirigir a la nueva vista basada en clases
    path('webhooks/keepa', KeepaWebhookView.as_view(), name='keepa_webhook'),
]
