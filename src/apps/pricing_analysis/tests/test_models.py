"""Tests for pricing_analysis models."""

from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from djmoney.money import Money

from apps.pricing_analysis.models import (
    KeepaConfiguration,
    ExchangeRate,
    KeepaProductData,
    BreakEvenAnalysisConfig,
    PricingAnalysisResult,
    PricingAnalysisBatch,
    KeepaAPILog,
)
from apps.products.models import Product


class KeepaConfigurationTest(TestCase):
    """Test KeepaConfiguration model."""

    def test_create_keepa_config(self):
        """Test creating Keepa configuration."""
        config = KeepaConfiguration.objects.create(
            api_key='test_api_key_12345',
            is_active=True,
            daily_token_limit=5000
        )
        self.assertEqual(config.tokens_used_today, 0)
        self.assertTrue(config.is_active)

    def test_token_consumption(self):
        """Test token consumption tracking."""
        config = KeepaConfiguration.objects.create(
            api_key='test_key',
            daily_token_limit=100
        )

        self.assertTrue(config.can_consume_tokens(50))
        config.consume_tokens(50)
        self.assertEqual(config.tokens_used_today, 50)

        self.assertTrue(config.can_consume_tokens(40))
        self.assertFalse(config.can_consume_tokens(51))


class ExchangeRateTest(TestCase):
    """Test ExchangeRate model."""

    def test_create_exchange_rate(self):
        """Test creating exchange rate."""
        rate = ExchangeRate.objects.create(
            from_currency='USD',
            to_currency='MXN',
            rate=Decimal('20.5000'),
            is_active=True
        )
        self.assertEqual(rate.rate, Decimal('20.5000'))

    def test_get_active_usd_mxn_rate(self):
        """Test getting active USD to MXN rate."""
        ExchangeRate.objects.create(
            from_currency='USD',
            to_currency='MXN',
            rate=Decimal('20.5000'),
            is_active=True
        )

        rate = ExchangeRate.get_active_usd_mxn_rate()
        self.assertEqual(rate, Decimal('20.5000'))

    def test_no_active_rate_raises_error(self):
        """Test that missing active rate raises error."""
        with self.assertRaises(ValueError):
            ExchangeRate.get_active_usd_mxn_rate()


class BreakEvenAnalysisConfigTest(TestCase):
    """Test BreakEvenAnalysisConfig model."""

    def test_create_config(self):
        """Test creating analysis config."""
        config = BreakEvenAnalysisConfig.objects.create(
            name='Default Config',
            is_active=True
        )
        self.assertEqual(config.import_admin_cost_rate, Decimal('0.2000'))
        self.assertEqual(config.iva_tax_rate, Decimal('0.1600'))

    def test_only_one_active_config(self):
        """Test that only one config can be active."""
        config1 = BreakEvenAnalysisConfig.objects.create(
            name='Config 1',
            is_active=True
        )
        config2 = BreakEvenAnalysisConfig.objects.create(
            name='Config 2',
            is_active=True
        )

        # Refresh from DB
        config1.refresh_from_db()
        self.assertFalse(config1.is_active)
        self.assertTrue(config2.is_active)

    def test_get_active_config(self):
        """Test getting active config."""
        BreakEvenAnalysisConfig.objects.create(
            name='Test Config',
            is_active=True
        )

        config = BreakEvenAnalysisConfig.get_active_config()
        self.assertEqual(config.name, 'Test Config')


class KeepaProductDataTest(TestCase):
    """Test KeepaProductData model."""

    def setUp(self):
        """Set up test product."""
        self.product = Product.objects.create(
            sku='TEST-001',
            title='Test Product',
            external_id='B07XYZ1234',
            category='Electronics',
            inventory_quantity=10
        )

    def test_create_keepa_data(self):
        """Test creating Keepa product data."""
        keepa_data = KeepaProductData.objects.create(
            product=self.product,
            asin='B07XYZ1234',
            marketplace='US',
            buy_box_price=Decimal('15.99'),
            current_amazon_price=Decimal('16.99'),
            title='Test Product',
            is_available=True
        )
        self.assertEqual(keepa_data.asin, 'B07XYZ1234')
        self.assertTrue(keepa_data.is_available)

    def test_unique_constraint(self):
        """Test unique constraint on asin and marketplace."""
        KeepaProductData.objects.create(
            product=self.product,
            asin='B07XYZ1234',
            marketplace='US'
        )

        # Should raise IntegrityError
        with self.assertRaises(Exception):
            KeepaProductData.objects.create(
                product=self.product,
                asin='B07XYZ1234',
                marketplace='US'
            )


class PricingAnalysisResultTest(TestCase):
    """Test PricingAnalysisResult model."""

    def setUp(self):
        """Set up test data."""
        self.product = Product.objects.create(
            sku='TEST-001',
            title='Test Product',
            external_id='B07XYZ1234',
            category='Electronics',
            inventory_quantity=10
        )
        self.config = BreakEvenAnalysisConfig.objects.create(
            name='Test Config',
            is_active=True
        )

    def test_create_pricing_result(self):
        """Test creating pricing analysis result."""
        result = PricingAnalysisResult.objects.create(
            product=self.product,
            asin='B07XYZ1234',
            analysis_config=self.config,
            usa_cost=Money(Decimal('12.50'), 'USD'),
            usa_cost_source='buy_box',
            exchange_rate=Decimal('20.1500'),
            break_even_price=Money(Decimal('485.23'), 'MXN'),
            current_mx_amazon_price=Money(Decimal('599.00'), 'MXN'),
            is_available_usa=True,
            is_feasible=True,
            potential_profit_margin=Decimal('0.1900')
        )
        self.assertTrue(result.is_feasible)
        self.assertEqual(result.usa_cost_source, 'buy_box')


class PricingAnalysisBatchTest(TestCase):
    """Test PricingAnalysisBatch model."""

    def test_create_batch(self):
        """Test creating analysis batch."""
        batch = PricingAnalysisBatch.objects.create(
            name='Test Batch',
            asins=['B07XYZ1234', 'B08ABC5678'],
            status='PENDING',
            total_asins=2
        )
        self.assertEqual(batch.status, 'PENDING')
        self.assertEqual(batch.total_asins, 2)
        self.assertEqual(batch.processed_asins, 0)


class KeepaAPILogTest(TestCase):
    """Test KeepaAPILog model."""

    def test_create_log(self):
        """Test creating API log."""
        log = KeepaAPILog.objects.create(
            endpoint='query',
            request_params={'asin': 'B07XYZ1234'},
            response_status=200,
            response_data={'products_count': 1},
            tokens_consumed=1,
            execution_time_ms=1500
        )
        self.assertEqual(log.response_status, 200)
        self.assertEqual(log.tokens_consumed, 1)
