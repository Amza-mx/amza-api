# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **Amza API**, a Django REST Framework application for managing e-commerce operations across multiple marketplaces (Amazon, WooCommerce). The system handles sales orders, purchase orders, inventory, warehouses, and shipping logistics with multi-currency support.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment (if not already done)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r etc/requirements/dev.txt  # For development
pip install -r etc/requirements/prod.txt  # For production

# Set up environment variables
cp src/core/.env.example src/core/.env
# Edit src/core/.env with your configuration
```

### Database Operations
```bash
# Run from project root
python src/manage.py makemigrations
python src/manage.py migrate

# Create superuser
python src/manage.py createsuperuser

# Load geographic data (cities/countries)
python src/manage.py cities_light
```

### Running the Development Server
```bash
python src/manage.py runserver
```

### Testing
```bash
# Run all tests
python src/manage.py test

# Run tests for a specific app
python src/manage.py test apps.products
python src/manage.py test apps.sales_orders

# Run a specific test class
python src/manage.py test apps.products.tests.ProductTestCase
```

### Code Quality
```bash
# Format code with Ruff
ruff format src/

# Lint code with Ruff
ruff check src/

# Run pre-commit hooks
pre-commit run --all-files
```

### Django Extensions
```bash
# Django shell with IPython
python src/manage.py shell_plus

# Show URLs
python src/manage.py show_urls
```

## Architecture

### Project Structure
```
src/
├── manage.py              # Django management script
├── core/                  # Django project settings
│   ├── settings.py        # Main settings file
│   ├── urls.py           # Root URL configuration
│   └── .env              # Environment variables (not in git)
├── base/                  # Shared base classes and utilities
│   ├── models.py         # BaseModel with created_at/updated_at
│   ├── admin.py          # BaseAdmin for common admin functionality
│   └── choices.py        # Shared TextChoices (status, couriers, etc.)
├── apps/                  # Django applications
│   ├── users/            # Custom user model (extends AbstractUser)
│   ├── products/         # Product catalog with pricing
│   ├── marketplaces/     # E-commerce platforms (Amazon, WooCommerce)
│   ├── sellers/          # Third-party sellers/suppliers
│   ├── warehouses/       # Warehouse management with custom currency (WHC)
│   ├── prep_centers/     # Fulfillment preparation centers
│   ├── sales_orders/     # Customer orders from marketplaces
│   └── purchases_orders/ # Orders to suppliers
└── api/                   # REST API layer
    └── v1/               # API version 1
        ├── urls.py       # Main router combining all sub-routers
        ├── auth/         # JWT authentication endpoints
        ├── products/     # Product API
        ├── marketplaces/ # Marketplace API
        ├── sales_orders/ # Sales order API
        └── prep_centers/ # Prep center API
