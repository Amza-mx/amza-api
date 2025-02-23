from rest_framework import serializers
from apps.sales_orders.models import SalesOrder, SalesOrderDetail, SalesOrderDetailShipment


class SalesOrderDetailShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrderDetailShipment
        fields = (
            'order_detail',
            'tracking_number',
            'cost',
            'courier',
            'status',
            'date_dispatched',
            'estimated_delivery_date',
            'delivery_date',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')


class SalesOrderDetailSerializer(serializers.ModelSerializer):
    sales_order_detail_shipments = SalesOrderDetailShipmentSerializer(required=False)
    prep_center = serializers.StringRelatedField()

    class Meta:
        model = SalesOrderDetail
        fields = (
            'product',
            'status',
            'quantity',
            'unit_price',
            'total_price',
            'dispatch_date',
            'prep_center',
            'prep_center_folio',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')


class SalesOrderSerializer(serializers.ModelSerializer):
    sales_orders_details = SalesOrderDetailSerializer(many=True)
    marketplace = serializers.StringRelatedField()

    class Meta:
        model = SalesOrder
        fields = (
            'external_id',
            'marketplace',
            'sale_date',
            'total_amount',
            'status',
            'delivery_promised_date',
            'shipping_deadline',
            'created_at',
            'updated_at',
            'sales_orders_details',
        )
        read_only_fields = ('created_at', 'updated_at')
