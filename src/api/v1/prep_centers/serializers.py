from rest_framework import serializers
from apps.prep_centers.models import PrepCenter


class PrepCenterSerializer(serializers.ModelSerializer):
	class Meta:
		model = PrepCenter
		fields = (
			'id',
			'name',
			'address',
		)
