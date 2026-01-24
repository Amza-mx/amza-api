# Amza API

Sistema de gestión de operaciones e-commerce para múltiples marketplaces (Amazon, WooCommerce) construido con Django REST Framework. Maneja órdenes de venta, órdenes de compra, inventario, almacenes, logística de envíos y análisis de precios con soporte multi-moneda.

## 🚀 Características Principales

- **Gestión Multi-Marketplace**: Integración con Amazon y WooCommerce
- **Órdenes de Venta y Compra**: Flujo completo desde la orden del cliente hasta la compra al proveedor
- **Inventario y Almacenes**: Control de stock con sistema de moneda personalizada (WHC)
- **Análisis de Precios**: Sistema automatizado de análisis de viabilidad con integración a Keepa API
- **Centros de Preparación**: Gestión de fulfillment centers
- **Logística de Envíos**: Tracking de envíos con múltiples couriers
- **Multi-Moneda**: Soporte para USD, MXN y WHC con tipos de cambio configurables
- **API RESTful**: Endpoints completos con autenticación JWT
- **Panel de Administración**: Interface administrativa personalizada

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.10+**
- **pip** (gestor de paquetes de Python)
- **Git**
- **SQLite** (incluido con Python) o **PostgreSQL** (para producción)

## 🔧 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Amza-mx/amza-api.git
cd amza-api
```

### 2. Crear y Activar Entorno Virtual

#### En Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

#### En Linux/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependencias

#### Para Desarrollo:
```bash
pip install -r etc/requirements/dev.txt
```

#### Para Producción:
```bash
pip install -r etc/requirements/prod.txt
```

#### Nota sobre Base de Datos

El proyecto soporta dos configuraciones de base de datos según el entorno:

**Entorno de Desarrollo (SQLite - por defecto):**
- No requiere configuración adicional
- Se crea automáticamente en `src/db.sqlite3`
- Ideal para desarrollo local y pruebas

**Entorno de Producción (PostgreSQL):**
```bash
# 1. Instalar dependencias de producción
pip install -r etc/requirements/prod.txt

# 2. Configurar DATABASE_URL en el archivo .env
DATABASE_URL=postgresql://usuario:contraseña@host:5432/nombre_bd

# Ejemplo con SSL (recomendado para producción):
DATABASE_URL=postgresql://amza_user:password123@db.example.com:5432/amza_db?sslmode=require
```

El sistema detecta automáticamente qué base de datos usar según la presencia de la variable `DATABASE_URL`.

**Migración de Datos (SQLite a PostgreSQL):**
```bash
# 1. Exportar datos desde SQLite
python src/manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > datadump.json

# 2. Configurar DATABASE_URL para PostgreSQL en .env

# 3. Ejecutar migraciones en PostgreSQL
python src/manage.py migrate

# 4. Importar datos
python src/manage.py loaddata datadump.json
```

### 4. Configurar Variables de Entorno

Copia el archivo de ejemplo y configúralo con tus credenciales:

```bash
cp src/core/.env.example src/core/.env
```

Edita `src/core/.env` y configura las siguientes variables:

```env
# Django Settings
SECRET_KEY=tu_secret_key_aqui_muy_segura
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
# Desarrollo: Dejar comentado para usar SQLite (por defecto)
# Producción: Descomentar y configurar PostgreSQL
# DATABASE_URL=postgresql://username:password@host:port/database_name

# Open Exchange Rates API (para tipos de cambio)
OPEN_EXCHANGE_RATES_APP_ID=tu_api_key_aqui

# Keepa API (para análisis de precios)
KEEPA_API_KEY=tu_keepa_api_key_aqui
KEEPA_DAILY_TOKEN_LIMIT=5000
```

> **Nota**: Genera un SECRET_KEY seguro usando:
> ```bash
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

### 5. Ejecutar Migraciones

```bash
python src/manage.py migrate
```

### 6. Cargar Datos Geográficos (Opcional)

Si necesitas datos de ciudades y países (USA y MX):

```bash
python src/manage.py cities_light
```

> **Nota**: Este comando puede tomar varios minutos la primera vez.

### 7. Crear Superusuario

```bash
python src/manage.py createsuperuser
```

Sigue las instrucciones en pantalla para crear tu usuario administrador.

## ▶️ Ejecutar el Proyecto

### Servidor de Desarrollo

```bash
python src/manage.py runserver
```

El servidor estará disponible en: `http://127.0.0.1:8000/`

### Acceder al Panel de Administración

Navega a: `http://127.0.0.1:8000/admin/`

Usa las credenciales del superusuario que creaste.

### Acceder a la API

La API está disponible en: `http://127.0.0.1:8000/api/v1/`

Documentación interactiva (Swagger): `http://127.0.0.1:8000/api/schema/swagger-ui/`

## 🧪 Testing

### Ejecutar Todos los Tests

```bash
python src/manage.py test
```

### Ejecutar Tests de una App Específica

```bash
python src/manage.py test apps.products
python src/manage.py test apps.sales_orders
python src/manage.py test apps.pricing_analysis
```

