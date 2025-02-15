from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.v1.sales_orders.views import SalesOrderViewSet

router = DefaultRouter()
router.register(r'sales-orders', SalesOrderViewSet, 'sales_order')

urlpatterns = [
    path('', include(router.urls)),
]
