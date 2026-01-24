from django.urls import path
from .views import (
    PricingAnalysisPanoramaView,
    PricingAnalysisResultDetailView,
    BrandRestrictionListView,
    PricingAnalysisBatchView,
)

app_name = 'pricing_analysis'

urlpatterns = [
    path('panorama/', PricingAnalysisPanoramaView.as_view(), name='panorama'),
    path('brands/', BrandRestrictionListView.as_view(), name='brand_restrictions'),
    path('batch/', PricingAnalysisBatchView.as_view(), name='batch_analyze'),
    path('results/<int:pk>/', PricingAnalysisResultDetailView.as_view(), name='result_detail'),
]
