"""
Webhooks API Views

Este módulo contiene las vistas para recibir webhooks de servicios externos.
"""

import json

from django.http import JsonResponse, HttpResponseNotAllowed
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from apps.store_products.models import StoreProduct, KeepaNotification


@method_decorator(csrf_exempt, name='dispatch')
class KeepaWebhookView(View):
    """
    Vista para recibir notificaciones push de Keepa API.

    Este endpoint recibe notificaciones cuando se disparan eventos de tracking
    configurados en Keepa (cambios de precio, disponibilidad de stock, etc.).

    Características:
    - Sin autenticación (endpoint público)
    - Sin protección CSRF (requerido para webhooks externos)
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

    def post(self, request, *args, **kwargs):
        """
        Procesa notificaciones POST de Keepa.

        1. Parsea el payload JSON
        2. Extrae ASIN, marketplace y tipo de evento
        3. Busca el StoreProduct asociado
        4. Crea registro de KeepaNotification
        5. Actualiza timestamp de última notificación en el producto
        6. Retorna 200 OK

        Args:
            request: HttpRequest con el payload JSON en el body

        Returns:
            JsonResponse con {"status": "ok"} y status code 200
        """
        # Parse JSON payload
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Si el payload no es JSON válido, usar diccionario vacío
            payload = {}

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
            payload=payload if isinstance(payload, dict) else {},
        )

        # Actualizar timestamp de última notificación en el producto
        if store_product:
            store_product.last_keepa_notification_at = timezone.now()
            store_product.save(update_fields=['last_keepa_notification_at'])

        # Siempre retornar 200 OK para que Keepa marque como entregado
        return JsonResponse({'status': 'ok'})

    def http_method_not_allowed(self, request, *args, **kwargs):
        """
        Maneja métodos HTTP no permitidos.

        Solo POST está permitido para este webhook.

        Returns:
            HttpResponseNotAllowed con la lista de métodos permitidos
        """
        return HttpResponseNotAllowed(['POST'])
