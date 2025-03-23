from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.v1.marketplaces.urls import router as marketplace_router
from api.v1.sales_orders.urls import router as sales_order_router
from api.v1.prep_centers.urls import router as prep_center_router
from api.v1.auth.urls import router as auth_router

# Create the main router
router = DefaultRouter()

# Include all sub-routers
router.registry.extend(marketplace_router.registry)
router.registry.extend(sales_order_router.registry)
router.registry.extend(prep_center_router.registry)
router.registry.extend(auth_router.registry)

urlpatterns = [
    path('v1/', include(router.urls)),
]
