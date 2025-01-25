from django.contrib import admin
from base.admin import BaseAdmin
from apps.sales_orders.models import (
    SalesOrder,
    SalesOrderDetail,
    SalesOrderDetailShipment,
    ShipmentTracking
)


class SalesOrderDetailInline(admin.TabularInline):
    model = SalesOrderDetail
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SalesOrder)
class SalesOrderAdmin(BaseAdmin):
    list_display = (
        'external_id', 'marketplace', 'status', 'sale_date',
        'delivery_promised_date', 'shipping_deadline'
    )
    search_fields = ('external_id', 'marketplace', 'status')
    list_filter = ('marketplace', 'status')
    inlines = (SalesOrderDetailInline,)


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
    list_display = ('tracking_number', 'cost', 'courier', 'status')
    search_fields = ('tracking_number', 'courier', 'status')
    list_filter = ('courier', 'status')
    inlines = (ShipmentTrackingInline,)
