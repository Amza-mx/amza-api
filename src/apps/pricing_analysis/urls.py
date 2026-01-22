from django.urls import path
from .views import PricingAnalysisResultDetailView

app_name = 'pricing_analysis'

urlpatterns = [
    path('results/<int:pk>/', PricingAnalysisResultDetailView.as_view(), name='result_detail'),
]
