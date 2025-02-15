from django.contrib import admin
from apps.purchases_orders.models import PurchaseOrder, PurchaseOrderDetail, ShipmentTracking


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    pass


@admin.register(PurchaseOrderDetail)
class PurchaseOrderDetailAdmin(admin.ModelAdmin):
    readonly_fields = ['total_price']


@admin.register(ShipmentTracking)
class PurchaseOrderTrackingAdmin(admin.ModelAdmin):
    pass
