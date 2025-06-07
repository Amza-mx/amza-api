from rest_framework import serializers
from apps.products.models import Product, ProductPrice


class ProductPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrice
        fields = ['id', 'amount', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    prices = ProductPriceSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'external_id', 'sku', 'title', 'description', 
                 'inventory_quantity', 'category', 'prices', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at'] 