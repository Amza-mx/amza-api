"""Filters for Pricing Analysis API."""

from django_filters import rest_framework as filters
from apps.pricing_analysis.models import (
    PricingAnalysisResult,
    PricingAnalysisBatch,
    KeepaProductData,
)


class PricingAnalysisResultFilter(filters.FilterSet):
    """Filter for PricingAnalysisResult."""

    asin = filters.CharFilter(lookup_expr='icontains')
    product_sku = filters.CharFilter(field_name='product__sku', lookup_expr='icontains')
    is_feasible = filters.BooleanFilter()
    is_available_usa = filters.BooleanFilter()
    confidence_score = filters.ChoiceFilter(choices=PricingAnalysisResult.CONFIDENCE_SCORE_CHOICES)
    usa_cost_source = filters.ChoiceFilter(choices=PricingAnalysisResult.USA_COST_SOURCE_CHOICES)
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    min_profit_margin = filters.NumberFilter(field_name='potential_profit_margin', lookup_expr='gte')

    class Meta:
        model = PricingAnalysisResult
        fields = [
            'asin',
            'product_sku',
            'is_feasible',
            'is_available_usa',
            'confidence_score',
            'usa_cost_source',
            'created_after',
            'created_before',
            'min_profit_margin',
        ]


class PricingAnalysisBatchFilter(filters.FilterSet):
    """Filter for PricingAnalysisBatch."""

    status = filters.ChoiceFilter(choices=PricingAnalysisBatch.STATUS_CHOICES)
    name = filters.CharFilter(lookup_expr='icontains')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = PricingAnalysisBatch
        fields = ['status', 'name', 'created_after', 'created_before']


class KeepaProductDataFilter(filters.FilterSet):
    """Filter for KeepaProductData."""

    asin = filters.CharFilter(lookup_expr='icontains')
    marketplace = filters.ChoiceFilter(choices=KeepaProductData.MARKETPLACE_CHOICES)
    sync_successful = filters.BooleanFilter()
    is_available = filters.BooleanFilter()

    class Meta:
        model = KeepaProductData
        fields = ['asin', 'marketplace', 'sync_successful', 'is_available']
