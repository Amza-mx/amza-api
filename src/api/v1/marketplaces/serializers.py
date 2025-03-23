from apps.marketplaces.models import Marketplace
from ..common.serializers import TimestampedModelSerializer


class MarketplaceSerializer(TimestampedModelSerializer):
    class Meta:
        model = Marketplace
        fields = ['id', 'name', 'platform', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at'] 