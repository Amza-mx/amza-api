from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from djmoney.models.fields import MoneyField
from decimal import Decimal
from base.models import BaseModel


class KeepaConfiguration(BaseModel):
    """Almacena credenciales y configuración de Keepa API."""

    api_key = models.CharField(
        max_length=255,
        help_text='Clave API de Keepa'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Configuración activa'
    )
    daily_token_limit = models.PositiveIntegerField(
        default=5000,
        help_text='Límite de tokens diarios'
    )
    tokens_used_today = models.PositiveIntegerField(
        default=0,
        help_text='Contador de tokens usados hoy'
    )
    last_reset_date = models.DateField(
        auto_now_add=True,
        help_text='Fecha del último reset de tokens'
    )

    class Meta:
        verbose_name = 'Keepa Configuration'
        verbose_name_plural = 'Keepa Configurations'
        ordering = ['-is_active', '-created_at']

    def __str__(self):
        return f'Keepa Config ({self.api_key[:8]}...) - {"Active" if self.is_active else "Inactive"}'

    def reset_tokens_if_needed(self):
        """Reset token counter if date has changed."""
        today = timezone.now().date()
        if self.last_reset_date < today:
            self.tokens_used_today = 0
            self.last_reset_date = today
            self.save(update_fields=['tokens_used_today', 'last_reset_date'])

    def can_consume_tokens(self, required_tokens):
        """Check if there are enough tokens available."""
        self.reset_tokens_if_needed()
        return (self.tokens_used_today + required_tokens) <= self.daily_token_limit

    def consume_tokens(self, tokens):
        """Consume tokens and update counter."""
        self.reset_tokens_if_needed()
        self.tokens_used_today += tokens
        self.save(update_fields=['tokens_used_today'])


class ExchangeRate(BaseModel):
    """Almacena tipos de cambio USD→MXN."""

    from_currency = models.CharField(
        max_length=3,
        default='USD',
        help_text='Moneda origen'
    )
    to_currency = models.CharField(
        max_length=3,
        default='MXN',
        help_text='Moneda destino'
    )
    rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
        help_text='Tasa de cambio'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Si es la tasa activa'
    )
    source = models.CharField(
        max_length=20,
        choices=[
            ('manual', 'Manual'),
            ('api', 'API'),
        ],
        default='manual',
        help_text='Origen del tipo de cambio'
    )

    class Meta:
        verbose_name = 'Exchange Rate'
        verbose_name_plural = 'Exchange Rates'
        ordering = ['-is_active', '-created_at']
        indexes = [
            models.Index(fields=['from_currency', 'to_currency', 'is_active']),
        ]

    def __str__(self):
        return f'{self.from_currency}→{self.to_currency}: {self.rate} ({self.get_source_display()})'

    @classmethod
    def get_active_usd_mxn_rate(cls):
        """Get the active USD to MXN exchange rate."""
        try:
            rate = cls.objects.get(
                from_currency='USD',
                to_currency='MXN',
                is_active=True
            )
            return rate.rate
        except cls.DoesNotExist:
            raise ValueError(
                'No active USD→MXN exchange rate found. '
                'Please configure one in the admin panel.'
            )


class KeepaProductData(BaseModel):
    """Datos de productos obtenidos de Keepa API."""

    MARKETPLACE_CHOICES = [
        ('US', 'Amazon USA'),
        ('MX', 'Amazon MX'),
    ]

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='keepa_data',
        help_text='Producto asociado (puede ser null si es temporal)'
    )
    asin = models.CharField(
        max_length=20,
        db_index=True,
        help_text='ASIN del producto'
    )
    marketplace = models.CharField(
        max_length=2,
        choices=MARKETPLACE_CHOICES,
        help_text='Marketplace de Amazon'
    )

    # Precios
    current_amazon_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Precio actual de Amazon'
    )
    buy_box_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Precio de Buy Box (prioritario para USA)'
    )
    current_new_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Precio actual nuevo'
    )
    avg_30_days_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Precio promedio 30 días'
    )
    avg_90_days_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Precio promedio 90 días'
    )

    # Metadatos
    title = models.CharField(
        max_length=500,
        blank=True,
        help_text='Título del producto'
    )
    brand = models.CharField(
        max_length=255,
        blank=True,
        help_text='Marca'
    )
    product_category = models.CharField(
        max_length=255,
        blank=True,
        help_text='Categoría del producto'
    )
    sales_rank = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Sales rank en su categoría'
    )
    is_available = models.BooleanField(
        default=True,
        help_text='Si el producto está disponible'
    )

    # Data cruda y sync
    raw_data = models.JSONField(
        default=dict,
        blank=True,
        help_text='Respuesta completa de Keepa para debugging'
    )
    last_synced_at = models.DateTimeField(
        auto_now=True,
        help_text='Última sincronización exitosa'
    )
    sync_successful = models.BooleanField(
        default=True,
        help_text='Si la sincronización fue exitosa'
    )
    sync_error_message = models.TextField(
        blank=True,
        help_text='Mensaje de error si hubo problema en sync'
    )

    class Meta:
        verbose_name = 'Keepa Product Data'
        verbose_name_plural = 'Keepa Product Data'
        ordering = ['-last_synced_at']
        constraints = [
            models.UniqueConstraint(
                fields=['asin', 'marketplace'],
                name='unique_asin_marketplace'
            )
        ]
        indexes = [
            models.Index(fields=['asin', 'marketplace']),
            models.Index(fields=['sync_successful', '-last_synced_at']),
        ]

    def __str__(self):
        return f'{self.asin} ({self.get_marketplace_display()}) - {self.title[:50]}'


