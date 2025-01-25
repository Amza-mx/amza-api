from rest_framework import viewsets
from apps.prep_centers.models import Warehouse
from api.warehouse.serializers import WarehouseSerializer

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
