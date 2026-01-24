"""Tests for PricingCalculator."""

from decimal import Decimal
from django.test import TestCase

from apps.pricing_analysis.models import BreakEvenAnalysisConfig
from apps.pricing_analysis.services.pricing_calculator import PricingCalculator


class PricingCalculatorTest(TestCase):
    """Test PricingCalculator service."""

    def setUp(self):
        """Set up test config."""
        self.config = BreakEvenAnalysisConfig.objects.create(
            name='Test Config',
            is_active=True,
            import_admin_cost_rate=Decimal('0.2000'),
            iva_tax_rate=Decimal('0.1600'),
            vat_retention_rate=Decimal('0.0800'),
            isr_retention_rate=Decimal('0.0250'),
            marketplace_fee_rate=Decimal('0.1500'),
        )
        self.calculator = PricingCalculator()

    def test_calculate_break_even(self):
        """Test Break Even calculation."""
        usa_cost = Decimal('12.50')
        exchange_rate = Decimal('20.0000')
        shipping_cost = Decimal('85.00')

        result = self.calculator.calculate_break_even(
            usa_cost_usd=usa_cost,
            exchange_rate=exchange_rate,
            shipping_cost_mxn=shipping_cost,
            config=self.config
        )

        # Verify structure
        self.assertIn('usa_cost_mxn', result)
        self.assertIn('after_import', result)
        self.assertIn('cost_base', result)
        self.assertIn('break_even_base', result)
        self.assertIn('retention_factor', result)
        self.assertIn('vat_retention', result)
        self.assertIn('isr_retention', result)
        self.assertIn('break_even_price', result)

        # Verify calculations
        # USA cost in MXN: 12.50 * 20 * 1.0825 = 270.625
        self.assertEqual(result['usa_cost_mxn'], Decimal('270.62'))

        # After import: (270.625 * 0.20) + IVA 16% = 62.785
        self.assertEqual(result['after_import'], Decimal('62.78'))

        # Cost base: 270.625 + 62.785 = 333.41
        self.assertEqual(result['cost_base'], Decimal('333.41'))

        # Break even base: 418.41 / 0.85 = 492.25
        self.assertEqual(result['break_even_base'], Decimal('492.25'))

        # Retention factor: (0.08 + 0.025) / 1.16 = 0.0905172
        self.assertEqual(result['retention_factor'], Decimal('0.0905172'))

        # VAT retention (BE): 541.24 / 1.16 * 0.08 = 37.33
        self.assertEqual(result['vat_retention'], Decimal('37.33'))

        # ISR retention (BE): 541.24 / 1.16 * 0.025 = 11.66
        self.assertEqual(result['isr_retention'], Decimal('11.66'))

        # Break even final: 492.25 / (1 - 0.0905172) = 541.24
        self.assertEqual(result['break_even_price'], Decimal('541.24'))

    def test_calculate_recommended_price(self):
        """Test recommended price calculation."""
        break_even = Decimal('541.24')
        target_margin = Decimal('0.25')

        recommended = self.calculator.calculate_recommended_price(
            break_even_price=break_even,
            target_margin=target_margin
        )

        # Recommended: 541.24 * 1.25 = 676.55
        self.assertEqual(recommended, Decimal('676.55'))

    def test_analyze_competitiveness_feasible(self):
        """Test competitiveness analysis for feasible product."""
        break_even = Decimal('541.24')
        current_price = Decimal('699.00')

        result = self.calculator.analyze_competitiveness(
            break_even=break_even,
            current_mx_price=current_price,
            config=self.config
        )

        self.assertTrue(result['is_feasible'])
        self.assertEqual(result['price_difference'], Decimal('157.76'))
        self.assertTrue(result['meets_min_margin'])

    def test_analyze_competitiveness_not_feasible(self):
        """Test competitiveness analysis for non-feasible product."""
        break_even = Decimal('541.24')
        current_price = Decimal('500.00')

        result = self.calculator.analyze_competitiveness(
            break_even=break_even,
            current_mx_price=current_price,
            config=self.config
        )

        self.assertFalse(result['is_feasible'])
        self.assertFalse(result['meets_min_margin'])

    def test_get_average_shipping_cost(self):
        """Test getting average shipping cost."""
        avg_shipping = self.calculator.get_average_shipping_cost(self.config)

        # Default config has min=70, max=100
        # Average: (70 + 100) / 2 = 85
        self.assertEqual(avg_shipping, Decimal('85.00'))

    def test_confidence_score_high(self):
        """Test confidence score HIGH when meeting target margin."""
        result = self.calculator.analyze_competitiveness(
            break_even=Decimal('400.00'),
            current_mx_price=Decimal('600.00'),  # 33% margin
            config=self.config
        )
        self.assertEqual(result['confidence_score'], 'HIGH')

    def test_confidence_score_medium(self):
        """Test confidence score MEDIUM when meeting min but not target."""
        result = self.calculator.analyze_competitiveness(
            break_even=Decimal('500.00'),
            current_mx_price=Decimal('575.00'),  # 13% margin
            config=self.config
        )
        self.assertEqual(result['confidence_score'], 'MEDIUM')

    def test_confidence_score_low(self):
        """Test confidence score LOW when not meeting min margin."""
        result = self.calculator.analyze_competitiveness(
            break_even=Decimal('500.00'),
            current_mx_price=Decimal('520.00'),  # 3.8% margin
            config=self.config
        )
        self.assertEqual(result['confidence_score'], 'LOW')