class BrandRestriction(BaseModel):
    """Marca con permiso o bloqueo de venta."""

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text='Nombre de la marca'
    )
    normalized_name = models.CharField(
        max_length=255,
        unique=True,
        help_text='Nombre normalizado para matching'
    )
    is_allowed = models.BooleanField(
        default=False,
        help_text='Si la marca esta permitida para venta'
    )

    class Meta:
        verbose_name = 'Brand Restriction'
        verbose_name_plural = 'Brand Restrictions'
        ordering = ['name']
        indexes = [
            models.Index(fields=['normalized_name']),
        ]

    def save(self, *args, **kwargs):
        self.normalized_name = (self.name or '').strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        status = 'Allowed' if self.is_allowed else 'Blocked'
        return f'{self.name} ({status})'


class BreakEvenAnalysisConfig(BaseModel):
    """Configuración de parámetros del análisis (permite ajustar sin cambiar código)."""

    name = models.CharField(
        max_length=100,
        help_text='Nombre de la configuración'
    )
    is_active = models.BooleanField(
        default=False,
        help_text='Configuración activa'
    )

    # Tasas
    import_admin_cost_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal('0.2000'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('1'))],
        help_text='Tasa de costos administrativos de importación (default: 0.20 = 20%)'
    )
    iva_tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal('0.1600'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('1'))],
        help_text='Tasa de IVA (default: 0.16 = 16%)'
    )
    vat_retention_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal('0.0800'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('1'))],
        help_text='Tasa de retención de IVA (default: 0.08 = 8%)'
    )
    isr_retention_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal('0.0250'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('1'))],
        help_text='Tasa de retención ISR (default: 0.025 = 2.5%)'
    )
    marketplace_fee_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal('0.1500'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('1'))],
        help_text='Tasa de comisión del marketplace (default: 0.15 = 15%)'
    )

    # Rangos de envío
    fixed_shipping_min = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency='MXN',
        default=Decimal('70.00'),
        help_text='Costo mínimo de envío en MXN'
    )
    fixed_shipping_max = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency='MXN',
        default=Decimal('100.00'),
        help_text='Costo máximo de envío en MXN'
    )

    # Márgenes objetivo
    min_profit_margin = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal('0.1000'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('1'))],
        help_text='Margen mínimo de ganancia (default: 0.10 = 10%)'
    )
    target_profit_margin = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal('0.2500'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('1'))],
        help_text='Margen objetivo de ganancia (default: 0.25 = 25%)'
    )

    class Meta:
        verbose_name = 'Break Even Analysis Config'
        verbose_name_plural = 'Break Even Analysis Configs'
        ordering = ['-is_active', '-created_at']

    def __str__(self):
        return f'{self.name} {"(Active)" if self.is_active else ""}'

    def save(self, *args, **kwargs):
        """Ensure only one config is active at a time."""
        if self.is_active:
            BreakEvenAnalysisConfig.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active_config(cls):
        """Get the active configuration."""
        try:
            return cls.objects.get(is_active=True)
        except cls.DoesNotExist:
            raise ValueError(
                'No active Break Even Analysis Config found. '
                'Please configure one in the admin panel.'
            )


