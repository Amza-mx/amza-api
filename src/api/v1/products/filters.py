from django_filters import rest_framework as filters
from apps.products.models import Product


class ProductFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='contains')
    sku = filters.CharFilter(lookup_expr='iexact')
    external_id = filters.CharFilter(lookup_expr='iexact')
    category = filters.ChoiceFilter(choices=Product.CategoriesChoices)
    min_inventory = filters.NumberFilter(field_name='inventory_quantity', lookup_expr='gte')
    max_inventory = filters.NumberFilter(field_name='inventory_quantity', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['title', 'sku', 'external_id', 'category', 'inventory_quantity'] 