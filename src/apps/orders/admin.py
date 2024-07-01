from django.contrib import admin
from apps.orders.models import (
    Order,
    OrderDetail,
    OrderDetailCost,
    OrderDetailShipment
)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'status',
        'customer_state',
        'customer_city',
        'customer_zip_code'
    ]
    search_fields = [
        'status',
        'customer_state',
        'customer_city',
        'customer_zip_code'
    ]
    list_filter = ['status']


@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = [
        'order',
        'product',
        'warehouse',
        'status',
        'quantity',
        'unit_price',
        'purchase_date'
    ]
    search_fields = [
        'product__sku',
        'warehouse__name'
    ]
    list_filter = [
        'status',
        'purchase_date'
    ]


@admin.register(OrderDetailCost)
class OrderDetailCostAdmin(admin.ModelAdmin):
    list_display = [
        'order_detail',
        'product_cost',
        'fee_cost',
        'importation_cost',
        'importation_vat',
        'logistics_cost',
        'logistics_vat',
        'customer_shipping_cost',
    ]
    readonly_fields = [
        'fee_cost',
        'importation_vat',
        'logistics_cost',
        'logistics_vat',
    ]
    search_fields = ['order_detail__product__sku']


@admin.register(OrderDetailShipment)
class OrderDetailShipmentAdmin(admin.ModelAdmin):
    list_display = [
        'order_detail',
        'tracking_number',
        'courier',
        'status',
        'dispatch_date',
        'delivery_date'
    ]
    search_fields = ['order_detail__product__sku']
    list_filter = ['status']
