from django.contrib.admin import register
from base.admin import BaseAdmin
from apps.marketplaces.models import Marketplace


@register(Marketplace)
class MarketplaceAdmin(BaseAdmin):
    list_display = ('name', 'platform')
