from django.contrib import admin
from base.admin import BaseAdmin
from apps.sales_orders.models import (
    SalesOrder,
    SalesOrderDetail,
    SalesOrderDetailShipment,
    ShipmentTracking,
)


class SalesOrderDetailInline(admin.TabularInline):
    model = SalesOrderDetail
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SalesOrder)
class SalesOrderAdmin(BaseAdmin):
    list_display = (
        'external_id',
        'marketplace',
        'status',
        'sale_date',
        'delivery_promised_date',
        'shipping_deadline',
        'fees',
        'yield_amount_before_shipping',
        'get_shipping_cost',
        'yield_amount',
    )
    search_fields = ('external_id', 'marketplace', 'status')
    list_filter = ('marketplace', 'status')
    inlines = (SalesOrderDetailInline,)
    readonly_fields = ('fees', 
                       'yield_amount_before_shipping', 
                       'get_shipping_cost',
                       'yield_amount')

    def yield_amount(self, obj):
        return obj.yield_amount_before_shipping - obj.get_shipping_cost


class SalesOrderDetailShipmentInline(admin.TabularInline):
    model = SalesOrderDetailShipment
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SalesOrderDetail)
class SalesOrderDetailAdmin(BaseAdmin):
    list_display = ('product', 'quantity')
    search_fields = ('product', 'quantity')
    list_filter = ('product', 'quantity')
    inlines = (SalesOrderDetailShipmentInline,)


class ShipmentTrackingInline(admin.TabularInline):
    model = ShipmentTracking
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SalesOrderDetailShipment)
class SalesOrderDetailShipmentAdmin(BaseAdmin):
    list_display = ('tracking_number', 'cost', 'courier', 'status', 'order_detail__sales_order__external_id', 'get_last_tracking')
    search_fields = ('tracking_number', 'courier', 'status', 'order_detail__sales_order__external_id')
    list_filter = ('courier', 'status')
    inlines = (ShipmentTrackingInline,)

    def order_detail__sales_order__external_id(self, obj):
        return obj.order_detail.sales_order.external_id

    def get_last_tracking(self, obj):
        last_tracking = obj.tracking.last()
        if not last_tracking:
            return 'No tracking information available'
        return last_tracking.message