from rest_framework import serializers
from apps.warehouse.models import Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = (
            'id',
            'name',
            'address',
        )
