from rest_framework import serializers
from apps.prep_centers.models import Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = (
            'id',
            'name',
            'address',
        )