### Ejecutar un Test Específico

```bash
python src/manage.py test apps.products.tests.ProductTestCase
```

## 📁 Estructura del Proyecto

```
amza-api/
├── etc/
│   └── requirements/          # Archivos de dependencias
│       ├── base.txt          # Dependencias base
│       ├── dev.txt           # Dependencias de desarrollo
│       └── prod.txt          # Dependencias de producción
├── src/
│   ├── manage.py             # Script de gestión de Django
│   ├── core/                 # Configuración del proyecto
│   │   ├── settings.py       # Settings de Django
│   │   ├── urls.py          # URLs principales
│   │   └── .env             # Variables de entorno (no en git)
│   ├── base/                 # Clases base y utilidades compartidas
│   ├── apps/                 # Aplicaciones Django
│   │   ├── users/           # Gestión de usuarios
│   │   ├── products/        # Catálogo de productos
│   │   ├── marketplaces/    # Plataformas de venta
│   │   ├── sellers/         # Proveedores
│   │   ├── warehouses/      # Almacenes
│   │   ├── prep_centers/    # Centros de preparación
│   │   ├── sales_orders/    # Órdenes de venta
│   │   ├── purchases_orders/# Órdenes de compra
│   │   └── pricing_analysis/# Análisis de precios
│   ├── api/                 # Capa de API REST
│   │   └── v1/             # API versión 1
│   ├── static/             # Archivos estáticos
│   └── templates/          # Templates HTML
├── .gitignore
├── .pre-commit-config.yaml  # Configuración de pre-commit hooks
├── pyproject.toml           # Configuración de herramientas
├── CLAUDE.md               # Guía para Claude Code
└── README.md               # Este archivo
```

## 🔑 Autenticación API

La API usa JWT (JSON Web Tokens) para autenticación.

### 1. Obtener Token

```bash
POST /api/v1/auth/jwt/token/
Content-Type: application/json

{
  "username": "tu_usuario",
  "password": "tu_password"
}
```

**Respuesta:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. Usar el Token

Incluye el token en el header de tus requests:

```bash
GET /api/v1/products/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### 3. Refrescar el Token

```bash
POST /api/v1/auth/jwt/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## 📊 Módulos Principales

### 1. Gestión de Productos
- Catálogo completo con SKU, títulos, descripciones
- Control de inventario con cantidades
- Precios multi-moneda
- Integración con marketplaces

### 2. Órdenes de Venta
- Órdenes desde marketplaces
- Detalles de líneas de productos
- Estados de orden configurables
- Tracking de envíos

### 3. Órdenes de Compra
- Órdenes a proveedores
- Relación 1-1 con órdenes de venta
- Costos de logística
- Estados de compra

### 4. Análisis de Precios (Pricing Analysis)
- Integración con Keepa API
- Cálculo automático de Break Even
- Análisis de viabilidad
- Comparación de precios USA vs MX
- Sistema de retenciones fiscales (IVA, ISR)
- Análisis en batch

**Documentación completa**: [src/apps/pricing_analysis/README.md](src/apps/pricing_analysis/README.md)

### 5. Almacenes
- Gestión de múltiples almacenes
- Moneda personalizada WHC (Warehouse Currency)
- Control de ubicaciones

### 6. Centros de Preparación
- Gestión de fulfillment centers
- Asignación de órdenes
- Estados de preparación

## 🛠️ Comandos Útiles

### Django Management

```bash
# Crear nuevas migraciones
python src/manage.py makemigrations

# Aplicar migraciones
python src/manage.py migrate

# Crear superusuario
python src/manage.py createsuperuser

# Shell interactivo con modelos cargados
python src/manage.py shell_plus

# Ver todas las URLs del proyecto
python src/manage.py show_urls

# Colectar archivos estáticos (producción)
python src/manage.py collectstatic
```

### Code Quality

```bash
# Formatear código con Ruff
ruff format src/

# Linter con Ruff
ruff check src/

# Ejecutar pre-commit hooks manualmente
pre-commit run --all-files
```

### Base de Datos

```bash
# Crear backup de la base de datos (SQLite)
cp src/db.sqlite3 src/db.sqlite3.backup

# Resetear base de datos (¡CUIDADO! Borra todos los datos)
rm src/db.sqlite3
python src/manage.py migrate
python src/manage.py createsuperuser
```

## 🌐 Endpoints Principales de la API

### Autenticación
- `POST /api/v1/auth/jwt/token/` - Obtener tokens
- `POST /api/v1/auth/jwt/token/refresh/` - Refrescar token
- `POST /api/v1/auth/jwt/token/verify/` - Verificar token

### Productos
- `GET /api/v1/products/` - Listar productos
- `POST /api/v1/products/` - Crear producto
- `GET /api/v1/products/{id}/` - Detalle de producto
- `PUT /api/v1/products/{id}/` - Actualizar producto
- `DELETE /api/v1/products/{id}/` - Eliminar producto

