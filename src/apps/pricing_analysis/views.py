from datetime import datetime
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
import csv
import io
from django.urls import reverse
from django.views.generic import DetailView, ListView
from .models import PricingAnalysisResult, BrandRestriction
from .services.analysis_service import PricingAnalysisService
from .forms import BrandRestrictionForm, BrandRestrictionToggleForm, BrandRestrictionUploadForm

IMPUESTOS_AMERICANOS = Decimal('1.0825')


def _get_usa_tax_multiplier(analysis: PricingAnalysisResult) -> Decimal:
    category = ''
    if analysis.usa_keepa_data and analysis.usa_keepa_data.product_category:
        category = analysis.usa_keepa_data.product_category
    elif analysis.product and getattr(analysis.product, 'category', None):
        category = analysis.product.category

    category = category.strip().lower()
    if category in {'health and household', 'health & household'}:
        return Decimal('1.0000')

    return IMPUESTOS_AMERICANOS


def _normalize_brand(brand: str) -> str:
    return (brand or '').strip().lower()


def _get_brand_status(analysis: PricingAnalysisResult) -> dict:
    brand = ''
    if analysis.usa_keepa_data and analysis.usa_keepa_data.brand:
        brand = analysis.usa_keepa_data.brand
    elif analysis.product and getattr(analysis.product, 'brand', None):
        brand = analysis.product.brand

    normalized = _normalize_brand(brand)
    if not normalized:
        return {'brand': '', 'is_allowed': True, 'is_blocked': False}

    restriction = BrandRestriction.objects.filter(normalized_name=normalized).first()
    if restriction is None:
        return {'brand': brand, 'is_allowed': True, 'is_blocked': False}

    return {
        'brand': brand,
        'is_allowed': restriction.is_allowed,
        'is_blocked': not restriction.is_allowed,
    }


def _get_first_image_url(analysis: PricingAnalysisResult) -> str:
    """Return first product image URL from Keepa raw data if available."""
    raw = None
    if analysis.usa_keepa_data and analysis.usa_keepa_data.raw_data:
        raw = analysis.usa_keepa_data.raw_data
    elif analysis.mx_keepa_data and analysis.mx_keepa_data.raw_data:
        raw = analysis.mx_keepa_data.raw_data

    if not raw:
        return ''

    images_csv = raw.get('imagesCSV', '')
    if not images_csv:
        return ''

    first = images_csv.split(',')[0].strip()
    if not first:
        return ''

    if not first.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        first = f'{first}.jpg'

    return f'https://images-na.ssl-images-amazon.com/images/I/{first}'


def _get_stat_value(raw_data: dict, keys: list[str]):
    if not raw_data:
        return None
    stats = raw_data.get('stats', {})
    for key in keys:
        value = stats.get(key)
        if value not in (None, '', 0):
            return value
    return None


