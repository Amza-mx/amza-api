# Keepa Tracking Service - Guía de Implementación

## Cambios Realizados

### Problemas Corregidos

1. **Campo `updateInterval` faltante**: Ahora se incluye SIEMPRE (requerido por la API de Keepa)
2. **Campo `trackingListName` eliminado**: No es parte del objeto de creación según la documentación
3. **Criterios de tracking agregados**: Se añadieron `thresholdValues` o `notifyIf` para especificar qué rastrear
4. **Campo `metaData` agregado**: Para mejor identificación de trackings

### Implementación Correcta

El servicio ahora crea trackings que cumplen con la especificación completa de Keepa:

```python
service = KeepaTrackingService()
response = service.add_tracking(
    asins=['B00M0QVG3W', 'B08N5WRWNW'],
    tracking_type='regular',  # o 'marketplace'
    marketplace='US',
    update_interval_hours=1,  # Actualizar cada hora (0-25)
    threshold_value=None,     # None = rastrear cambios de stock
    csv_type=0,               # 0=Amazon price
    is_drop=True,            # True = notificar bajadas de precio
)
```

## Tipos de Tracking

### Regular Tracking
- **Costo**: 0.9 tokens por actualización por locale
- **Rastrea**:
  - Precio de Amazon
  - Precio New
  - Precio Used
  - List Price
  - Collectible
  - Refurbished
  - Lightning Deal
  - Conteos de ofertas
  - Sales Rank

### Marketplace Tracking
- **Costo**: 9 tokens por actualización por locale
- **Rastrea todo lo anterior MÁS**:
  - Warehouse Deals
  - Buy Box New & Used
  - New 3rd Party FBA & FBM
  - Rating
  - Prime Exclusive
  - Review Counts
  - Todas las condiciones Used y Collectible con costos de envío
  - Primeras 20 ofertas del producto

## Parámetros Importantes

### `updateInterval`
- **Rango**: 0-25 horas
- **Significado**: Frecuencia de actualización
  - `1` = actualizar ~24 veces al día (cada hora)
  - `12` = actualizar ~2 veces al día
  - `0` = actualizar lo más frecuente posible
- **Impacto**: Reduce tu token refill rate

### `threshold_value`
- **Unidad**: Centavos (smallest currency unit)
- **Ejemplo**: `2000` = $20.00 USD
- **Uso**: Si se especifica, notifica cuando el precio cruza este umbral
- **None**: Rastrea cambios de disponibilidad (stock)

### `csv_type` (Tipo de Precio)
Según el campo `csv` del Product Object:
- `0` = AMAZON (precio de Amazon)
- `1` = NEW (precio de ofertas nuevas)
- `2` = USED (precio de ofertas usadas)
- `3` = SALES_RANK
- `4` = LISTPRICE
- `5` = COLLECTIBLE
- `6` = REFURBISHED
- `7` = NEW_FBM_SHIPPING
- `8` = LIGHTNING_DEAL
- etc.

### `is_drop`
- `True`: Notificar cuando el precio **baja** por debajo del threshold
- `False`: Notificar cuando el precio **sube** por encima del threshold

### `notifyIf` Types
Cuando `threshold_value=None`, se usa `notifyIf`:
- `0`: OUT_OF_STOCK - Notificar cuando se agota
- `1`: BACK_IN_STOCK - Notificar cuando vuelve a estar disponible

## Ejemplo de Uso Completo

### Rastrear bajadas de precio en Amazon.com

```python
from apps.store_products.services.keepa_tracking_service import KeepaTrackingService

service = KeepaTrackingService()

# Configurar webhook (solo una vez)
webhook_url = 'https://tu-dominio.com/api/v1/webhooks/keepa'
service.set_webhook(webhook_url)

# Añadir tracking: notificar si el precio de Amazon baja a menos de $15.00
response = service.add_tracking(
    asins=['B00M0QVG3W'],
    tracking_type='regular',
    marketplace='US',
    update_interval_hours=1,
    threshold_value=1500,  # $15.00 en centavos
    csv_type=0,           # Precio de Amazon
    is_drop=True,         # Notificar bajadas
)

# La respuesta incluye:
# - trackings: array con los objetos de tracking creados
# - error: mensaje de error si algo falló
print(response)
```

