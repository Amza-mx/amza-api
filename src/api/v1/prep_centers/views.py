from rest_framework import viewsets
from apps.prep_centers.models import PrepCenter
from api.v1.prep_centers.serializers import PrepCenterSerializer


class PrepCenterModelViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = PrepCenter.objects.all()
    serializer_class = PrepCenterSerializer