class PricingAnalysisPanoramaView(LoginRequiredMixin, ListView):
    """
    Vista panoramica para revisar analisis en forma de tabla.

    URL: /pricing-analysis/panorama/
    Template: pricing_analysis/panorama.html
    """
    model = PricingAnalysisResult
    template_name = 'pricing_analysis/panorama.html'
    context_object_name = 'analyses'
    login_url = '/admin/login/'

    def get_queryset(self):
        """Optimiza queries con select_related."""
        return PricingAnalysisResult.objects.select_related(
            'product',
            'usa_keepa_data',
            'analysis_config',
        )

    def get_context_data(self, **kwargs):
        """Agrega datos calculados para columnas dinamicas."""
        context = super().get_context_data(**kwargs)
        rows = []

        for analysis in context['analyses']:
            config = analysis.analysis_config
            usa_cost_mxn = None
            import_fees = None
            import_taxes = None
            import_taxes_usd = None
            brand_status = _get_brand_status(analysis)
            image_url = _get_first_image_url(analysis)

            if analysis.usa_cost and analysis.exchange_rate:
                usa_tax_multiplier = _get_usa_tax_multiplier(analysis)
                usa_cost_base = analysis.usa_cost.amount * analysis.exchange_rate
                usa_cost_mxn = (usa_cost_base * usa_tax_multiplier).quantize(Decimal('0.01'))

                if config:
                    import_fees = (usa_cost_mxn * config.import_admin_cost_rate).quantize(Decimal('0.01'))
                    import_taxes = (import_fees * config.iva_tax_rate).quantize(Decimal('0.01'))
                    if analysis.exchange_rate:
                        import_taxes_usd = (import_taxes / analysis.exchange_rate).quantize(Decimal('0.01'))

            retenciones = None
            if analysis.vat_retention and analysis.isr_retention:
                retenciones = (analysis.vat_retention.amount + analysis.isr_retention.amount).quantize(Decimal('0.01'))

            margen_pct = None
            if analysis.potential_profit_margin is not None:
                margen_pct = (analysis.potential_profit_margin * Decimal('100')).quantize(Decimal('0.01'))

            precio_minimo = None
            precio_maximo = None
            if analysis.break_even_price:
                precio_minimo = (analysis.break_even_price.amount * Decimal('1.25')).quantize(Decimal('0.01'))
                precio_maximo = (analysis.break_even_price.amount * Decimal('1.50')).quantize(Decimal('0.01'))

            retenciones_actual = None
            retenciones_min = None
            retenciones_max = None
            if config and analysis.break_even_price:
                retention_factor = (
                    (config.vat_retention_rate + config.isr_retention_rate) /
                    (Decimal('1') + config.iva_tax_rate)
                )
                if analysis.current_mx_amazon_price and analysis.current_mx_amazon_price.amount:
                    retenciones_actual = (analysis.current_mx_amazon_price.amount * retention_factor).quantize(Decimal('0.01'))
                if precio_minimo:
                    retenciones_min = (precio_minimo * retention_factor).quantize(Decimal('0.01'))
                if precio_maximo:
                    retenciones_max = (precio_maximo * retention_factor).quantize(Decimal('0.01'))

            utilidad_neta_actual = None
            margen_neto_actual = None
            if config and analysis.break_even_price and analysis.current_mx_amazon_price and analysis.current_mx_amazon_price.amount:
                retention_factor = (
                    (config.vat_retention_rate + config.isr_retention_rate) /
                    (Decimal('1') + config.iva_tax_rate)
                )
                be_amount = analysis.break_even_price.amount
                break_even_base = be_amount * (Decimal('1') - retention_factor)
                current_price = analysis.current_mx_amazon_price.amount
                utilidad_neta_actual = (current_price - break_even_base - (current_price * retention_factor)).quantize(Decimal('0.01'))
                margen_neto_actual = (utilidad_neta_actual / current_price * Decimal('100')).quantize(Decimal('0.01'))

            mx_bought = (
                _get_stat_value(analysis.mx_keepa_data.raw_data, ['buyBoxCount', 'buyBoxCount30'])
                if analysis.mx_keepa_data and analysis.mx_keepa_data.raw_data else None
            )
            mx_rank = analysis.mx_keepa_data.sales_rank if analysis.mx_keepa_data else None
            mx_drops = (
                _get_stat_value(analysis.mx_keepa_data.raw_data, ['salesRankDrops30'])
                if analysis.mx_keepa_data and analysis.mx_keepa_data.raw_data else None
            )

            rows.append({
                'id': analysis.id,
                'asin': analysis.asin,
                'detail_url': reverse('pricing_analysis:result_detail', args=[analysis.pk]),
                'image_url': image_url,
                'brand': analysis.usa_keepa_data.brand if analysis.usa_keepa_data else None,
                'category': analysis.usa_keepa_data.product_category if analysis.usa_keepa_data else None,
                'bought_past_month_us': _get_stat_value(analysis.usa_keepa_data.raw_data, ['buyBoxCount', 'buyBoxCount30']) if analysis.usa_keepa_data and analysis.usa_keepa_data.raw_data else None,
                'sales_rank_us': analysis.usa_keepa_data.sales_rank if analysis.usa_keepa_data else None,
                'bought_past_month_mx': mx_bought,
                'sales_rank_mx': mx_rank,
                'drops_30_us': _get_stat_value(analysis.usa_keepa_data.raw_data, ['salesRankDrops30']) if analysis.usa_keepa_data and analysis.usa_keepa_data.raw_data else None,
                'drops_30_mx': mx_drops,
                'precio_mx': analysis.current_mx_amazon_price.amount if analysis.current_mx_amazon_price else None,
                'precio_usa_usd': analysis.usa_cost.amount if analysis.usa_cost else None,
                'taxes': import_taxes_usd,
                'tc': analysis.exchange_rate,
                'be': analysis.break_even_price.amount if analysis.break_even_price else None,
                'precio_usa_mxn': usa_cost_mxn,
                'importacion': import_fees,
                'envio': analysis.shipping_cost_used.amount if analysis.shipping_cost_used else None,
                'retenciones': retenciones,
                'retenciones_actual': retenciones_actual,
                'retenciones_min': retenciones_min,
                'retenciones_max': retenciones_max,
                'utilidad_neta_actual': utilidad_neta_actual,
                'margen_neto_actual': margen_neto_actual,
                'vendible': analysis.is_feasible and analysis.is_available_usa,
                'disponible_usa': analysis.is_available_usa,
                'brand_blocked': brand_status['is_blocked'],
                'brand_name': brand_status['brand'],
                'margen_pct': margen_pct,
                'precio_minimo': precio_minimo,
                'precio_maximo': precio_maximo,
            })

        context['rows'] = rows
        return context