```

### Key Architectural Patterns

**Base Classes**: All models inherit from `base.models.BaseModel` which provides `created_at` and `updated_at` timestamp fields. All admin classes should inherit from `base.admin.BaseAdmin` for consistent timestamp display.

**API Structure**: The API uses Django REST Framework's `ModelViewSet` pattern with versioned URLs (`/api/v1/`). Each domain (products, sales_orders, etc.) has its own sub-router that gets combined in `api/v1/urls.py`.

**Multi-Currency System**: The project uses `django-money` (djmoney) with a custom warehouse currency (WHC) for internal tracking. Sales orders default to MXN, purchase orders to USD. Currency exchange rates are managed via Open Exchange Rates API.

**Order Flow**:
1. `SalesOrder` represents customer orders from marketplaces
2. `PurchaseOrder` is created (one-to-one with SalesOrder) to source products from sellers
3. Both have detail models (`SalesOrderDetail`, `PurchaseOrderDetail`) for line items
4. Shipments track delivery with `SalesOrderDetailShipment` and `PurchaseOrderDetailShipment`
5. `ShipmentTracking` records status updates for shipments

**Generated Fields**: Models use Django's `GeneratedField` for calculated values like `total_price` (unit_price × quantity) and `fees` (15% of total_amount). These are automatically computed and persisted in the database.

**Status Tracking**: Common status choices are defined in `base/choices.py` including:
- `SalesOrderStatusChoices` and `PurchaseOrderStatusChoices` (PENDING → BOUGHT → IN_WAREHOUSE → DELIVERY_PROCESS → DELIVERED)
- `ShipmentStatusChoices` (PENDING → DISPATCHED → IN_TRANSIT → DELIVERED)
- `CourierChoices` (DHL, UPS, FEDEX, ESTAFETA, OTHER)

### Authentication

The API uses JWT (JSON Web Tokens) via `rest_framework_simplejwt`. All endpoints require authentication by default except the auth endpoints. The custom user model is `users.User` (extends Django's `AbstractUser`).

Auth endpoints:
- `POST /api/v1/auth/jwt/token/` - Obtain token pair
- `POST /api/v1/auth/jwt/token/refresh/` - Refresh access token
- `POST /api/v1/auth/jwt/token/verify/` - Verify token validity

### Adding New API Endpoints

1. Create models in the appropriate app under `apps/`
2. Create serializers, views, and URLs in `api/v1/<domain>/`
3. Register the router in `api/v1/urls.py` by extending the main router
4. Add tests in the app's `tests.py`
5. Update `api/README.md` documentation

### Important Configuration

- **Custom User Model**: `AUTH_USER_MODEL = 'users.User'`
- **Geographic Data**: Uses `django-cities-light` with US and MX countries only
- **Admin Interface**: Accessible at `/admin/` with custom branding ("Amza API")
- **DRF Settings**: Page size is 100, authentication via JWT, uses drf-spectacular for OpenAPI schema
- **Database**: Environment-specific (SQLite for dev, PostgreSQL for production via `DATABASE_URL`)

### Database Configuration

The project supports environment-specific database backends:

**Development (SQLite - Default):**
- Automatically used when `DATABASE_URL` is not set
- No additional setup required
- Database file location: `src/db.sqlite3`
- Ideal for local development and testing

**Production (PostgreSQL):**
- Triggered by setting `DATABASE_URL` environment variable
- Format: `postgresql://username:password@host:port/database_name`
- Example: `DATABASE_URL=postgresql://amza_user:mypassword@localhost:5432/amza_db`
- For SSL: append `?sslmode=require` to the connection string
- Requirements: Install production dependencies with `pip install -r etc/requirements/prod.txt`

**Environment Detection:**
The application automatically detects which database to use based on the presence of the `DATABASE_URL` environment variable. No code changes needed to switch environments.

**Database URL Examples:**
```bash
# Local PostgreSQL
DATABASE_URL=postgresql://postgres:password@localhost:5432/amza_db

# PostgreSQL with SSL
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require

# Cloud platforms (Heroku, Railway, etc.) set this automatically
DATABASE_URL=postgresql://user:pass@ec2-xx-xx-xx-xx.compute-1.amazonaws.com:5432/dbname
```

### Deployment to Railway

**Prerequisites:**
- Railway account with PostgreSQL database provisioned
- Environment variables configured (see .env.example Railway section)
- Docker configuration files in place (Dockerfile, entrypoint.sh, railway.json)

**Deployment Process:**
Railway uses the Dockerfile for containerized deployment. The deployment process:
1. Builds Docker image using Python 3.13
2. Installs production dependencies (PostgreSQL adapter, Gunicorn, WhiteNoise, CORS headers)
3. Runs entrypoint.sh which:
   - Collects static files with WhiteNoise
   - Runs database migrations
   - Starts Gunicorn server on port 8000

**Database:**
Railway automatically provisions PostgreSQL and sets the `DATABASE_URL` environment variable. The application detects this and uses PostgreSQL instead of SQLite.

**Static Files:**
Static files are served by WhiteNoise (no separate web server needed). WhiteNoise provides compression and caching for optimal performance.

**CORS:**
CORS is enabled for API access from different origins. In development, all origins are allowed. In production, use the `CORS_ALLOWED_ORIGINS` environment variable to specify allowed frontend URLs.

**Monitoring:**
- Check deployment logs in Railway dashboard
- Health check endpoint: `/admin/login/`
- Gunicorn logs include access and error logs

**Common Commands in Railway Shell:**
```bash
# Create superuser
python src/manage.py createsuperuser

# Check database connection
python src/manage.py dbshell

# Run custom management commands
python src/manage.py <command>
```

### Code Style

- **Formatter**: Ruff with single quotes, 100 character line length, 4-space indentation
- **Pre-commit Hooks**: YAML checking, end-of-file fixing, trailing whitespace removal, large file detection
- **Import Order**: Django imports first, then third-party, then local apps

### Common Gotchas

- The `manage.py` file is in `src/` directory, not project root
- Environment variables are loaded from `src/core/.env` via `django-environ`
- When creating models, always inherit from `BaseModel` for automatic timestamps
- When creating admin classes, inherit from `BaseAdmin` to display timestamps
- The warehouse currency (WHC) is a custom currency defined in settings
- Purchase orders use USD while sales orders use MXN by default