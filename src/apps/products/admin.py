from django.contrib.admin import register
from base.admin import BaseAdmin
from apps.products.models import Product, ProductPrice


@register(Product)
class ProductAdmin(BaseAdmin):
    list_display = (
        'title',
        'sku',
        'external_id',
    )
    search_fields = (
        'title',
        'sku',
        'external_id',
    )


@register(ProductPrice)
class ProductPriceAdmin(BaseAdmin):
    list_display = ('product', 'amount')
    search_fields = (
        'product__sku',
        'product_external_id',
    )
    raw_id_fields = ('product',)

    def get_product_title(self, obj):
        return obj.product.title