### Rastrear disponibilidad (stock)

```python
# Notificar cuando el producto vuelva a estar disponible
response = service.add_tracking(
    asins=['B00M0QVG3W'],
    tracking_type='regular',
    marketplace='US',
    update_interval_hours=2,  # Revisar cada 2 horas
    threshold_value=None,     # Sin umbral de precio
    csv_type=0,
    is_drop=True,             # No usado cuando threshold_value=None
)
```

### Batch Tracking (Múltiples ASINs)

```python
asins = ['B00M0QVG3W', 'B08N5WRWNW', 'B07XYZ1234']

response = service.add_tracking(
    asins=asins,
    tracking_type='marketplace',  # Tracking más detallado
    marketplace='US',
    update_interval_hours=1,
)

# Extraer tracking IDs
trackings = response.get('trackings', [])
for tracking in trackings:
    asin = tracking.get('asin')
    tracking_id = tracking.get('trackingId')
    print(f'{asin}: {tracking_id}')
```

## Gestión de Trackings

### Verificar un Tracking

```python
response = service.get_tracking('B00M0QVG3W')
trackings = response.get('trackings', [])
if trackings:
    print('Tracking activo:', trackings[0])
else:
    print('No hay tracking para este ASIN')
```

### Usar Named Lists

```python
# Separar trackings por cliente o propósito
response = service.add_tracking(
    asins=['B00M0QVG3W'],
    tracking_type='regular',
    marketplace='US',
    update_interval_hours=1,
    list_name='cliente_123',  # Lista nombrada
)

# Consultar tracking en lista específica
response = service.get_tracking('B00M0QVG3W', list_name='cliente_123')
```

## Notificaciones Webhook

Cuando se dispara una notificación, Keepa hace un POST a tu webhook URL:

```json
{
  "asin": "B00M0QVG3W",
  "domain": 1,
  "type": "PRICE_DROP",
  "timestamp": 123456789,
  "newPrice": 1299,
  "oldPrice": 1599
}
```

Tu endpoint debe:
1. Responder con status code `200` para confirmar recepción
2. Si falla, Keepa reintentará después de 15 segundos
3. Content-Type es `application/json` (NO `application/x-www-form-urlencoded`)

## Costos y Límites

### Token Flow Reduction

Cada tracking reduce tu token refill rate:
- **Regular**: 0.9 tokens × updates/hora
- **Marketplace**: 9 tokens × updates/hora

**Ejemplo**:
- 2000 Regular Trackings con `updateInterval=1`:
  - 2000 × 0.9 tokens/hora = 1800 tokens/hora = 30 tokens/minuto
  - Tu refill rate se reduce en 30 tokens/minuto

### Límites
- Cuando tu refill rate llega a 0, no puedes añadir más trackings ni hacer requests
- El `tokenFlowReduction` se actualiza cada 5 minutos
- Si tu API se termina, los trackings se desactivan después de 7 días

## Troubleshooting

### Error: "Missing required field: updateInterval"
- Asegúrate de pasar `update_interval_hours` al llamar `add_tracking()`

### Error: "Invalid tracking criteria"
- Debes especificar `threshold_value` O dejar que el código use `notifyIf`
- No se puede rastrear sin criterios

### Webhook no recibe notificaciones
1. Verifica que el webhook esté configurado: `service.set_webhook(url)`
2. Asegúrate que tu endpoint responda con status 200
3. Revisa que `notificationType[5] = True` (API notifications)

### Tracking no se crea
1. Revisa que tengas suficientes tokens disponibles
2. Verifica que el ASIN sea válido para el marketplace especificado
3. Consulta los logs de error en la respuesta de la API

## Referencias

- [Keepa Tracking Documentation](https://keepa.com/#!discuss/t/tracking-products/2066)
- [Tracking Creation Object](https://keepa.com/#!discuss/t/tracking-creation-object/2068)
