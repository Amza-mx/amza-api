from rest_framework.viewsets import ModelViewSet
from apps.sales_orders.models import SalesOrder
from api.v1.sales_orders.serializers import SalesOrderSerializer


class SalesOrderViewSet(ModelViewSet):
    """
    ViewSet for managing SalesOrder instances.

    This viewset leverages Django REST Framework's ModelViewSet to provide 
    CRUD operations (create, retrieve, update, and delete) for the SalesOrder model.
    It uses SalesOrderSerializer for data serialization and deserialization.
    """
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
