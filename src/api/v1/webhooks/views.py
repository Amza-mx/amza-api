"""
Webhooks API Views

Este módulo contiene las vistas para recibir webhooks de servicios externos.
"""

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.store_products.models import StoreProduct, KeepaNotification


class KeepaWebhookView(APIView):
    """
    Vista para recibir notificaciones push de Keepa API.

    Este endpoint recibe notificaciones cuando se disparan eventos de tracking
    configurados en Keepa (cambios de precio, disponibilidad de stock, etc.).

    Características:
    - Sin autenticación (endpoint público con AllowAny)
    - Solo acepta método POST
    - Siempre retorna 200 OK para confirmar recepción a Keepa

    Payload esperado:
    {
        "asin": "B00M0QVG3W",
        "domain": 1,
        "type": "PRICE_DROP",
        "currentPrice": 1299,
        "timestamp": 123456789,
        ...
    }
    """

    # Permitir acceso sin autenticación (endpoint público)
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Procesa notificaciones POST de Keepa.

        1. Parsea el payload JSON (request.data ya viene parseado por DRF)
        2. Extrae ASIN, marketplace y tipo de evento
        3. Busca el StoreProduct asociado
        4. Crea registro de KeepaNotification
        5. Actualiza timestamp de última notificación en el producto
        6. Retorna 200 OK

        Args:
            request: Request de DRF con el payload JSON en request.data

        Returns:
            Response con {"status": "ok"} y status code 200
        """
        # DRF ya parsea el JSON automáticamente en request.data
        payload = request.data if isinstance(request.data, dict) else {}

        # Extraer campos del payload (con nombres alternativos para compatibilidad)
        asin = (payload.get('asin') or payload.get('ASIN') or '').strip().upper()
        domain = payload.get('domain') or payload.get('domainId') or payload.get('marketplace')
        event_type = payload.get('type') or payload.get('eventType') or ''

        # Buscar producto asociado al ASIN
        store_product = None
        if asin:
            store_product = StoreProduct.objects.filter(asin=asin).first()

        # Crear registro de notificación
        KeepaNotification.objects.create(
            store_product=store_product,
            asin=asin,
            marketplace=str(domain or ''),
            event_type=str(event_type),
            message='',
            payload=payload,
        )

        # Actualizar timestamp de última notificación en el producto
        if store_product:
            store_product.last_keepa_notification_at = timezone.now()
            store_product.save(update_fields=['last_keepa_notification_at'])

        # Siempre retornar 200 OK para que Keepa marque como entregado
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)
