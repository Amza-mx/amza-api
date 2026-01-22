"""
Pricing Analysis Service

Main orchestrator that coordinates the entire analysis flow:
1. Fetch Keepa data (USA and MX)
2. Determine USA cost
3. Get exchange rate
4. Calculate Break Even
5. Analyze competitiveness
6. Save results
"""

from decimal import Decimal
from typing import List, Optional
from django.utils import timezone
from djmoney.money import Money

from apps.pricing_analysis.models import (
    ExchangeRate,
    BreakEvenAnalysisConfig,
    PricingAnalysisResult,
    PricingAnalysisBatch,
)
from .keepa_service import KeepaService
from .pricing_calculator import PricingCalculator
from .exceptions import (
    ExchangeRateNotFoundError,
    AnalysisConfigNotFoundError,
    ProductNotAvailableError,
)


class PricingAnalysisService:
    """Main service for orchestrating pricing analysis."""

    def __init__(self):
        """Initialize services."""
        self.keepa_service = KeepaService()
        self.calculator = PricingCalculator()

    def analyze_single_asin(
        self,
        asin: str,
        shipping_cost_mxn: Optional[Decimal] = None,
        config: Optional[BreakEvenAnalysisConfig] = None
    ) -> PricingAnalysisResult:
        """
        Analyze a single ASIN for pricing viability.

        Args:
            asin: Product ASIN
            shipping_cost_mxn: Optional shipping cost override
            config: Optional config override (uses active if not provided)

        Returns:
            PricingAnalysisResult instance

        Raises:
            ExchangeRateNotFoundError: If no active exchange rate
            AnalysisConfigNotFoundError: If no active config
        """
        # 1. Get configuration
        if config is None:
            try:
                config = BreakEvenAnalysisConfig.get_active_config()
            except ValueError as e:
                raise AnalysisConfigNotFoundError(str(e))

        # 2. Fetch Keepa data for USA and MX
        usa_keepa_data = self.keepa_service.fetch_product_data(asin, 'US')
        mx_keepa_data = self.keepa_service.fetch_product_data(asin, 'MX')

        # 3. Determine USA cost
        usa_cost, usa_cost_source = self.keepa_service.determine_usa_cost(usa_keepa_data)

        # 4. Handle unavailable products
        if usa_cost_source == 'unavailable':
            return self._create_unavailable_result(
                asin=asin,
                usa_keepa_data=usa_keepa_data,
                mx_keepa_data=mx_keepa_data,
                config=config,
            )

        # 5. Get exchange rate
        try:
            exchange_rate = ExchangeRate.get_active_usd_mxn_rate()
        except ValueError as e:
            raise ExchangeRateNotFoundError(str(e))

        # 6. Validate/get shipping cost
        if shipping_cost_mxn is None:
            shipping_cost_mxn = self.calculator.get_average_shipping_cost(config)

        # 7. Get current MX price
        mx_current_price = None
        if mx_keepa_data.buy_box_price:
            mx_current_price = mx_keepa_data.buy_box_price
        elif mx_keepa_data.current_amazon_price:
            mx_current_price = mx_keepa_data.current_amazon_price
        elif mx_keepa_data.current_new_price:
            mx_current_price = mx_keepa_data.current_new_price

        # 8. Calculate Break Even
        breakdown = self.calculator.calculate_break_even(
            usa_cost_usd=usa_cost,
            cost_mx=mx_current_price,
            exchange_rate=exchange_rate,
            shipping_cost_mxn=shipping_cost_mxn,
            config=config
        )

        # 9. Analyze competitiveness
        competitiveness = self.calculator.analyze_competitiveness(
            break_even=breakdown['break_even_price'],
            current_mx_price=mx_current_price or Decimal('0'),
            config=config
        )

        # 10. Calculate recommended price
        recommended_price = self.calculator.calculate_recommended_price(
            break_even=breakdown['break_even_price'],
            target_margin=config.target_profit_margin
        )

        # 11. Generate analysis notes
        analysis_notes = self._generate_analysis_notes(
            competitiveness=competitiveness,
            usa_cost=usa_cost,
            usa_cost_source=usa_cost_source,
            break_even=breakdown['break_even_price'],
            mx_current_price=mx_current_price,
            recommended_price=recommended_price,
        )

        # 12. Create result
        product = usa_keepa_data.product or mx_keepa_data.product
        if product is None:
            # This should not happen, but handle it
            product = self.keepa_service.get_or_create_product(
                asin,
                usa_keepa_data.raw_data or {}
            )

        result = PricingAnalysisResult.objects.create(
            product=product,
            asin=asin,
            usa_keepa_data=usa_keepa_data,
            mx_keepa_data=mx_keepa_data,
            analysis_config=config,
            # Inputs
            usa_cost=Money(usa_cost, 'USD'),
            usa_cost_source=usa_cost_source,
            exchange_rate=exchange_rate.quantize(Decimal('0.0001')),
            current_mx_amazon_price=Money(mx_current_price or Decimal('0'), 'MXN'),
            # Calculations
            cost_base_mxn=Money(breakdown['cost_base'], 'MXN'),
            vat_retention=Money(breakdown['vat_retention'], 'MXN'),
            isr_retention=Money(breakdown['isr_retention'], 'MXN'),
            shipping_cost_used=Money(shipping_cost_mxn, 'MXN'),
            break_even_price=Money(breakdown['break_even_price'], 'MXN'),
            # Results
            is_available_usa=True,
            is_feasible=competitiveness['is_feasible'],
            recommended_price=Money(recommended_price, 'MXN'),
            price_difference=Money(competitiveness['price_difference'], 'MXN'),
            potential_profit_margin=competitiveness['potential_profit_margin'].quantize(Decimal('0.0001')),
            confidence_score=competitiveness['confidence_score'],
            analysis_notes=analysis_notes,
        )

        return result

    def _create_unavailable_result(
        self,
        asin: str,
        usa_keepa_data,
        mx_keepa_data,
        config: BreakEvenAnalysisConfig
    ) -> PricingAnalysisResult:
        """Create result for unavailable product."""
        # Try to get product
        product = usa_keepa_data.product or mx_keepa_data.product
        if product is None:
            # Create a placeholder product
            from apps.products.models import Product
            product, _ = Product.objects.get_or_create(
                external_id=asin,
                defaults={
                    'sku': f'KEEPA-{asin}',
                    'title': f'Unavailable Product {asin}',
                    'description': 'Product not available in Amazon USA',
                    'category': 'Uncategorized',
                    'inventory_quantity': 0,
                }
            )

        result = PricingAnalysisResult.objects.create(
            product=product,
            asin=asin,
            usa_keepa_data=usa_keepa_data,
            mx_keepa_data=mx_keepa_data,
            analysis_config=config,
            usa_cost=Money(Decimal('0'), 'USD'),
            usa_cost_source='unavailable',
            is_available_usa=False,
            is_feasible=False,
            analysis_notes=(
                '⚠️ Producto NO disponible en Amazon USA.\n\n'
                'Recomendación: Establecer inventory_quantity = 0 para este producto.\n\n'
                'El producto no tiene precio de Buy Box ni precio de Amazon en el marketplace de USA, '
                'por lo que no se puede calcular un Break Even. '
                'Se recomienda no intentar vender este producto hasta que esté disponible nuevamente.'
            ),
        )

        return result

    def _generate_analysis_notes(
        self,
        competitiveness: dict,
        usa_cost: Decimal,
        usa_cost_source: str,
        break_even: Decimal,
        mx_current_price: Optional[Decimal],
        recommended_price: Decimal,
    ) -> str:
        """Generate human-readable analysis notes."""
        notes = []

        # USA cost source
        source_display = {
            'buy_box': 'Buy Box Price',
            'amazon': 'Amazon Price',
            'new': 'Current New Price',
        }.get(usa_cost_source, 'Unknown')

        notes.append(f'✓ Precio USA obtenido de: {source_display} (${usa_cost} USD)')

        # Break even
        notes.append(f'✓ Break Even calculado: ${break_even} MXN')

        # Current MX price
        if mx_current_price and mx_current_price > 0:
            notes.append(f'✓ Precio actual en Amazon MX: ${mx_current_price} MXN')

            # Difference
            diff = competitiveness['price_difference']
            if diff > 0:
                notes.append(f'✓ Diferencia positiva: ${diff} MXN ({competitiveness["potential_profit_margin"] * 100:.2f}% margen)')
            else:
                notes.append(f'⚠ Diferencia negativa: ${diff} MXN - No es viable vender a precio actual')
        else:
            notes.append('⚠ No hay precio actual en Amazon MX')

        # Recommended price
        notes.append(f'✓ Precio recomendado: ${recommended_price} MXN')

        # Feasibility
        if competitiveness['is_feasible']:
            if competitiveness['meets_target_margin']:
                notes.append('✅ VIABLE - Cumple margen objetivo (25%)')
            else:
                notes.append('✅ VIABLE - Cumple margen mínimo (10%)')
        else:
            notes.append('❌ NO VIABLE - No cumple margen mínimo')

        return '\n'.join(notes)

    def analyze_multiple_asins(
        self,
        asins: List[str],
        batch_name: str,
        shipping_cost_mxn: Optional[Decimal] = None,
        config: Optional[BreakEvenAnalysisConfig] = None
    ) -> PricingAnalysisBatch:
        """
        Analyze multiple ASINs in a batch.

        Args:
            asins: List of ASINs to analyze
            batch_name: Name for the batch
            shipping_cost_mxn: Optional shipping cost override
            config: Optional config override

        Returns:
            PricingAnalysisBatch instance
        """
        # Create batch
        batch = PricingAnalysisBatch.objects.create(
            name=batch_name,
            asins=asins,
            status='PROCESSING',
            total_asins=len(asins),
            started_at=timezone.now(),
        )

        # Get config once
        if config is None:
            try:
                config = BreakEvenAnalysisConfig.get_active_config()
            except ValueError as e:
                batch.status = 'FAILED'
                batch.error_log = {'error': str(e)}
                batch.completed_at = timezone.now()
                batch.save()
                raise AnalysisConfigNotFoundError(str(e))

        # Process each ASIN
        for asin in asins:
            try:
                result = self.analyze_single_asin(
                    asin=asin,
                    shipping_cost_mxn=shipping_cost_mxn,
                    config=config
                )

                # Add to batch
                batch.results.add(result)
                batch.processed_asins += 1

                if result.is_available_usa:
                    batch.successful_analyses += 1
                else:
                    batch.unavailable_in_usa_count += 1

                batch.save()

            except Exception as e:
                batch.failed_analyses += 1
                batch.processed_asins += 1

                # Log error
                if not batch.error_log:
                    batch.error_log = {}
                batch.error_log[asin] = str(e)

                batch.save()

        # Mark as completed
        batch.status = 'COMPLETED'
        batch.completed_at = timezone.now()
        batch.save()

        return batch