### Marketplaces
- `GET /api/v1/marketplaces/` - Listar marketplaces
- `GET /api/v1/marketplaces/{id}/` - Detalle de marketplace

### Órdenes de Venta
- `GET /api/v1/sales-orders/` - Listar órdenes
- `POST /api/v1/sales-orders/` - Crear orden
- `GET /api/v1/sales-orders/{id}/` - Detalle de orden

### Análisis de Precios
- `POST /api/v1/pricing-analysis/analyze-asin/` - Analizar un ASIN
- `POST /api/v1/pricing-analysis/analyze-bulk/` - Análisis en batch
- `GET /api/v1/pricing-analysis/feasible/` - Productos viables
- `POST /api/v1/pricing-analysis/{id}/refresh/` - Refrescar análisis

### Documentación Completa
- `GET /api/schema/swagger-ui/` - Swagger UI
- `GET /api/schema/redoc/` - ReDoc

## 🐛 Troubleshooting

### Error: "No module named 'core'"

Asegúrate de estar ejecutando los comandos desde la raíz del proyecto y que el path sea correcto:

```bash
python src/manage.py runserver
```

### Error: "django.core.exceptions.ImproperlyConfigured"

Verifica que tu archivo `.env` esté correctamente configurado en `src/core/.env`.

### Error de Migraciones

Intenta:

```bash
python src/manage.py makemigrations
python src/manage.py migrate --run-syncdb
```

### Base de Datos Bloqueada (SQLite)

Si estás en desarrollo, cierra todos los procesos que puedan estar usando la BD y reinicia el servidor.

## 📝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'feat: add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Convenciones de Commits

Usamos Conventional Commits:

- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de bugs
- `docs:` - Cambios en documentación
- `refactor:` - Refactorización de código
- `test:` - Añadir o modificar tests
- `chore:` - Cambios en build, configuración, etc.

## 📄 Licencia

Este proyecto es propiedad de Amza MX.

## 🚀 Despliegue en Railway

### Requisitos Previos

1. Cuenta en [Railway](https://railway.app/)
2. Repositorio Git con el código
3. API keys configuradas (Open Exchange Rates, Keepa)

### Pasos para Desplegar

#### 1. Crear Proyecto en Railway

1. Accede a [Railway Dashboard](https://railway.app/dashboard)
2. Click en "New Project"
3. Selecciona "Deploy from GitHub repo"
4. Autoriza Railway para acceder a tu repositorio
5. Selecciona el repositorio `amza-api`

#### 2. Agregar Base de Datos PostgreSQL

1. En tu proyecto Railway, click en "New"
2. Selecciona "Database" → "Add PostgreSQL"
3. Railway creará automáticamente la base de datos y configurará `DATABASE_URL`

#### 3. Configurar Variables de Entorno

En la pestaña "Variables" del servicio, agrega:

```env
DEBUG=false
SECRET_KEY=<genera-una-clave-segura>
ALLOWED_HOSTS=<tu-app>.up.railway.app
OPEN_EXCHANGE_RATES_APP_ID=<tu-api-key>
KEEPA_API_KEY=<tu-api-key>
CURRENCIES='USD,MXN'
```

**Generar SECRET_KEY seguro:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### 4. Despliegue Automático

Railway detecta automáticamente el `Dockerfile` y despliega:
- ✅ Instala dependencias de producción
- ✅ Ejecuta migraciones de base de datos
- ✅ Recolecta archivos estáticos
- ✅ Inicia servidor Gunicorn

#### 5. Crear Superusuario

Desde el Railway Dashboard:
1. Ve a tu servicio desplegado
2. Click en "Shell" o "Terminal"
3. Ejecuta:
```bash
python src/manage.py createsuperuser
```

#### 6. Verificar Despliegue

- Admin: `https://<tu-app>.up.railway.app/admin/`
- API: `https://<tu-app>.up.railway.app/api/v1/`

### Actualizaciones

Railway redespliega automáticamente cuando haces push a la rama principal:

```bash
git add .
git commit -m "Update feature"
git push origin main
# Railway despliega automáticamente
```

### Solución de Problemas

**Error en migraciones:**
- Revisa logs en Railway Dashboard
- Verifica que `DATABASE_URL` esté configurado
- Asegúrate que PostgreSQL esté corriendo

**Error 502/503:**
- Verifica que `ALLOWED_HOSTS` incluya tu dominio de Railway
- Revisa logs de Gunicorn en Dashboard
- Confirma que el puerto 8000 esté expuesto

**Archivos estáticos no se cargan:**
- Verifica que WhiteNoise esté en MIDDLEWARE (settings.py)
- Confirma que `collectstatic` se ejecutó (revisa logs de despliegue)

## 🤝 Soporte

Para preguntas o soporte:
- Revisa la documentación en `/docs`
- Abre un issue en el repositorio
- Contacta al equipo de desarrollo

## 🔗 Enlaces Útiles

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Keepa API Documentation](https://keepa.com/#!api)
- [Open Exchange Rates API](https://openexchangerates.org/)

---

**Desarrollado con ❤️ por el equipo de Amza MX**
