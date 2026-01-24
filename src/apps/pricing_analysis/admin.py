from django.contrib import admin
from django.utils.html import format_html
from django import forms
import re
from base.admin import BaseAdmin
from .models import (
    KeepaConfiguration,
    ExchangeRate,
    KeepaProductData,
    BrandRestriction,
    BreakEvenAnalysisConfig,
    PricingAnalysisResult,
    PricingAnalysisBatch,
    KeepaAPILog,
)


@admin.register(KeepaConfiguration)
class KeepaConfigurationAdmin(BaseAdmin):
    list_display = [
        'id',
        'api_key_display',
        'is_active',
        'daily_token_limit',
        'tokens_used_today',
        'last_reset_date',
    ]
    list_filter = ['is_active', 'last_reset_date']
    search_fields = ['api_key']
    readonly_fields = ['tokens_used_today', 'last_reset_date', 'created_at', 'updated_at']

    fieldsets = (
        ('API Configuration', {
            'fields': ('api_key', 'is_active')
        }),
        ('Token Management', {
            'fields': (
                'daily_token_limit',
                'tokens_used_today',
                'last_reset_date',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='API Key')
    def api_key_display(self, obj):
        """Display masked API key."""
        if obj.api_key:
            return f'{obj.api_key[:8]}...'
        return '-'

    @admin.display(description='Usage %')
    def token_usage_display(self, obj):
        """Display token usage as percentage."""
        if obj.daily_token_limit > 0:
            percentage = (obj.tokens_used_today / obj.daily_token_limit) * 100
            color = 'green' if percentage < 50 else ('orange' if percentage < 80 else 'red')
            return format_html(
                '<span style="color: {};">{:.1f}%</span>',
                color,
                percentage
            )
        return '-'


@admin.register(ExchangeRate)
class ExchangeRateAdmin(BaseAdmin):
    list_display = [
        'id',
        'from_currency',
        'to_currency',
        'rate',
        'is_active',
        'source',
    ]
    list_filter = ['is_active', 'source', 'from_currency', 'to_currency']
    search_fields = ['from_currency', 'to_currency']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Exchange Rate', {
            'fields': ('from_currency', 'to_currency', 'rate', 'is_active')
        }),
        ('Metadata', {
            'fields': ('source',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(KeepaProductData)
class KeepaProductDataAdmin(BaseAdmin):
    list_display = [
        'id',
        'asin',
        'marketplace',
        'title_display',
        'buy_box_price',
        'current_amazon_price',
        'is_available',
        'sync_successful',
        'last_synced_at',
    ]
    list_filter = [
        'marketplace',
        'is_available',
        'sync_successful',
        'last_synced_at',
    ]
    search_fields = ['asin', 'title', 'brand']
    readonly_fields = [
        'last_synced_at',
        'created_at',
        'updated_at',
        'raw_data',
    ]
    raw_id_fields = ['product']

    fieldsets = (
        ('Product Info', {
            'fields': (
                'product',
                'asin',
                'marketplace',
                'title',
                'brand',
                'product_category',
                'sales_rank',
                'is_available',
            )
        }),
        ('Prices', {
            'fields': (
                'buy_box_price',
                'current_amazon_price',
                'current_new_price',
                'avg_30_days_price',
                'avg_90_days_price',
            )
        }),
        ('Sync Status', {
            'fields': (
                'sync_successful',
                'sync_error_message',
                'last_synced_at',
            )
        }),
        ('Raw Data', {
            'fields': ('raw_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Title')
    def title_display(self, obj):
        """Display truncated title."""
        if obj.title:
            return obj.title[:60] + '...' if len(obj.title) > 60 else obj.title
        return '-'


@admin.register(BrandRestriction)
class BrandRestrictionAdmin(BaseAdmin):
    list_display = [
        'id',
        'name',
        'normalized_name',
        'is_allowed',
        'updated_at',
    ]
    list_filter = ['is_allowed']
    search_fields = ['name', 'normalized_name']
    readonly_fields = ['normalized_name', 'created_at', 'updated_at']
    ordering = ['name']


@admin.register(BreakEvenAnalysisConfig)
class BreakEvenAnalysisConfigAdmin(BaseAdmin):
    list_display = [
        'id',
        'name',
        'is_active',
        'import_admin_cost_rate',
        'iva_tax_rate',
        'marketplace_fee_rate',
        'min_profit_margin',
        'target_profit_margin',
    ]
    list_filter = ['is_active']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Configuration', {
            'fields': ('name', 'is_active')
        }),
        ('Tax Rates', {
            'fields': (
                'import_admin_cost_rate',
                'iva_tax_rate',
                'vat_retention_rate',
                'isr_retention_rate',
            )
        }),
        ('Marketplace Fees', {
            'fields': ('marketplace_fee_rate',)
        }),
        ('Shipping Costs', {
            'fields': (
                'fixed_shipping_min',
                'fixed_shipping_max',
            )
        }),
        ('Profit Margins', {
            'fields': (
                'min_profit_margin',
                'target_profit_margin',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['activate_config']

    def activate_config(self, request, queryset):
        """Activate selected config (only one can be active)."""
        if queryset.count() > 1:
            self.message_user(request, 'Please select only one config to activate.', level='error')
            return
        config = queryset.first()
        config.is_active = True
        config.save()
        self.message_user(request, f'Config "{config.name}" has been activated.')
    activate_config.short_description = 'Activate selected config'


@admin.register(PricingAnalysisResult)
class PricingAnalysisResultAdmin(BaseAdmin):
    list_display = [
        'id',
        'asin',
        'product_link',
        'is_available_usa',
        'is_feasible',
        'usa_cost',
        'break_even_price',
        'current_mx_amazon_price',
        'confidence_score',
    ]
    list_filter = [
        'is_feasible',
        'is_available_usa',
        'confidence_score',
        'usa_cost_source',
        'created_at',
    ]
    search_fields = ['asin', 'product__sku', 'product__title']
    readonly_fields = [
        'created_at',
        'updated_at',
    ]
    raw_id_fields = [
        'product',
        'usa_keepa_data',
        'mx_keepa_data',
        'analysis_config',
    ]

    fieldsets = (
        ('Product Info', {
            'fields': ('product', 'asin')
        }),
        ('Keepa Data', {
            'fields': ('usa_keepa_data', 'mx_keepa_data', 'analysis_config')
        }),
        ('Input Data', {
            'fields': (
                'usa_cost',
                'usa_cost_source',
                'exchange_rate',
                'current_mx_amazon_price',
            )
        }),
        ('Calculations', {
            'fields': (
                'cost_base_mxn',
                'vat_retention',
                'isr_retention',
                'shipping_cost_used',
                'break_even_price',
            )
        }),
        ('Results', {
            'fields': (
                'is_available_usa',
                'is_feasible',
                'recommended_price',
                'price_difference',
                'potential_profit_margin',
                'confidence_score',
                'analysis_notes',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Product')
    def product_link(self, obj):
        """Display link to product."""
        if obj.product:
            return format_html(
                '<a href="/admin/products/product/{}/change/">{}</a>',
                obj.product.id,
                obj.product.sku
            )
        return '-'

    @admin.display(description='Profit Margin')
    def potential_profit_margin_display(self, obj):
        """Display profit margin as percentage with color."""
        if obj.potential_profit_margin is not None:
            percentage = float(obj.potential_profit_margin) * 100
            color = 'green' if percentage >= 25 else ('orange' if percentage >= 10 else 'red')
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.2f}%</span>',
                color,
                percentage
            )
        return '-'


class PricingAnalysisBatchForm(forms.ModelForm):
    """Custom form for PricingAnalysisBatch with user-friendly ASIN input."""

    asins_input = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 10,
            'cols': 60,
            'placeholder': 'B07XYZ1234\nB08ABC5678\nB09DEF9012'
        }),
        required=True,
        label='ASINs',
        help_text='Ingrese ASINs separados por comas, espacios o nuevas líneas. Ejemplo: B07XYZ1234, B08ABC5678'
    )
    shipping_cost_mxn = forms.DecimalField(
        required=False,
        min_value=0,
        max_value=500,
        label='Costo de envío (MXN)',
        help_text='Opcional. Si no se especifica, usa el promedio de la configuración (70-100 MXN)',
        widget=forms.NumberInput(attrs={'placeholder': '85'})
    )
    execute_now = forms.BooleanField(
        required=False,
        initial=False,
        label='✓ Ejecutar análisis inmediatamente al guardar',
        help_text='Si se marca, el análisis comenzará automáticamente'
    )

    class Meta:
        model = PricingAnalysisBatch
        fields = ['name', 'asins_input', 'shipping_cost_mxn', 'execute_now']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si es edición de batch existente, poblar textarea desde JSON
        if self.instance.pk and self.instance.asins:
            self.fields['asins_input'].initial = '\n'.join(self.instance.asins)

        # Si batch ya fue procesado, deshabilitar edición
        if self.instance.pk and self.instance.status != 'PENDING':
            for field in self.fields:
                if field != 'name':  # Solo permitir cambiar nombre
                    self.fields[field].disabled = True

    def clean_asins_input(self):
        """Parse and validate ASINs."""
        raw_input = self.cleaned_data['asins_input']

        # Split por múltiples delimitadores: comas, espacios, newlines
        asins = re.split(r'[,\s\n\r]+', raw_input.strip())
        asins = [asin.strip().upper() for asin in asins if asin.strip()]

        if not asins:
            raise forms.ValidationError('Debe ingresar al menos un ASIN válido')

        # Validar formato ASIN (10 caracteres alfanuméricos, empieza con B)
        invalid_asins = []
        for asin in asins:
            if not (len(asin) == 10 and asin[0] == 'B' and asin.isalnum()):
                invalid_asins.append(asin)

        if invalid_asins:
            raise forms.ValidationError(
                f'ASINs inválidos (deben tener 10 caracteres, empezar con B): {", ".join(invalid_asins[:5])}'
                + (f' y {len(invalid_asins) - 5} más...' if len(invalid_asins) > 5 else '')
            )

        # Eliminar duplicados manteniendo orden
        seen = set()
        unique_asins = []
        for asin in asins:
            if asin not in seen:
                seen.add(asin)
                unique_asins.append(asin)

        if len(unique_asins) < len(asins):
            duplicates_count = len(asins) - len(unique_asins)
            self.add_error('asins_input', f'Se eliminaron {duplicates_count} ASINs duplicados')

        return unique_asins

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Convertir asins_input (list) a JSON
        instance.asins = self.cleaned_data['asins_input']
        instance.total_asins = len(instance.asins)
        instance.status = 'PENDING' if not instance.pk else instance.status

        if commit:
            instance.save()
        return instance


@admin.register(PricingAnalysisBatch)
class PricingAnalysisBatchAdmin(BaseAdmin):
    form = PricingAnalysisBatchForm

    list_display = [
        'id',
        'name',
        'successful_analyses',
        'unavailable_in_usa_count',
        'started_at',
        'completed_at',
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['name']
    ordering = ['-created_at']

    def get_readonly_fields(self, request, obj=None):
        """Make fields readonly based on batch status."""
        base_readonly = ['created_at', 'updated_at', 'error_log']

        if obj and obj.status != 'PENDING':
            # Batch already processed, everything readonly except name
            return base_readonly + [
                'status', 'total_asins', 'processed_asins',
                'successful_analyses', 'failed_analyses',
                'unavailable_in_usa_count', 'started_at', 'completed_at'
            ]
        return base_readonly + [
            'status', 'total_asins', 'processed_asins',
            'successful_analyses', 'failed_analyses',
            'unavailable_in_usa_count', 'started_at', 'completed_at'
        ]

    fieldsets = (
        ('Información del Batch', {
            'fields': ('name', 'asins_input', 'shipping_cost_mxn', 'execute_now'),
            'description': 'Ingrese los ASINs a analizar. Puede separarlos por comas, espacios o nuevas líneas.'
        }),
        ('Estado', {
            'fields': ('status',)
        }),
        ('Progreso', {
            'fields': (
                'total_asins',
                'processed_asins',
                'successful_analyses',
                'failed_analyses',
                'unavailable_in_usa_count',
            ),
            'classes': ('collapse',)
        }),
        ('Resultados', {
            'fields': ('results',),
            'classes': ('collapse',)
        }),
        ('Tiempos', {
            'fields': ('started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
        ('Log de Errores', {
            'fields': ('error_log',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    filter_horizontal = ['results']
    actions = ['execute_batch_analysis']

    def save_model(self, request, obj, form, change):
        """Handle execute_now checkbox."""
        super().save_model(request, obj, form, change)

        # Si execute_now está marcado, ejecutar análisis
        if form.cleaned_data.get('execute_now') and obj.status == 'PENDING':
            shipping_cost = form.cleaned_data.get('shipping_cost_mxn')
            self._execute_analysis(request, obj, shipping_cost)

    def execute_batch_analysis(self, request, queryset):
        """Admin action to execute batch analysis for PENDING batches."""
        # Filtrar solo batches PENDING
        pending_batches = queryset.filter(status='PENDING')

        if pending_batches.count() == 0:
            self.message_user(
                request,
                '⚠️ No hay batches con status PENDING seleccionados.',
                level='warning'
            )
            return

        if pending_batches.count() > 1:
            self.message_user(
                request,
                '❌ Por favor seleccione solo un batch a la vez para evitar exceder límites de API.',
                level='error'
            )
            return

        batch = pending_batches.first()
        self._execute_analysis(request, batch)

    execute_batch_analysis.short_description = '▶️ Ejecutar análisis de batch seleccionado'

    def _execute_analysis(self, request, batch, shipping_cost_mxn=None):
        """Internal method to execute batch analysis."""
        from apps.pricing_analysis.services.analysis_service import PricingAnalysisService
        from apps.pricing_analysis.services.exceptions import (
            ExchangeRateNotFoundError,
            AnalysisConfigNotFoundError,
            TokenLimitExceededError,
        )

        try:
            service = PricingAnalysisService()
            service.analyze_multiple_asins(
                asins=batch.asins,
                batch_name=batch.name,
                shipping_cost_mxn=shipping_cost_mxn
            )

            # Refresh para obtener los resultados actualizados
            batch.refresh_from_db()

            self.message_user(
                request,
                f'✅ Análisis completado exitosamente!\n'
                f'  • {batch.successful_analyses} análisis exitosos\n'
                f'  • {batch.failed_analyses} fallidos\n'
                f'  • {batch.unavailable_in_usa_count} no disponibles en USA',
                level='success'
            )

        except ExchangeRateNotFoundError:
            self.message_user(
                request,
                '❌ Error: No hay tipo de cambio USD→MXN configurado. '
                'Por favor configure uno en Pricing Analysis → Exchange Rates.',
                level='error'
            )
        except AnalysisConfigNotFoundError:
            self.message_user(
                request,
                '❌ Error: No hay configuración de análisis activa. '
                'Por favor configure una en Pricing Analysis → Break Even Analysis Configs.',
                level='error'
            )
        except TokenLimitExceededError as e:
            self.message_user(
                request,
                f'❌ Límite de tokens Keepa excedido: {str(e)}\n'
                'Espere hasta mañana o ajuste el límite en Keepa Configuration.',
                level='error'
            )
        except Exception as e:
            self.message_user(
                request,
                f'❌ Error inesperado: {str(e)}',
                level='error'
            )

    @admin.display(description='Status')
    def status_colored(self, obj):
        """Display status with color coding."""
        colors = {
            'PENDING': 'orange',
            'PROCESSING': 'blue',
            'COMPLETED': 'green',
            'FAILED': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )

    @admin.display(description='Progreso')
    def progress_display(self, obj):
        """Display progress as percentage with progress bar."""
        if obj.total_asins > 0:
            percentage = (obj.processed_asins / obj.total_asins) * 100
            bar_width = int(percentage)
            return format_html(
                '<div style="width: 150px; border: 1px solid #ddd; background: #f5f5f5;">'
                '<div style="width: {}%; background: #4CAF50; color: white; text-align: center; padding: 2px;">'
                '{}/{} ({:.1f}%)'
                '</div></div>',
                bar_width,
                obj.processed_asins,
                obj.total_asins,
                percentage
            )
        return '0/0'


@admin.register(KeepaAPILog)
class KeepaAPILogAdmin(BaseAdmin):
    list_display = [
        'id',
        'endpoint',
        'response_status',
        'status_display',
        'tokens_consumed',
        'execution_time_ms',
    ]
    list_filter = ['response_status', 'created_at']
    search_fields = ['endpoint', 'error_message']
    readonly_fields = [
        'endpoint',
        'request_params',
        'response_status',
        'response_data',
        'tokens_consumed',
        'error_message',
        'execution_time_ms',
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('Request', {
            'fields': ('endpoint', 'request_params')
        }),
        ('Response', {
            'fields': (
                'response_status',
                'response_data',
                'error_message',
            )
        }),
        ('Metrics', {
            'fields': ('tokens_consumed', 'execution_time_ms')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Status')
    def status_display(self, obj):
        """Display status with color."""
        if obj.response_status:
            if 200 <= obj.response_status < 300:
                color = 'green'
            elif 400 <= obj.response_status < 500:
                color = 'orange'
            else:
                color = 'red'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color,
                obj.response_status
            )
        return '-'

    def has_add_permission(self, request):
        """Don't allow manual creation of logs."""
        return False

    def has_change_permission(self, request, obj=None):
        """Don't allow editing logs."""
        return False
