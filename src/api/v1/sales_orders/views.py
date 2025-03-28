from rest_framework.viewsets import ModelViewSet
from apps.sales_orders.models import SalesOrder
from api.v1.sales_orders.serializers import SalesOrderSerializer


class SalesOrderViewSet(ModelViewSet):
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
