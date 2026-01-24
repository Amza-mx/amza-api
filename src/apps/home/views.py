from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils import timezone
from datetime import timedelta


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home/index.html'
    login_url = '/admin/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Import models here to avoid circular imports
        from apps.pricing_analysis.models import (
            PricingAnalysisResult,
            BrandRestriction,
            KeepaProductData,
        )

        # Date ranges
        last_7_days = timezone.now() - timedelta(days=7)

        # Statistics
        context['stats'] = {
            'total_analyses': PricingAnalysisResult.objects.count(),
            'recent_analyses': PricingAnalysisResult.objects.filter(
                created_at__gte=last_7_days
            ).count(),
            'feasible_products': PricingAnalysisResult.objects.filter(
                is_feasible=True, is_available_usa=True
            ).count(),
            'total_brands': BrandRestriction.objects.count(),
            'allowed_brands': BrandRestriction.objects.filter(is_allowed=True).count(),
            'blocked_brands': BrandRestriction.objects.filter(is_allowed=False).count(),
            'usa_products': KeepaProductData.objects.filter(
                marketplace='USA', sync_successful=True
            ).count(),
            'mx_products': KeepaProductData.objects.filter(
                marketplace='MX', sync_successful=True
            ).count(),
        }

        return context
