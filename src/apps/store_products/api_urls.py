from django.urls import path

from .views import keepa_webhook

urlpatterns = [
    path('webhooks/keepa', keepa_webhook, name='keepa_webhook'),
]
