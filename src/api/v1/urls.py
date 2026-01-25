from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.v1.marketplaces.urls import router as marketplace_router
from api.v1.sales_orders.urls import router as sales_order_router
from api.v1.prep_centers.urls import router as prep_center_router
from api.v1.auth.urls import router as auth_router
from api.v1.products.urls import router as product_router
from api.v1.pricing_analysis.urls import router as pricing_router

# Main Router of the API
router = DefaultRouter()

# Sub Routers
router.registry.extend(marketplace_router.registry)
router.registry.extend(sales_order_router.registry)
router.registry.extend(prep_center_router.registry)
router.registry.extend(auth_router.registry)
router.registry.extend(product_router.registry)
router.registry.extend(pricing_router.registry)

# Main URL Pattern for the API
urlpatterns = [
    path('', include(router.urls)),
    path('', include('api.v1.healthcheck.urls')),
    path('', include('apps.store_products.api_urls')),
]
