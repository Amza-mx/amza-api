from django.contrib.admin import register
from base.admin import BaseAdmin
from apps.prep_centers.models import PrepCenter


@register(PrepCenter)
class PrepCenterAdmin(BaseAdmin):
    list_display = (
        'name',
        'address',
    )
    search_fields = (
        'name',
        'address',
    )
    raw_id_fields = (
        'country',
        'region',
        'sub_region',
        'city',
    )