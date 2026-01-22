"""
Keepa Service

Handles all interactions with Keepa API including:
- Fetching product data
- Parsing responses
- Determining USA cost with cascading priority
- Auto-creating products
- Token tracking
"""

import time
import json
import numpy as np
from datetime import datetime, date, time as dt_time
from decimal import Decimal
from typing import List, Dict, Tuple, Optional, Any
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
import keepa

from apps.pricing_analysis.models import (
    KeepaConfiguration,
    KeepaProductData,
    KeepaAPILog,
)
from apps.products.models import Product
from .exceptions import KeepaAPIError, TokenLimitExceededError


class KeepaService:
    """Service for interacting with Keepa API."""

    # Domain mapping for marketplaces
    MARKETPLACE_DOMAINS = {
        'US': 'US',  # Amazon.com
        'MX': 'MX',  # Amazon.com.mx
    }

    def __init__(self):
        """Initialize Keepa API client."""
        self.config = self._get_active_config()
        self.api = keepa.Keepa(self.config.api_key)

    @staticmethod
    def _convert_to_json_serializable(obj: Any) -> Any:
        """
        Convert Keepa data to JSON-serializable format.
        Handles numpy arrays, datetime objects, and other non-serializable types.

        This uses a two-pass approach:
        1. First pass: convert numpy arrays and basic types recursively
        2. Second pass: use DjangoJSONEncoder to handle datetime and other Django types

        Args:
            obj: Object to convert

        Returns:
            JSON-serializable version of the object
        """
        # First pass: handle numpy arrays and recurse through structures
        def first_pass(value):
            if isinstance(value, np.ndarray):
                return value.tolist()
            elif isinstance(value, (np.integer, np.floating)):
                return value.item()
            elif isinstance(value, dict):
                return {k: first_pass(v) for k, v in value.items()}
            elif isinstance(value, (list, tuple)):
                return [first_pass(item) for item in value]
            else:
                return value

        # Apply first pass
        converted = first_pass(obj)

        # Second pass: use DjangoJSONEncoder to handle datetime and convert back
        try:
            json_str = json.dumps(converted, cls=DjangoJSONEncoder)
            return json.loads(json_str)
        except (TypeError, ValueError) as e:
            # If still failing, log and return empty dict
            print(f"Warning: Could not serialize Keepa data: {e}")
            return {}

    def _get_active_config(self) -> KeepaConfiguration:
        """Get the active Keepa configuration."""
        try:
            return KeepaConfiguration.objects.get(is_active=True)
        except KeepaConfiguration.DoesNotExist:
            raise KeepaAPIError(
                'No active Keepa configuration found. '
                'Please configure Keepa API key in the admin panel.'
            )

    def check_token_availability(self, required_tokens: int = 1) -> bool:
        """
        Check if there are enough tokens available.

        Args:
            required_tokens: Number of tokens required for the operation

        Returns:
            True if tokens are available, False otherwise
        """
        self.config.refresh_from_db()
        return self.config.can_consume_tokens(required_tokens)

    def fetch_product_data(
        self,
        asin: str,
        marketplace: str = 'US'
    ) -> KeepaProductData:
        """
        Fetch product data from Keepa API.

        Args:
            asin: Product ASIN
            marketplace: 'US' or 'MX'

        Returns:
            KeepaProductData instance

        Raises:
            TokenLimitExceededError: If token limit is exceeded
            KeepaAPIError: If API call fails
        """
        # Check token availability
        if not self.check_token_availability(1):
            raise TokenLimitExceededError(
                f'Keepa API token limit exceeded. '
                f'Used: {self.config.tokens_used_today}/{self.config.daily_token_limit}'
            )

        start_time = time.time()
        domain_id = self.MARKETPLACE_DOMAINS.get(marketplace, 1)

        try:
            # Make API call with buybox=True to get Buy Box data
            products = self.api.query(asin, domain=domain_id, buybox=True)

            execution_time_ms = int((time.time() - start_time) * 1000)

            # Log the API call
            self._log_api_call(
                endpoint='query',
                request_params={'asin': asin, 'domain': domain_id, 'buybox': True},
                response_status=200,
                response_data={'products_count': len(products) if products else 0},
                tokens_consumed=1,
                execution_time_ms=execution_time_ms,
            )

            # Consume token
            self.config.consume_tokens(1)

            if not products or len(products) == 0:
                # Product not found
                return self._create_unavailable_keepa_data(asin, marketplace)

            product_data = products[0]

            # Parse and save data
            keepa_data = self._parse_keepa_response(
                asin=asin,
                marketplace=marketplace,
                keepa_product=product_data
            )

            return keepa_data

        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)

            # Log error
            self._log_api_call(
                endpoint='query',
                request_params={'asin': asin, 'domain': domain_id},
                response_status=500,
                response_data={},
                tokens_consumed=1,
                error_message=str(e),
                execution_time_ms=execution_time_ms,
            )

            raise KeepaAPIError(f'Failed to fetch data for ASIN {asin}: {str(e)}')

    def _parse_keepa_response(
        self,
        asin: str,
        marketplace: str,
        keepa_product: dict
    ) -> KeepaProductData:
        """
        Parse Keepa API response and create/update KeepaProductData.

        Args:
            asin: Product ASIN
            marketplace: Marketplace code
            keepa_product: Raw Keepa product data

        Returns:
            KeepaProductData instance
        """
        # Get current prices from product['data']
        # Prices are already in dollars/pesos (not cents)
        def get_current_price(price_key):
            """Extract current price from Keepa data array."""
            data = keepa_product.get('data', {})
            price_array = data.get(price_key)

            if price_array is None or len(price_array) == 0:
                return None

            # Get the last value (most recent)
            # Handle numpy nan values
            import math
            last_price = price_array[-1]

            if last_price is None or (isinstance(last_price, float) and math.isnan(last_price)):
                return None

            return Decimal(str(last_price))

        # Get current prices from different sources
        buy_box_price = get_current_price('BUY_BOX_SHIPPING')
        current_amazon_price = get_current_price('AMAZON')

        # For simplicity, use stats if available
        stats = keepa_product.get('stats', {})

        # Check if product is available
        is_available = (
            current_amazon_price is not None or
            buy_box_price is not None
        )

        # Get or create product
        product = self.get_or_create_product(asin, keepa_product)

        # Create or update KeepaProductData
        keepa_data, created = KeepaProductData.objects.update_or_create(
            asin=asin,
            marketplace=marketplace,
            defaults={
                'product': product,
                'current_amazon_price': current_amazon_price,
                'buy_box_price': buy_box_price,
                'current_new_price': get_current_price('NEW'),
                'avg_30_days_price': Decimal(str(stats.get('avg30', [None])[0])) if stats.get('avg30') and stats.get('avg30')[0] not in (None, -1) else None,
                'avg_90_days_price': Decimal(str(stats.get('avg90', [None])[0])) if stats.get('avg90') and stats.get('avg90')[0] not in (None, -1) else None,
                'title': keepa_product.get('title', ''),
                'brand': keepa_product.get('brand', ''),
                'product_category': keepa_product.get('categoryTree', [{}])[0].get('name', '') if keepa_product.get('categoryTree') else '',
                'sales_rank': keepa_product.get('salesRanks', {}).get('current', [None, None])[1] if keepa_product.get('salesRanks', {}).get('current') else None,
                'is_available': is_available,
                'raw_data': self._convert_to_json_serializable(keepa_product),
                'sync_successful': True,
                'sync_error_message': '',
            }
        )

        return keepa_data

    def _create_unavailable_keepa_data(
        self,
        asin: str,
        marketplace: str
    ) -> KeepaProductData:
        """Create KeepaProductData for unavailable product."""
        keepa_data, created = KeepaProductData.objects.update_or_create(
            asin=asin,
            marketplace=marketplace,
            defaults={
                'product': None,
                'is_available': False,
                'sync_successful': False,
                'sync_error_message': 'Product not found in Keepa',
                'raw_data': {},
            }
        )
        return keepa_data

    def get_or_create_product(self, asin: str, keepa_data: dict) -> Product:
        """
        Get or create Product from Keepa data.

        Args:
            asin: Product ASIN
            keepa_data: Keepa product data

        Returns:
            Product instance
        """
        # Try to find existing product by external_id
        try:
            product = Product.objects.get(external_id=asin)
            return product
        except Product.DoesNotExist:
            pass

        # Create new product
        title = keepa_data.get('title', f'Keepa Product {asin}')
        sku = f'KEEPA-{asin}'

        # Map category (simplified - you might want to enhance this)
        category_tree = keepa_data.get('categoryTree', [])
        category_name = category_tree[0].get('name', '') if category_tree else ''

        product = Product.objects.create(
            sku=sku,
            external_id=asin,
            title=title[:500],
            description=title,
            category=category_name[:100] if category_name else 'Uncategorized',
            inventory_quantity=0,  # Start with 0 inventory
        )

        return product

    def determine_usa_cost(
        self,
        usa_keepa_data: KeepaProductData
    ) -> Tuple[Optional[Decimal], str]:
        """
        Determine USA cost with cascading priority.

        Priority:
        1. Buy Box Price
        2. Current Amazon Price
        3. Current New Price
        4. Unavailable

        Args:
            usa_keepa_data: KeepaProductData for US marketplace

        Returns:
            Tuple of (price, source) where source is 'buy_box', 'amazon', 'new', or 'unavailable'
        """
        if usa_keepa_data.buy_box_price is not None and usa_keepa_data.buy_box_price > 0:
            return (usa_keepa_data.buy_box_price, 'buy_box')

        if usa_keepa_data.current_amazon_price is not None and usa_keepa_data.current_amazon_price > 0:
            return (usa_keepa_data.current_amazon_price, 'amazon')

        if usa_keepa_data.current_new_price is not None and usa_keepa_data.current_new_price > 0:
            return (usa_keepa_data.current_new_price, 'new')

        return (None, 'unavailable')

    def fetch_bulk_product_data(
        self,
        asins: List[str],
        marketplace: str = 'US'
    ) -> Dict[str, KeepaProductData]:
        """
        Fetch multiple products data (sequentially to avoid rate limits).

        Args:
            asins: List of ASINs
            marketplace: Marketplace code

        Returns:
            Dictionary mapping ASIN to KeepaProductData
        """
        results = {}

        for asin in asins:
            try:
                data = self.fetch_product_data(asin, marketplace)
                results[asin] = data
            except (KeepaAPIError, TokenLimitExceededError) as e:
                # Log error but continue with other ASINs
                print(f'Error fetching {asin}: {e}')
                continue

        return results

    def _log_api_call(
        self,
        endpoint: str,
        request_params: dict,
        response_status: int,
        response_data: dict,
        tokens_consumed: int,
        error_message: str = '',
        execution_time_ms: int = 0
    ):
        """Log Keepa API call."""
        return
        KeepaAPILog.objects.create(
            endpoint=endpoint,
            request_params=request_params,
            response_status=response_status,
            response_data=response_data,
            tokens_consumed=tokens_consumed,
            error_message=error_message,
            execution_time_ms=execution_time_ms,
        )