class PricingAnalysisResult(BaseModel):
    """Resultado de cada análisis de pricing."""

    USA_COST_SOURCE_CHOICES = [
        ('buy_box', 'Buy Box Price'),
        ('amazon', 'Amazon Price'),
        ('unavailable', 'Unavailable'),
    ]

    CONFIDENCE_SCORE_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='pricing_analyses',
        help_text='Producto analizado'
    )
    asin = models.CharField(
        max_length=20,
        db_index=True,
        help_text='ASIN (redundante para queries rápidas)'
    )
    usa_keepa_data = models.ForeignKey(
        'KeepaProductData',
        on_delete=models.SET_NULL,
        null=True,
        related_name='usa_analyses',
        help_text='Datos de Keepa USA'
    )
    mx_keepa_data = models.ForeignKey(
        'KeepaProductData',
        on_delete=models.SET_NULL,
        null=True,
        related_name='mx_analyses',
        help_text='Datos de Keepa MX'
    )
    analysis_config = models.ForeignKey(
        'BreakEvenAnalysisConfig',
        on_delete=models.SET_NULL,
        null=True,
        help_text='Configuración utilizada'
    )

    # Inputs capturados
    usa_cost = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency='USD',
        null=True,
        blank=True,
        help_text='Precio usado de Keepa (USD)'
    )
    usa_cost_source = models.CharField(
        max_length=20,
        choices=USA_COST_SOURCE_CHOICES,
        default='unavailable',
        help_text='Fuente del precio USA'
    )
    exchange_rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text='Tipo de cambio usado'
    )
    current_mx_amazon_price = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency='MXN',
        null=True,
        blank=True,
        help_text='Precio actual en Amazon MX'
    )

    # Cálculos intermedios
    cost_base_mxn = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency='MXN',
        null=True,
        blank=True,
        help_text='Cost base después de import + IVA'
    )
    vat_retention = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency='MXN',
        null=True,
        blank=True,
        help_text='Retención de IVA (8% de cost base)'
    )
    isr_retention = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency='MXN',
        null=True,
        blank=True,
        help_text='Retención ISR (2.5% de cost base)'
    )
    shipping_cost_used = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency='MXN',
        null=True,
        blank=True,
        help_text='Costo de envío usado en el cálculo'
    )
    break_even_price = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency='MXN',
        null=True,
        blank=True,
        help_text='Precio de Break Even calculado'
    )

    # Resultados
    is_feasible = models.BooleanField(
        default=False,
        help_text='Si es viable vender el producto'
    )
    is_available_usa = models.BooleanField(
        default=False,
        help_text='Si se puede comprar en Amazon USA'
    )
    recommended_price = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency='MXN',
        null=True,
        blank=True,
        help_text='Precio recomendado con margen objetivo'
    )
    price_difference = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency='MXN',
        null=True,
        blank=True,
        help_text='Diferencia con precio actual MX'
    )
    potential_profit_margin = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        null=True,
        blank=True,
        help_text='Margen potencial de ganancia'
    )

    confidence_score = models.CharField(
        max_length=10,
        choices=CONFIDENCE_SCORE_CHOICES,
        default='LOW',
        help_text='Nivel de confianza del análisis'
    )
    analysis_notes = models.TextField(
        blank=True,
        help_text='Notas y recomendaciones del análisis'
    )

    class Meta:
        verbose_name = 'Pricing Analysis Result'
        verbose_name_plural = 'Pricing Analysis Results'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['asin', '-created_at']),
            models.Index(fields=['is_feasible', '-created_at']),
            models.Index(fields=['is_available_usa']),
        ]

    def __str__(self):
        return f'{self.asin} - {"Feasible" if self.is_feasible else "Not Feasible"} ({self.created_at.date()})'


class PricingAnalysisBatch(BaseModel):
    """Agrupa múltiples análisis en un batch."""

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    name = models.CharField(
        max_length=200,
        help_text='Nombre del batch'
    )
    asins = models.JSONField(
        default=list,
        help_text='Lista de ASINs a analizar'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text='Estado del batch'
    )

    # Contadores
    total_asins = models.PositiveIntegerField(
        default=0,
        help_text='Total de ASINs en el batch'
    )
    processed_asins = models.PositiveIntegerField(
        default=0,
        help_text='ASINs procesados'
    )
    successful_analyses = models.PositiveIntegerField(
        default=0,
        help_text='Análisis exitosos'
    )
    failed_analyses = models.PositiveIntegerField(
        default=0,
        help_text='Análisis fallidos'
    )
    unavailable_in_usa_count = models.PositiveIntegerField(
        default=0,
        help_text='Productos no disponibles en USA'
    )

    results = models.ManyToManyField(
        'PricingAnalysisResult',
        blank=True,
        related_name='batches',
        help_text='Resultados del análisis'
    )
    error_log = models.JSONField(
        default=dict,
        blank=True,
        help_text='Log de errores durante el procesamiento'
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha de inicio del procesamiento'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha de finalización'
    )

    class Meta:
        verbose_name = 'Pricing Analysis Batch'
        verbose_name_plural = 'Pricing Analysis Batches'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.get_status_display()} ({self.processed_asins}/{self.total_asins})'


class KeepaAPILog(BaseModel):
    """Log de todas las llamadas a Keepa API."""

    endpoint = models.CharField(
        max_length=255,
        help_text='Endpoint llamado'
    )
    request_params = models.JSONField(
        default=dict,
        help_text='Parámetros de la request'
    )
    response_status = models.IntegerField(
        null=True,
        blank=True,
        help_text='HTTP status code de la respuesta'
    )
    response_data = models.JSONField(
        default=dict,
        blank=True,
        help_text='Data de la respuesta'
    )
    tokens_consumed = models.PositiveIntegerField(
        default=0,
        help_text='Tokens consumidos en esta llamada'
    )
    error_message = models.TextField(
        blank=True,
        help_text='Mensaje de error si hubo problema'
    )
    execution_time_ms = models.PositiveIntegerField(
        default=0,
        help_text='Tiempo de ejecución en milisegundos'
    )

    class Meta:
        verbose_name = 'Keepa API Log'
        verbose_name_plural = 'Keepa API Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['response_status']),
        ]

    def __str__(self):
        return f'{self.endpoint} - Status {self.response_status} ({self.created_at})'
