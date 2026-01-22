from datetime import datetime
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from .models import PricingAnalysisResult


class PricingAnalysisResultDetailView(LoginRequiredMixin, DetailView):
    """
    Vista detallada para visualizar resultados de análisis de pricing.

    URL: /pricing-analysis/results/<int:pk>/
    Template: pricing_analysis/result_detail.html
    """
    model = PricingAnalysisResult
    template_name = 'pricing_analysis/result_detail.html'
    context_object_name = 'analysis'
    login_url = '/admin/login/'

    def get_queryset(self):
        """Optimiza queries con select_related."""
        return PricingAnalysisResult.objects.select_related(
            'product',
            'usa_keepa_data',
            'mx_keepa_data',
            'analysis_config'
        )

    def get_context_data(self, **kwargs):
        """Agrega datos adicionales al contexto del template."""
        context = super().get_context_data(**kwargs)
        analysis = self.object

        # Extraer historial de precios de Keepa
        context['price_history_data'] = self._extract_price_history(analysis.usa_keepa_data)

        # Calcular métricas adicionales para display
        context['metrics'] = self._calculate_display_metrics(analysis)

        # Configuración de badges de confianza
        context['confidence_badges'] = {
            'HIGH': {'class': 'success', 'icon': '✓', 'text': 'Alta Confianza'},
            'MEDIUM': {'class': 'warning', 'icon': '~', 'text': 'Confianza Media'},
            'LOW': {'class': 'danger', 'icon': '!', 'text': 'Baja Confianza'}
        }

        return context

    def _extract_price_history(self, keepa_data):
        """
        Extrae datos históricos de precios de Keepa para Chart.js.

        Args:
            keepa_data: KeepaProductData object con raw_data

        Returns:
            dict con labels (fechas), prices (valores), currency, has_data
        """
        if not keepa_data or not keepa_data.raw_data:
            return {
                'labels': [],
                'prices': [],
                'currency': 'USD',
                'has_data': False
            }

        raw = keepa_data.raw_data

        # Verificar que existe el array de precios BUY_BOX_SHIPPING
        if 'csv' not in raw or not isinstance(raw['csv'], list) or len(raw['csv']) < 19:
            return {
                'labels': [],
                'prices': [],
                'currency': 'USD',
                'has_data': False
            }

        # csv[18] = BUY_BOX_SHIPPING
        buy_box_data = raw['csv'][18]

        if not buy_box_data or len(buy_box_data) == 0:
            return {
                'labels': [],
                'prices': [],
                'currency': 'USD',
                'has_data': False
            }

        # Keepa Epoch: 21 Dec 2011 00:00 UTC
        KEEPA_EPOCH_MS = 1324339200000

        labels = []
        prices = []

        # Array formato: [timestamp_minutes, price_cents, timestamp_minutes, price_cents, ...]
        for i in range(0, len(buy_box_data), 2):
            if i + 1 < len(buy_box_data):
                keepa_minutes = buy_box_data[i]
                price_keepa = buy_box_data[i + 1]

                # -1 significa sin datos
                if price_keepa is None or price_keepa == -1:
                    continue

                try:
                    # Convertir timestamp de Keepa a fecha
                    timestamp_ms = KEEPA_EPOCH_MS + (keepa_minutes * 60 * 1000)
                    date = datetime.fromtimestamp(timestamp_ms / 1000)

                    # Convertir precio de centavos a USD
                    price_usd = price_keepa / 100.0

                    labels.append(date.strftime('%Y-%m-%d'))
                    prices.append(round(price_usd, 2))
                except (ValueError, TypeError, OverflowError):
                    # Ignorar valores inválidos
                    continue

        # Limitar a últimos 90 puntos de datos
        if len(labels) > 90:
            labels = labels[-90:]
            prices = prices[-90:]

        return {
            'labels': labels,
            'prices': prices,
            'currency': 'USD',
            'has_data': len(prices) > 0
        }

    def _calculate_display_metrics(self, analysis):
        """
        Calcula métricas adicionales para display en el template.

        Args:
            analysis: PricingAnalysisResult object

        Returns:
            dict con métricas calculadas
        """
        metrics = {}

        # Porcentaje de ganancia potencial
        if analysis.potential_profit_margin:
            metrics['profit_percentage'] = float(analysis.potential_profit_margin) * 100
        else:
            metrics['profit_percentage'] = 0.0

        # Diferencia porcentual break even vs precio MX
        if (analysis.break_even_price and
            analysis.current_mx_amazon_price and
            analysis.break_even_price.amount > 0):

            diff = analysis.current_mx_amazon_price.amount - analysis.break_even_price.amount
            percentage = (diff / analysis.break_even_price.amount) * 100
            metrics['price_diff_percentage'] = round(float(percentage), 2)
        else:
            metrics['price_diff_percentage'] = 0.0

        # Total de retenciones (IVA + ISR)
        if analysis.vat_retention and analysis.isr_retention:
            total_retenciones = analysis.vat_retention.amount + analysis.isr_retention.amount
            metrics['total_retenciones'] = round(float(total_retenciones), 2)
        else:
            metrics['total_retenciones'] = 0.0

        # Multiplicador de markup (precio recomendado / break even)
        if (analysis.recommended_price and
            analysis.break_even_price and
            analysis.break_even_price.amount > 0):

            multiplier = analysis.recommended_price.amount / analysis.break_even_price.amount
            metrics['markup_multiplier'] = round(float(multiplier), 2)
        else:
            metrics['markup_multiplier'] = 1.0

        return metrics
