# Webhooks API

Este módulo maneja webhooks de servicios externos que envían notificaciones push a la API.

## Endpoints Disponibles

### Keepa Webhook

**URL**: `POST /api/v1/webhooks/keepa`

Recibe notificaciones push de Keepa API cuando se disparan eventos de tracking configurados (cambios de precio, disponibilidad de stock, etc.).

#### Características

- **Sin Autenticación**: El endpoint es público (`permission_classes = [AllowAny]`)
- **Django REST Framework**: Usa `APIView` de DRF
- **Método**: Solo acepta `POST`
- **Content-Type**: `application/json`
- **Respuesta**: Siempre retorna `200 OK` con `{"status": "ok"}`

#### Payload Esperado

```json
{
  "asin": "B00M0QVG3W",
  "domain": 1,
  "domainId": 1,
  "type": "PRICE_DROP",
  "csvType": 0,
  "timestamp": 123456789,
  "currentPrice": 1299,
  "desiredPrice": 1500,
  "notifyIfType": null,
  "trackingId": 12345678
}
```

#### Campos del Payload

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `asin` | string | ASIN del producto de Amazon |
| `domain` o `domainId` | int | ID del marketplace (1=USA, 3=Alemania, etc.) |
| `type` o `eventType` | string | Tipo de evento (PRICE_DROP, BACK_IN_STOCK, etc.) |
| `trackingId` | int | ID del tracking que disparó la notificación |
| `timestamp` | int | Timestamp en formato KeepaTime (minutos) |
| `currentPrice` | int | Precio actual en centavos |
| `desiredPrice` | int | Precio umbral configurado |

#### Procesamiento

Cuando se recibe una notificación:

1. Parsea el payload JSON
2. Extrae ASIN, marketplace y tipo de evento
3. Busca el `StoreProduct` asociado al ASIN
4. Crea un registro `KeepaNotification` en la base de datos
5. Si existe el producto, actualiza `last_keepa_notification_at`
6. Retorna `200 OK`

#### Ejemplo de Uso

**Configurar el webhook en Keepa:**
```bash
python src/manage.py setup_keepa_webhook https://tu-dominio.com/api/v1/webhooks/keepa
```

**Probar manualmente:**
```bash
curl -X POST https://tu-dominio.com/api/v1/webhooks/keepa \
  -H "Content-Type: application/json" \
  -d '{
    "asin": "B00TEST123",
    "domain": 1,
    "type": "PRICE_DROP",
    "timestamp": 123456789,
    "currentPrice": 1299
  }'
```

**Respuesta esperada:**
```json
{
  "status": "ok"
}
```

## Seguridad

### Consideraciones de Seguridad

⚠️ **Importante**: El webhook de Keepa es público y no requiere autenticación porque:

1. Keepa no soporta autenticación en webhooks
2. La URL del webhook es la única "credencial"
3. Los datos recibidos son informativos y no modifican datos críticos directamente

**Implementación de Seguridad:**
- Usa `permission_classes = [AllowAny]` de DRF para permitir acceso público
- Bypasa el middleware de autenticación JWT del proyecto
- DRF maneja automáticamente el parseo seguro del JSON

### Recomendaciones

- **HTTPS Obligatorio**: La URL del webhook debe usar HTTPS
- **Validación de Payload**: DRF valida y parsea el JSON automáticamente en `request.data`
- **Logging**: Todas las notificaciones se registran en la base de datos
- **Manejo de Errores**: DRF maneja errores de parseo de forma segura sin exponer información sensible

## Monitoreo

### Verificar Notificaciones Recibidas

En Django admin:
1. Ir a `/admin/store_products/keepanotification/`
2. Ver lista de notificaciones ordenadas por fecha

En shell de Django:
```python
from apps.store_products.models import KeepaNotification

# Últimas 10 notificaciones
notifications = KeepaNotification.objects.order_by('-created_at')[:10]
for n in notifications:
    print(f"{n.created_at}: {n.asin} - {n.event_type}")
```

### Logs

En desarrollo:
```bash
python src/manage.py runserver
# Verás: "POST /api/v1/webhooks/keepa" en la consola
```

En producción (Railway):
- Revisar logs en Railway Dashboard
- Buscar: `POST /api/v1/webhooks/keepa`

## Troubleshooting

### El webhook no recibe notificaciones

**Posibles causas:**

1. **URL no configurada en Keepa**
   ```bash
   python src/manage.py setup_keepa_webhook https://tu-dominio.com/api/v1/webhooks/keepa
   ```

2. **URL no es accesible públicamente**
   - Verificar que sea HTTPS
   - Probar acceso desde dispositivo externo
   - En desarrollo local, usar ngrok

3. **Tracking no configurado correctamente**
   - Verificar que `notificationType[5] = True` (API notifications)

### Error 405 Method Not Allowed

El endpoint solo acepta `POST`. Verificar que estás usando el método correcto.

### Error 500 Internal Server Error

Revisar logs del servidor para ver el error específico. Causas comunes:
- Payload JSON malformado
- Error en base de datos
- Error en procesamiento del payload

## Desarrollo Local

Para probar webhooks en desarrollo local, usa ngrok:

```bash
# Terminal 1: Iniciar Django
python src/manage.py runserver

# Terminal 2: Iniciar ngrok
ngrok http 8000

# Terminal 3: Configurar webhook con URL de ngrok
python src/manage.py setup_keepa_webhook https://abc123.ngrok.io/api/v1/webhooks/keepa
```

⚠️ **Nota**: Cada vez que reinicias ngrok, la URL cambia y debes reconfigurar el webhook.

## Agregar Nuevos Webhooks

Para agregar un nuevo webhook de otro servicio:

1. Crear la vista en el app correspondiente
2. Agregar la ruta en `api/v1/webhooks/urls.py`:
   ```python
   path('nombre-servicio', nombre_webhook_view, name='nombre-servicio'),
   ```
3. Documentar el endpoint en este README

## Referencias

- [Documentación de Keepa Tracking](https://keepa.com/#!discuss/t/tracking-products/2066)
- [Guía de configuración del webhook](../../apps/store_products/WEBHOOK_SETUP.md)
- [Implementación del webhook](../../apps/store_products/views.py)
