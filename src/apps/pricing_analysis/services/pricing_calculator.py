"""
Pricing Calculator Service

Implements the Break Even calculation formula:

1. USA_Cost_MXN = USA_Cost_USD * Exchange_Rate * 1.0825
   (1.0825 = 8.25% impuestos americanos)

2. Import_Fees = USA_Cost_MXN * 0.20
   (20% costos administrativos de importación)

3. IVA_Import_Fees = Import_Fees * 0.16
   (16% IVA sobre los fees de importación)

4. Cost_Base = USA_Cost_MXN + Import_Fees + IVA_Import_Fees

5. Total_Costs = Cost_Base + Shipping_Cost_MXN

6. Break_Even_Base = Total_Costs / (1 - Marketplace_Fee_Rate)
   (donde Marketplace_Fee_Rate = 0.15 para Amazon)

7. VAT_Retention = (Cost_MX / 1.16) * 0.08
   ISR_Retention = (Cost_MX / 1.16) * 0.025

8. Break_Even_Final = Break_Even_Base + VAT_Retention + ISR_Retention

Donde:
- USA_Cost_USD: Precio de compra del producto en USA (obtenido de Keepa)
- Exchange_Rate: Tipo de cambio USD→MXN actual
- Cost_MX: Precio de venta del producto (puede ser el precio de Amazon MX u otro precio establecido)
- Shipping_Cost_MXN: Costo de envío ($70-$100 MXN promedio)
"""

from decimal import Decimal
from typing import Dict, Any
from djmoney.money import Money


class PricingCalculator:
    """Handles all Break Even and pricing calculations."""

    @staticmethod
    def calculate_break_even(
        usa_cost_usd: Decimal,
        cost_mx: Decimal,
        exchange_rate: Decimal,
        shipping_cost_mxn: Decimal,
        config: 'BreakEvenAnalysisConfig'
    ) -> Dict[str, Decimal]:
        """
        Calculate Break Even price based on USA cost and config parameters.

        Args:
            usa_cost_usd: Precio de compra del producto en USD (obtenido de Keepa)
            cost_mx: Precio de venta del producto en MXN (puede ser el precio de Amazon MX
                     u otro precio establecido)
            exchange_rate: USD to MXN exchange rate
            shipping_cost_mxn: Shipping cost in MXN
            config: Analysis configuration with tax rates

        Returns:
            Dictionary with all calculation steps:
            {
                'usa_cost_mxn': Decimal,
                'after_import': Decimal,
                'cost_base': Decimal,
                'vat_retention': Decimal,
                'isr_retention': Decimal,
                'total_costs': Decimal,
                'break_even_price': Decimal
            }
        """
        # Convert USA cost to MXN
        usa_cost_mxn = usa_cost_usd * exchange_rate

        IMPUESTOS_AMERICANOS = Decimal('1.0825')

        # $1,000
        usa_cost_mxn = usa_cost_mxn * IMPUESTOS_AMERICANOS

        # $200
        # Apply import administrative costs (20%)
        percent_import_fees = usa_cost_mxn * config.import_admin_cost_rate

        # $32
        # Apply taxes of import fees
        iva_import_fees = percent_import_fees * config.iva_tax_rate

        # $232
        after_import = percent_import_fees + iva_import_fees

        # $1,232.00
        cost_base = usa_cost_mxn + after_import

        # Calculate retentions
        costo_venta_base = cost_mx / (Decimal('1') + config.iva_tax_rate)
        vat_retention = costo_venta_base * config.vat_retention_rate
        isr_retention = costo_venta_base * config.isr_retention_rate

        # Total costs
        # $469.20 + $85 = $554.21
        total_costs = cost_base + shipping_cost_mxn


        # Break Even (divide by (1 - marketplace_fee_rate) to account for 15% fee)
        break_even_price = total_costs / (Decimal('1') - config.marketplace_fee_rate)
        break_even_price = break_even_price + vat_retention + isr_retention

        return {
            'usa_cost_mxn': usa_cost_mxn.quantize(Decimal('0.01')),
            'after_import': after_import.quantize(Decimal('0.01')),
            'cost_base': cost_base.quantize(Decimal('0.01')),
            'vat_retention': vat_retention.quantize(Decimal('0.01')),
            'isr_retention': isr_retention.quantize(Decimal('0.01')),
            'total_costs': total_costs.quantize(Decimal('0.01')),
            'break_even_price': break_even_price.quantize(Decimal('0.01')),
        }

    @staticmethod
    def calculate_recommended_price(
        break_even: Decimal,
        target_margin: Decimal
    ) -> Decimal:
        """
        Calculate recommended selling price based on target profit margin.

        Args:
            break_even: Break even price
            target_margin: Target profit margin (e.g., 0.25 for 25%)

        Returns:
            Recommended price with target margin
        """
        recommended = break_even / (Decimal('1') - target_margin)
        return recommended.quantize(Decimal('0.01'))

    @staticmethod
    def analyze_competitiveness(
        break_even: Decimal,
        current_mx_price: Decimal,
        config: 'BreakEvenAnalysisConfig'
    ) -> Dict[str, Any]:
        """
        Analyze if selling the product is competitive and feasible.

        Args:
            break_even: Calculated break even price
            current_mx_price: Current price on Amazon MX (or None)
            config: Analysis configuration

        Returns:
            Dictionary with:
            {
                'is_feasible': bool,
                'price_difference': Decimal,
                'potential_profit_margin': Decimal,
                'confidence_score': str ('HIGH', 'MEDIUM', 'LOW'),
                'meets_min_margin': bool,
                'meets_target_margin': bool
            }
        """
        if current_mx_price is None or current_mx_price <= 0:
            return {
                'is_feasible': False,
                'price_difference': Decimal('0.00'),
                'potential_profit_margin': Decimal('0.0000'),
                'confidence_score': 'LOW',
                'meets_min_margin': False,
                'meets_target_margin': False,
            }

        # Calculate price difference
        price_difference = current_mx_price - break_even

        # Calculate potential profit margin
        if current_mx_price > 0:
            potential_profit_margin = (price_difference / current_mx_price).quantize(Decimal('0.0001'))
        else:
            potential_profit_margin = Decimal('0.0000')

        # Check if margins are met
        meets_min_margin = potential_profit_margin >= config.min_profit_margin
        meets_target_margin = potential_profit_margin >= config.target_profit_margin

        # Determine feasibility
        is_feasible = meets_min_margin and price_difference > 0

        # Determine confidence score
        if meets_target_margin:
            confidence_score = 'HIGH'
        elif meets_min_margin:
            confidence_score = 'MEDIUM'
        else:
            confidence_score = 'LOW'

        return {
            'is_feasible': is_feasible,
            'price_difference': price_difference.quantize(Decimal('0.01')),
            'potential_profit_margin': potential_profit_margin,
            'confidence_score': confidence_score,
            'meets_min_margin': meets_min_margin,
            'meets_target_margin': meets_target_margin,
        }

    @staticmethod
    def get_average_shipping_cost(config: 'BreakEvenAnalysisConfig') -> Decimal:
        """
        Get average shipping cost from config.

        Args:
            config: Analysis configuration

        Returns:
            Average of min and max shipping costs
        """
        min_amount = config.fixed_shipping_min.amount
        max_amount = config.fixed_shipping_max.amount
        average = (min_amount + max_amount) / Decimal('2')
        return average.quantize(Decimal('0.01'))
