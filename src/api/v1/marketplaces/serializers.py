from rest_framework import serializers
from apps.marketplaces.models import Marketplace


class MarketplaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marketplace
        fields = ('id', 'name', 'platform', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')