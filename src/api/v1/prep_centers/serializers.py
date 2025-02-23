from rest_framework import serializers
from apps.prep_centers.models import PrepCenter


class PrepCenterSerializer(serializers.ModelSerializer):
    country = serializers.StringRelatedField()
    region = serializers.StringRelatedField()
    sub_region = serializers.StringRelatedField()
    city = serializers.StringRelatedField()

    class Meta:
        model = PrepCenter
        fields = (
            'id',
            'name',
            'address',
            'country',
            'region',
            'sub_region',
            'city',
        )
