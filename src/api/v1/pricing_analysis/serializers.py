"""Serializers for Pricing Analysis API."""

from rest_framework import serializers
from decimal import Decimal

from apps.pricing_analysis.models import (
    PricingAnalysisResult,
    PricingAnalysisBatch,
    KeepaProductData,
    BreakEvenAnalysisConfig,
    ExchangeRate,
)


class PricingAnalysisResultSerializer(serializers.ModelSerializer):
    """Serializer for PricingAnalysisResult."""

    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_title = serializers.CharField(source='product.title', read_only=True)

    class Meta:
        model = PricingAnalysisResult
        fields = [
            'id',
            'asin',
            'product',
            'product_sku',
            'product_title',
            # Keepa data
            'usa_keepa_data',
            'mx_keepa_data',
            'analysis_config',
            # Inputs
            'usa_cost',
            'usa_cost_currency',
            'usa_cost_source',
            'exchange_rate',
            'current_mx_amazon_price',
            'current_mx_amazon_price_currency',
            # Calculations
            'cost_base_mxn',
            'cost_base_mxn_currency',
            'vat_retention',
            'vat_retention_currency',
            'isr_retention',
            'isr_retention_currency',
            'shipping_cost_used',
            'shipping_cost_used_currency',
            'break_even_price',
            'break_even_price_currency',
            # Results
            'is_available_usa',
            'is_feasible',
            'recommended_price',
            'recommended_price_currency',
            'price_difference',
            'price_difference_currency',
            'potential_profit_margin',
            'confidence_score',
            'analysis_notes',
            # Timestamps
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class AnalyzeASINSerializer(serializers.Serializer):
    """Serializer for analyzing a single ASIN."""

    asin = serializers.CharField(
        max_length=20,
        required=True,
        help_text='Product ASIN to analyze'
    )
    shipping_cost_mxn = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
        help_text='Optional shipping cost override in MXN'
    )


class AnalyzeBulkSerializer(serializers.Serializer):
    """Serializer for bulk analysis."""

    asins = serializers.ListField(
        child=serializers.CharField(max_length=20),
        required=True,
        help_text='List of ASINs to analyze'
    )
    batch_name = serializers.CharField(
        max_length=200,
        required=True,
        help_text='Name for the batch'
    )
    shipping_cost_mxn = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
        help_text='Optional shipping cost override in MXN'
    )

    def validate_asins(self, value):
        """Validate that ASINs list is not empty."""
        if not value:
            raise serializers.ValidationError('ASINs list cannot be empty.')
        if len(value) > 100:
            raise serializers.ValidationError('Maximum 100 ASINs per batch.')
        return value


class PricingAnalysisBatchSerializer(serializers.ModelSerializer):
    """Serializer for PricingAnalysisBatch."""

    class Meta:
        model = PricingAnalysisBatch
        fields = [
            'id',
            'name',
            'asins',
            'status',
            'total_asins',
            'processed_asins',
            'successful_analyses',
            'failed_analyses',
            'unavailable_in_usa_count',
            'results',
            'error_log',
            'started_at',
            'completed_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class KeepaProductDataSerializer(serializers.ModelSerializer):
    """Serializer for KeepaProductData."""

    product_sku = serializers.CharField(source='product.sku', read_only=True)

    class Meta:
        model = KeepaProductData
        fields = [
            'id',
            'product',
            'product_sku',
            'asin',
            'marketplace',
            'current_amazon_price',
            'buy_box_price',
            'current_new_price',
            'avg_30_days_price',
            'avg_90_days_price',
            'title',
            'brand',
            'product_category',
            'sales_rank',
            'is_available',
            'sync_successful',
            'sync_error_message',
            'last_synced_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class SyncASINSerializer(serializers.Serializer):
    """Serializer for syncing ASIN without analysis."""

    asin = serializers.CharField(
        max_length=20,
        required=True,
        help_text='Product ASIN to sync'
    )
    marketplace = serializers.ChoiceField(
        choices=['US', 'MX'],
        default='US',
        help_text='Marketplace to sync from'
    )


class BreakEvenAnalysisConfigSerializer(serializers.ModelSerializer):
    """Serializer for BreakEvenAnalysisConfig."""

    class Meta:
        model = BreakEvenAnalysisConfig
        fields = [
            'id',
            'name',
            'is_active',
            'import_admin_cost_rate',
            'iva_tax_rate',
            'vat_retention_rate',
            'isr_retention_rate',
            'marketplace_fee_rate',
            'fixed_shipping_min',
            'fixed_shipping_min_currency',
            'fixed_shipping_max',
            'fixed_shipping_max_currency',
            'min_profit_margin',
            'target_profit_margin',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class ExchangeRateSerializer(serializers.ModelSerializer):
    """Serializer for ExchangeRate."""

    class Meta:
        model = ExchangeRate
        fields = [
            'id',
            'from_currency',
            'to_currency',
            'rate',
            'is_active',
            'source',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