class BrandRestrictionListView(LoginRequiredMixin, View):
    template_name = 'pricing_analysis/brand_restrictions.html'
    login_url = '/admin/login/'

    def get(self, request):
        restrictions = BrandRestriction.objects.order_by('name')
        context = {
            'restrictions': restrictions,
            'brand_form': BrandRestrictionForm(),
            'toggle_form': BrandRestrictionToggleForm(),
            'upload_form': BrandRestrictionUploadForm(),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        action = request.POST.get('action', '')

        if action == 'add':
            form = BrandRestrictionForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                is_allowed = bool(form.cleaned_data.get('is_allowed'))
                normalized = _normalize_brand(name)
                BrandRestriction.objects.update_or_create(
                    normalized_name=normalized,
                    defaults={'name': name, 'is_allowed': is_allowed}
                )

        elif action == 'update':
            form = BrandRestrictionToggleForm(request.POST)
            if form.is_valid():
                brand_id = form.cleaned_data['brand_id']
                is_allowed = bool(form.cleaned_data.get('is_allowed'))
                BrandRestriction.objects.filter(id=brand_id).update(is_allowed=is_allowed)

        elif action == 'upload':
            form = BrandRestrictionUploadForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data['file']
                raw = file.read()
                data = None
                for encoding in ('utf-8-sig', 'utf-8', 'cp1252', 'latin-1'):
                    try:
                        data = raw.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                if data is None:
                    return redirect(request.path)
                stream = io.StringIO(data)
                reader = csv.reader(stream)
                rows = list(reader)
                if not rows:
                    return redirect(request.path)

                header = [c.strip().lower() for c in rows[0]]
                has_header = any(h in {'brand', 'name', 'allowed', 'is_allowed'} for h in header)

                allowed_values = {'1', 'true', 'yes', 'si', 'allowed', 'permitido'}

                if has_header:
                    stream.seek(0)
                    dict_reader = csv.DictReader(stream)
                    for row in dict_reader:
                        brand = (row.get('brand') or row.get('name') or '').strip()
                        if not brand:
                            continue
                        allowed_raw = (row.get('allowed') or row.get('is_allowed') or '').strip().lower()
                        is_allowed = allowed_raw in allowed_values
                        normalized = _normalize_brand(brand)
                        BrandRestriction.objects.update_or_create(
                            normalized_name=normalized,
                            defaults={'name': brand, 'is_allowed': is_allowed}
                        )
                else:
                    for row in rows:
                        if not row:
                            continue
                        brand = (row[0] or '').strip()
                        if not brand:
                            continue
                        is_allowed = False
                        if len(row) > 1:
                            is_allowed = (row[1] or '').strip().lower() in allowed_values
                        normalized = _normalize_brand(brand)
                        BrandRestriction.objects.update_or_create(
                            normalized_name=normalized,
                            defaults={'name': brand, 'is_allowed': is_allowed}
                        )

        return redirect(request.path)


class PricingAnalysisBatchView(LoginRequiredMixin, View):
    template_name = 'pricing_analysis/batch_analyze.html'
    login_url = '/admin/login/'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        asin_input = request.POST.get('asins', '')
        batch_name = request.POST.get('batch_name', '').strip() or 'Batch'
        shipping_raw = request.POST.get('shipping_cost_mxn', '').strip()

        asins = []
        for token in asin_input.replace(',', ' ').split():
            clean = token.strip().upper()
            if clean:
                asins.append(clean)

        if not asins:
            return render(request, self.template_name, {
                'error': 'No se encontraron ASINs validos.',
                'batch_name': batch_name,
                'asins': asin_input,
                'shipping_cost_mxn': shipping_raw,
            })

        shipping_cost = None
        if shipping_raw:
            try:
                shipping_cost = Decimal(shipping_raw)
            except Exception:
                return render(request, self.template_name, {
                    'error': 'Costo de envio invalido.',
                    'batch_name': batch_name,
                    'asins': asin_input,
                    'shipping_cost_mxn': shipping_raw,
                })

        service = PricingAnalysisService()
        batch = service.analyze_multiple_asins(
            asins=asins,
            batch_name=batch_name,
            shipping_cost_mxn=shipping_cost,
        )

        return redirect('pricing_analysis:panorama')


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

        # Estado de marca
        context['brand_status'] = _get_brand_status(analysis)
        context['image_url'] = _get_first_image_url(analysis)
        context['bought_past_month_us'] = (
            _get_stat_value(analysis.usa_keepa_data.raw_data, ['buyBoxCount', 'buyBoxCount30'])
            if analysis.usa_keepa_data and analysis.usa_keepa_data.raw_data else None
        )
        context['sales_rank_us'] = analysis.usa_keepa_data.sales_rank if analysis.usa_keepa_data else None
        context['bought_past_month_mx'] = (
            _get_stat_value(analysis.mx_keepa_data.raw_data, ['buyBoxCount', 'buyBoxCount30'])
            if analysis.mx_keepa_data and analysis.mx_keepa_data.raw_data else None
        )
        context['sales_rank_mx'] = analysis.mx_keepa_data.sales_rank if analysis.mx_keepa_data else None
        context['drops_30_us'] = (
            _get_stat_value(analysis.usa_keepa_data.raw_data, ['salesRankDrops30'])
            if analysis.usa_keepa_data and analysis.usa_keepa_data.raw_data else None
        )
        context['drops_30_mx'] = (
            _get_stat_value(analysis.mx_keepa_data.raw_data, ['salesRankDrops30'])
            if analysis.mx_keepa_data and analysis.mx_keepa_data.raw_data else None
        )
        context['sales_rank'] = analysis.usa_keepa_data.sales_rank if analysis.usa_keepa_data else None

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

        # Diferencia porcentual break even vs precio MX
        if (analysis.break_even_price and
            analysis.current_mx_amazon_price and
            analysis.break_even_price.amount > 0):

            diff = analysis.current_mx_amazon_price.amount - analysis.break_even_price.amount
            percentage = (diff / analysis.break_even_price.amount) * 100
            metrics['price_diff_percentage'] = round(float(percentage), 2)
        else:
            metrics['price_diff_percentage'] = 0.0

        # Margen actual sobre BE (porcentaje) usando retenciones con precio actual
        if analysis.potential_profit_margin is not None:
            metrics['current_margin_percentage'] = round(float(analysis.potential_profit_margin) * 100, 2)
        else:
            metrics['current_margin_percentage'] = 0.0

        # Precios recomendados min/max (25% y 50% sobre BE)
        if analysis.break_even_price and analysis.break_even_price.amount:
            be_amount = analysis.break_even_price.amount
            metrics['recommended_min'] = round(float(be_amount * Decimal('1.25')), 2)
            metrics['recommended_max'] = round(float(be_amount * Decimal('1.50')), 2)
        else:
            metrics['recommended_min'] = 0.0
            metrics['recommended_max'] = 0.0
            be_amount = None

        # Retenciones sobre precio actual, min y max
        if analysis.analysis_config and be_amount:
            config = analysis.analysis_config
            retention_factor = (
                (config.vat_retention_rate + config.isr_retention_rate) /
                (Decimal('1') + config.iva_tax_rate)
            )
            if analysis.current_mx_amazon_price and analysis.current_mx_amazon_price.amount:
                current_price = analysis.current_mx_amazon_price.amount
                metrics['retention_current'] = round(float(current_price * retention_factor), 2)
                metrics['retention_current_vat'] = round(
                    float(current_price / (Decimal('1') + config.iva_tax_rate) * config.vat_retention_rate), 2
                )
                metrics['retention_current_isr'] = round(
                    float(current_price / (Decimal('1') + config.iva_tax_rate) * config.isr_retention_rate), 2
                )
            else:
                current_price = None
                metrics['retention_current'] = 0.0
                metrics['retention_current_vat'] = 0.0
                metrics['retention_current_isr'] = 0.0
            metrics['retention_min'] = round(float(be_amount * Decimal('1.25') * retention_factor), 2)
            metrics['retention_max'] = round(float(be_amount * Decimal('1.50') * retention_factor), 2)

            if current_price:
                break_even_base = be_amount * (Decimal('1') - retention_factor)
                net_profit = current_price - break_even_base - (current_price * retention_factor)
                metrics['net_profit_current'] = round(float(net_profit), 2)
                metrics['net_margin_current'] = round(float(net_profit / current_price) * 100, 2)
            else:
                metrics['net_profit_current'] = 0.0
                metrics['net_margin_current'] = 0.0
        else:
            metrics['retention_current'] = 0.0
            metrics['retention_current_vat'] = 0.0
            metrics['retention_current_isr'] = 0.0
            metrics['retention_min'] = 0.0
            metrics['retention_max'] = 0.0
            metrics['net_profit_current'] = 0.0
            metrics['net_margin_current'] = 0.0

        # Porcentaje de ganancia potencial (neto sobre precio actual)
        metrics['profit_percentage'] = metrics['net_margin_current']

        # Total de retenciones (IVA + ISR)
        if analysis.vat_retention and analysis.isr_retention:
            total_retenciones = analysis.vat_retention.amount + analysis.isr_retention.amount
            metrics['total_retenciones'] = round(float(total_retenciones), 2)
        else:
            metrics['total_retenciones'] = 0.0

        # Desglose de importacion
        if analysis.analysis_config and analysis.usa_cost and analysis.exchange_rate:
            config = analysis.analysis_config
            usa_tax_multiplier = _get_usa_tax_multiplier(analysis)
            usa_cost_mxn = analysis.usa_cost.amount * analysis.exchange_rate * usa_tax_multiplier
            import_fees = usa_cost_mxn * config.import_admin_cost_rate
            import_iva = import_fees * config.iva_tax_rate
            metrics['import_fees'] = round(float(import_fees), 2)
            metrics['import_iva'] = round(float(import_iva), 2)
            metrics['import_total'] = round(float(import_fees + import_iva), 2)
        else:
            metrics['import_fees'] = 0.0
            metrics['import_iva'] = 0.0
            metrics['import_total'] = 0.0

        # Multiplicador de markup (precio recomendado / break even)
        if (analysis.recommended_price and
            analysis.break_even_price and
            analysis.break_even_price.amount > 0):

            multiplier = analysis.recommended_price.amount / analysis.break_even_price.amount
            metrics['markup_multiplier'] = round(float(multiplier), 2)
        else:
            metrics['markup_multiplier'] = 1.0

        return metrics
