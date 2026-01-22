from django.apps import AppConfig


class PricingAnalysisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pricing_analysis'
    verbose_name = 'Pricing Analysis'

    def ready(self):
        """Import signals when app is ready."""
        pass
