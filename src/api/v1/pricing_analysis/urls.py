"""URLs for Pricing Analysis API."""

from rest_framework.routers import DefaultRouter
from .views import (
    PricingAnalysisViewSet,
    PricingAnalysisBatchViewSet,
    KeepaProductDataViewSet,
    BreakEvenConfigViewSet,
    ExchangeRateViewSet,
)

router = DefaultRouter()

router.register(
    r'pricing-analysis',
    PricingAnalysisViewSet,
    basename='pricing-analysis'
)
router.register(
    r'pricing-analysis-batches',
    PricingAnalysisBatchViewSet,
    basename='pricing-analysis-batch'
)
router.register(
    r'keepa-data',
    KeepaProductDataViewSet,
    basename='keepa-data'
)
router.register(
    r'break-even-configs',
    BreakEvenConfigViewSet,
    basename='break-even-config'
)
router.register(
    r'exchange-rates',
    ExchangeRateViewSet,
    basename='exchange-rate'
)

urlpatterns = router.urls
