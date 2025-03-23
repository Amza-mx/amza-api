from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MarketplaceViewSet

router = DefaultRouter()
router.register(r'marketplaces', MarketplaceViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 