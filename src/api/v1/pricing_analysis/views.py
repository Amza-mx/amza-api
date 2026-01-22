"""Views for Pricing Analysis API."""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal

from apps.pricing_analysis.models import (
    PricingAnalysisResult,
    PricingAnalysisBatch,
    KeepaProductData,
    BreakEvenAnalysisConfig,
    ExchangeRate,
)
from apps.pricing_analysis.services import PricingAnalysisService, KeepaService
from apps.pricing_analysis.services.exceptions import (
    KeepaAPIError,
    TokenLimitExceededError,
    ExchangeRateNotFoundError,
    AnalysisConfigNotFoundError,
)

from .serializers import (
    PricingAnalysisResultSerializer,
    AnalyzeASINSerializer,
    AnalyzeBulkSerializer,
    PricingAnalysisBatchSerializer,
    KeepaProductDataSerializer,
    SyncASINSerializer,
    BreakEvenAnalysisConfigSerializer,
    ExchangeRateSerializer,
)
from .filters import (
    PricingAnalysisResultFilter,
    PricingAnalysisBatchFilter,
    KeepaProductDataFilter,
)


class PricingAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Pricing Analysis Results.

    Provides endpoints for:
    - Listing all analyses
    - Retrieving single analysis
    - Analyzing single ASIN
    - Bulk analysis
    - Refreshing analysis
    - Getting feasible products
    """

    queryset = PricingAnalysisResult.objects.all().select_related(
        'product',
        'usa_keepa_data',
        'mx_keepa_data',
        'analysis_config',
    )
    serializer_class = PricingAnalysisResultSerializer
    filterset_class = PricingAnalysisResultFilter
    ordering_fields = ['created_at', 'potential_profit_margin', 'break_even_price']
    ordering = ['-created_at']

    @action(detail=False, methods=['post'])
    def analyze_asin(self, request):
        """
        Analyze a single ASIN.

        POST /api/v1/pricing-analysis/analyze-asin/
        {
            "asin": "B07XYZ1234",
            "shipping_cost_mxn": 85  // Optional
        }
        """
        serializer = AnalyzeASINSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        asin = serializer.validated_data['asin']
        shipping_cost_mxn = serializer.validated_data.get('shipping_cost_mxn')

        try:
            service = PricingAnalysisService()
            result = service.analyze_single_asin(
                asin=asin,
                shipping_cost_mxn=shipping_cost_mxn
            )

            result_serializer = PricingAnalysisResultSerializer(result)
            return Response(result_serializer.data, status=status.HTTP_200_OK)

        except TokenLimitExceededError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        except (ExchangeRateNotFoundError, AnalysisConfigNotFoundError) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except KeepaAPIError as e:
            return Response(
                {'error': f'Keepa API error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {'error': f'Unexpected error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def analyze_bulk(self, request):
        """
        Analyze multiple ASINs in a batch.

        POST /api/v1/pricing-analysis/analyze-bulk/
        {
            "asins": ["B07XYZ1234", "B08ABC5678"],
            "batch_name": "Weekly Review",
            "shipping_cost_mxn": 85  // Optional
        }
        """
        serializer = AnalyzeBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        asins = serializer.validated_data['asins']
        batch_name = serializer.validated_data['batch_name']
        shipping_cost_mxn = serializer.validated_data.get('shipping_cost_mxn')

        try:
            service = PricingAnalysisService()
            batch = service.analyze_multiple_asins(
                asins=asins,
                batch_name=batch_name,
                shipping_cost_mxn=shipping_cost_mxn
            )

            batch_serializer = PricingAnalysisBatchSerializer(batch)
            return Response(batch_serializer.data, status=status.HTTP_200_OK)

        except (ExchangeRateNotFoundError, AnalysisConfigNotFoundError) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Unexpected error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def feasible(self, request):
        """
        Get all feasible products.

        GET /api/v1/pricing-analysis/feasible/?min_margin=0.15
        """
        min_margin = request.query_params.get('min_margin')

        queryset = self.get_queryset().filter(is_feasible=True)

        if min_margin:
            try:
                min_margin = Decimal(min_margin)
                queryset = queryset.filter(potential_profit_margin__gte=min_margin)
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid min_margin parameter'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        """
        Refresh an existing analysis with fresh data.

        POST /api/v1/pricing-analysis/{id}/refresh/
        """
        analysis = self.get_object()

        try:
            service = PricingAnalysisService()
            result = service.analyze_single_asin(
                asin=analysis.asin,
                shipping_cost_mxn=analysis.shipping_cost_used.amount if analysis.shipping_cost_used else None
            )

            result_serializer = PricingAnalysisResultSerializer(result)
            return Response(result_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Refresh failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PricingAnalysisBatchViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Pricing Analysis Batches."""

    queryset = PricingAnalysisBatch.objects.all().prefetch_related('results')
    serializer_class = PricingAnalysisBatchSerializer
    filterset_class = PricingAnalysisBatchFilter
    ordering_fields = ['created_at', 'started_at', 'completed_at']
    ordering = ['-created_at']


class KeepaProductDataViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Keepa Product Data."""

    queryset = KeepaProductData.objects.all().select_related('product')
    serializer_class = KeepaProductDataSerializer
    filterset_class = KeepaProductDataFilter
    ordering_fields = ['last_synced_at', 'created_at']
    ordering = ['-last_synced_at']

    @action(detail=False, methods=['post'])
    def sync_asin(self, request):
        """
        Sync ASIN data from Keepa without running analysis.

        POST /api/v1/keepa-data/sync-asin/
        {
            "asin": "B07XYZ1234",
            "marketplace": "US"  // Optional, default: US
        }
        """
        serializer = SyncASINSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        asin = serializer.validated_data['asin']
        marketplace = serializer.validated_data.get('marketplace', 'US')

        try:
            service = KeepaService()
            keepa_data = service.fetch_product_data(asin, marketplace)

            data_serializer = KeepaProductDataSerializer(keepa_data)
            return Response(data_serializer.data, status=status.HTTP_200_OK)

        except TokenLimitExceededError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        except KeepaAPIError as e:
            return Response(
                {'error': f'Keepa API error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {'error': f'Unexpected error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BreakEvenConfigViewSet(viewsets.ModelViewSet):
    """ViewSet for Break Even Analysis Config."""

    queryset = BreakEvenAnalysisConfig.objects.all()
    serializer_class = BreakEvenAnalysisConfigSerializer
    ordering_fields = ['created_at', 'is_active']
    ordering = ['-is_active', '-created_at']

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate a configuration.

        POST /api/v1/break-even-configs/{id}/activate/
        """
        config = self.get_object()
        config.is_active = True
        config.save()

        serializer = self.get_serializer(config)
        return Response(serializer.data)


class ExchangeRateViewSet(viewsets.ModelViewSet):
    """ViewSet for Exchange Rates."""

    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializer
    ordering_fields = ['created_at', 'is_active']
    ordering = ['-is_active', '-created_at']

    @action(detail=False, methods=['get'])
    def active_usd_mxn(self, request):
        """
        Get the active USD to MXN exchange rate.

        GET /api/v1/exchange-rates/active-usd-mxn/
        """
        try:
            rate = ExchangeRate.get_active_usd_mxn_rate()
            exchange_rate = ExchangeRate.objects.get(
                from_currency='USD',
                to_currency='MXN',
                is_active=True
            )
            serializer = self.get_serializer(exchange_rate)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
