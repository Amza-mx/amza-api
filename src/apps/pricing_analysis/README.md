# Pricing Analysis - Sistema de Análisis de Precios con Keepa

Sistema automatizado que analiza la viabilidad de vender productos en Amazon MX basándose en datos de Keepa (USA y MX), calculando el Break Even con costos de importación, retenciones fiscales y fees de Amazon.

## Tabla de Contenidos

- [Resumen](#resumen)
- [Fórmula del Break Even](#fórmula-del-break-even)
- [Instalación](#instalación)
- [Configuración Inicial](#configuración-inicial)
- [Uso de la API](#uso-de-la-api)
- [Modelos](#modelos)
- [Administración Django](#administración-django)
- [Tests](#tests)

## Resumen

**Input**: Lista de ASINs de productos Amazon

**Output**: Análisis de viabilidad con:
- Break Even calculado
- Precio recomendado con margen objetivo
- Comparativa con precio actual en Amazon MX
- Notas y recomendaciones

## Fórmula del Break Even

El cálculo del Break Even se realiza en los siguientes pasos:

### Paso 1: Convertir costo USA a MXN con impuestos americanos
```
USA_Cost_MXN = USA_Cost_USD * Exchange_Rate * 1.0825
```
- `1.0825` = 8.25% impuestos americanos

### Paso 2: Calcular fees de importación
```
Import_Fees = USA_Cost_MXN * 0.20
```
- `0.20` = 20% costos administrativos de importación

### Paso 3: Calcular IVA sobre los fees de importación
```
IVA_Import_Fees = Import_Fees * 0.16
```
- `0.16` = 16% IVA

### Paso 4: Calcular costo base total
```
Cost_Base = USA_Cost_MXN + Import_Fees + IVA_Import_Fees
```

### Paso 5: Sumar costos de envío
```
Total_Costs = Cost_Base + Shipping_Cost_MXN
```
- `Shipping_Cost_MXN` = $70-$100 MXN (configurable)

### Paso 6: Calcular Break Even base (con fee de marketplace)
```
Break_Even_Base = Total_Costs / (1 - 0.15)
```
- `0.15` = 15% fee de Amazon

### Paso 7: Calcular retenciones fiscales
```
Cost_Base_Without_VAT = Cost_MX / 1.16
VAT_Retention = Cost_Base_Without_VAT * 0.08
ISR_Retention = Cost_Base_Without_VAT * 0.025
```
- `Cost_MX` = Precio de venta del producto (puede ser el precio de Amazon MX u otro precio establecido)
- `0.08` = 8% retención IVA
- `0.025` = 2.5% retención ISR

### Paso 8: Break Even Final
```
Break_Even_Final = Break_Even_Base + VAT_Retention + ISR_Retention
```

### Ejemplo Numérico

Para un producto con:
- USA Cost (Precio de Compra): $50.00 USD
- Exchange Rate: 20.00 MXN/USD
- Shipping: $85.00 MXN
- Cost MX (Precio de Venta): $1,500.00 MXN

```
1. USA_Cost_MXN = $50.00 * 20.00 * 1.0825 = $1,082.50 MXN
2. Import_Fees = $1,082.50 * 0.20 = $216.50 MXN
3. IVA_Import_Fees = $216.50 * 0.16 = $34.64 MXN
4. Cost_Base = $1,082.50 + $216.50 + $34.64 = $1,333.64 MXN
5. Total_Costs = $1,333.64 + $85.00 = $1,418.64 MXN
6. Break_Even_Base = $1,418.64 / 0.85 = $1,668.99 MXN
7. VAT_Retention = ($1,500.00 / 1.16) * 0.08 = $103.45 MXN
   ISR_Retention = ($1,500.00 / 1.16) * 0.025 = $32.33 MXN
8. Break_Even_Final = $1,668.99 + $103.45 + $32.33 = $1,804.77 MXN
```

### Notas Importantes sobre los Valores

- **USA_Cost_USD**: Es el **precio de compra del producto** en USA. Se obtiene de Keepa API y representa el costo al que se puede adquirir el producto.

- **Cost_MX**: Es el **precio de venta del producto** en México. Este valor puede ser:
  - El precio actual en Amazon MX (obtenido de Keepa)
  - Un precio personalizado establecido por el vendedor
  - Un precio objetivo para el análisis

  El sistema utiliza este valor para calcular las retenciones fiscales (IVA e ISR) que se aplican sobre el precio de venta.

## Instalación

### 1. La app ya está instalada (se hizo durante implementación)

La app `pricing_analysis` ya está agregada a `INSTALLED_APPS` en `settings.py`.

### 2. Instalar dependencias

```bash
pip install -r etc/requirements/base.txt
```

Esto instalará `keepa==1.3.7` y todas sus dependencias.

### 3. Ejecutar migraciones (ya ejecutadas)

```bash
python src/manage.py migrate
```

## Configuración Inicial

### 1. Configurar Keepa API Key

Agregar a tu archivo `.env`:

```env
KEEPA_API_KEY=tu_clave_keepa_aqui
KEEPA_DAILY_TOKEN_LIMIT=5000
```

Luego, en el admin de Django (`/admin/`):

1. Ir a **Pricing Analysis > Keepa Configurations**
2. Crear nueva configuración:
   - API Key: (tu clave de Keepa)
   - Is Active: ✓ (marcado)
   - Daily Token Limit: 5000

### 2. Configurar Tipo de Cambio USD→MXN

En el admin, ir a **Pricing Analysis > Exchange Rates**:

1. Crear nuevo Exchange Rate:
   - From Currency: USD
   - To Currency: MXN
   - Rate: 20.5000 (ejemplo - ajustar según tipo de cambio actual)
   - Is Active: ✓ (marcado)
   - Source: manual

**Nota**: Solo puede haber un Exchange Rate activo USD→MXN a la vez.

### 3. Revisar Configuración de Break Even (Opcional)

La data migration creó una configuración por defecto llamada "Default Configuration" que ya está activa.

Para ajustar parámetros:

1. Ir a **Pricing Analysis > Break Even Analysis Configs**
2. Editar "Default Configuration" o crear una nueva
3. Ajustar tasas según necesidad:
   - Import Admin Cost Rate: 0.20 (20%)
   - IVA Tax Rate: 0.16 (16%)
   - VAT Retention Rate: 0.08 (8%)
   - ISR Retention Rate: 0.025 (2.5%)
   - Marketplace Fee Rate: 0.15 (15%)
   - Fixed Shipping Min/Max: 70-100 MXN
   - Min/Target Profit Margin: 10%/25%

## Uso de la API

### Autenticación

Todos los endpoints requieren autenticación JWT. Primero obtén un token:

```bash
POST /api/v1/auth/jwt/token/
{
  "username": "tu_usuario",
  "password": "tu_password"
}
```

Usa el token en headers:
```
Authorization: Bearer {tu_access_token}
```

### Endpoints Disponibles

#### 1. Analizar un ASIN

```bash
POST /api/v1/pricing-analysis/analyze-asin/
Content-Type: application/json

{
  "asin": "B07XYZ1234",
  "shipping_cost_mxn": 85  // Opcional, usa promedio de config si no se especifica
}
```

**Respuesta Exitosa (200)**:
```json
{
  "id": 1,
  "asin": "B07XYZ1234",
  "product": 15,
  "product_sku": "KEEPA-B07XYZ1234",
  "product_title": "Producto Ejemplo",
  "usa_cost": "12.50",
  "usa_cost_currency": "USD",
  "usa_cost_source": "buy_box",
  "is_available_usa": true,
  "exchange_rate": "20.1500",
  "break_even_price": "485.23",
  "break_even_price_currency": "MXN",
  "current_mx_amazon_price": "599.00",
  "current_mx_amazon_price_currency": "MXN",
  "is_feasible": true,
  "recommended_price": "646.97",
  "recommended_price_currency": "MXN",
  "potential_profit_margin": "0.1900",
  "confidence_score": "MEDIUM",
  "analysis_notes": "✓ Precio USA obtenido de: Buy Box Price ($12.50 USD)\n...",
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Caso: Producto No Disponible en USA**:
```json
{
  "is_available_usa": false,
  "is_feasible": false,
  "analysis_notes": "⚠️ Producto NO disponible en Amazon USA.\n\nRecomendación: Establecer inventory_quantity = 0..."
}
```

#### 2. Análisis en Batch (Múltiples ASINs)

```bash
POST /api/v1/pricing-analysis/analyze-bulk/
Content-Type: application/json

{
  "asins": ["B07XYZ1234", "B08ABC5678", "B09DEF9012"],
  "batch_name": "Weekly Review - Jan 2025",
  "shipping_cost_mxn": 85  // Opcional
}
```

**Respuesta (200)**:
```json
{
  "id": 5,
  "name": "Weekly Review - Jan 2025",
  "status": "COMPLETED",
  "total_asins": 3,
  "processed_asins": 3,
  "successful_analyses": 2,
  "failed_analyses": 0,
  "unavailable_in_usa_count": 1,
  "results": [1, 2, 3],  // IDs de PricingAnalysisResult
  "started_at": "2025-01-15T10:30:00Z",
  "completed_at": "2025-01-15T10:32:15Z"
}
```

#### 3. Listar Productos Viables

```bash
GET /api/v1/pricing-analysis/feasible/?min_margin=0.15
```

Retorna solo productos con `is_feasible=True` y opcionalmente filtrados por margen mínimo.

#### 4. Refrescar Análisis

```bash
POST /api/v1/pricing-analysis/{id}/refresh/
```

Re-ejecuta el análisis con datos frescos de Keepa.

#### 5. Otros Endpoints

- `GET /api/v1/pricing-analysis/` - Listar todos los análisis
- `GET /api/v1/pricing-analysis/{id}/` - Detalle de un análisis
- `GET /api/v1/pricing-analysis-batches/` - Listar batches
- `GET /api/v1/keepa-data/` - Ver datos de Keepa
- `POST /api/v1/keepa-data/sync-asin/` - Sincronizar ASIN sin análisis
- `GET /api/v1/exchange-rates/active-usd-mxn/` - Obtener tipo de cambio activo

### Códigos de Error

- `400 Bad Request`: Falta configuración (Exchange Rate o Break Even Config)
- `429 Too Many Requests`: Límite de tokens Keepa excedido
- `500 Internal Server Error`: Error en Keepa API u otro error inesperado

## Modelos

### 1. KeepaConfiguration
Almacena credenciales y tracking de tokens de Keepa API.

### 2. ExchangeRate
Tipos de cambio USD→MXN. Solo uno puede estar activo.

### 3. KeepaProductData
Datos obtenidos de Keepa API para cada ASIN/marketplace.

### 4. BreakEvenAnalysisConfig
Parámetros configurables del análisis (tasas, márgenes, shipping).

### 5. PricingAnalysisResult
Resultado de cada análisis individual.

### 6. PricingAnalysisBatch
Agrupa múltiples análisis en un batch.

### 7. KeepaAPILog
Log de todas las llamadas a Keepa API.

## Administración Django

### Visualizar Análisis

En `/admin/`, ir a **Pricing Analysis > Pricing Analysis Results**:

- Ver todos los análisis
- Filtrar por viabilidad, disponibilidad, confianza
- Ver márgenes de ganancia con colores (verde/naranja/rojo)
- Exportar reportes

### Monitorear Batches

En **Pricing Analysis > Pricing Analysis Batches**:

- Ver progreso de batches
- Revisar ASINs procesados vs total
- Identificar productos no disponibles en USA

### Keepa Data

En **Pricing Analysis > Keepa Product Data**:

- Ver datos sincronizados
- Verificar disponibilidad de productos
- Revisar errores de sincronización

## Tests

Ejecutar tests:

```bash
# Todos los tests de pricing_analysis
python src/manage.py test apps.pricing_analysis

# Solo tests de modelos
python src/manage.py test apps.pricing_analysis.tests.test_models

# Solo tests de calculator
python src/manage.py test apps.pricing_analysis.tests.test_calculator
```

## Flujo Completo de Uso

### Ejemplo: Análisis Semanal de Productos

1. **Preparar lista de ASINs** a analizar (de tu catálogo o nuevas oportunidades)

2. **Ejecutar análisis en batch**:
   ```bash
   POST /api/v1/pricing-analysis/analyze-bulk/
   {
     "asins": ["B07ABC", "B08DEF", "B09GHI"],
     "batch_name": "Week 3 - January 2025",
     "shipping_cost_mxn": 80
   }
   ```

3. **Revisar resultados viables**:
   ```bash
   GET /api/v1/pricing-analysis/feasible/?min_margin=0.15
   ```

4. **Revisar productos no disponibles en USA** (para poner stock en 0):
   ```bash
   GET /api/v1/pricing-analysis/?is_available_usa=false
   ```

5. **Ajustar inventario** basándose en análisis:
   - Productos viables → Aumentar stock
   - No viables → Reducir precio o descontinuar
   - No disponibles USA → Stock = 0

6. **Re-analizar periódicamente** para ajustar a cambios de precio

## Notas Importantes

### Auto-creación de Products

Si un ASIN no existe en la base de datos, el sistema automáticamente crea un `Product` con:
- `sku`: KEEPA-{asin}
- `external_id`: {asin}
- `title`: Obtenido de Keepa
- `inventory_quantity`: 0

### Prioridad de Precios USA

El sistema usa esta cascada para determinar el costo USA:
1. **Buy Box Price** (prioridad más alta)
2. **Current Amazon Price**
3. Si ninguno existe → Producto no disponible

### Rate Limits Keepa

- Monitorear uso de tokens en admin
- El sistema verifica disponibilidad antes de llamar
- Error 429 si se excede límite diario

### Actualización de Tipo de Cambio

Recuerda actualizar el Exchange Rate periódicamente para cálculos precisos.

## Soporte

Para problemas o preguntas:
1. Revisar logs en `/admin/pricing_analysis/keepaapilog/`
2. Verificar configuración de Keepa y Exchange Rate
3. Ejecutar tests: `python src/manage.py test apps.pricing_analysis`
