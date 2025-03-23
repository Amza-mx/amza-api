from django.contrib import admin
from base.admin import BaseAdmin
from apps.purchases_orders.models import (
    PurchaseOrder,
    PurchaseOrderDetail,
    ShipmentTracking,
    PurchaseOrderDetailShipment,
)


class PurchaseOrderDetailInline(admin.TabularInline):
    """
    Inline admin for :model:`apps.purchases_orders.PurchaseOrderDetail` model.
    
    This inline admin allows managing purchase order details directly within the
    :model:`apps.purchases_orders.PurchaseOrder` admin interface. It provides a
    tabular view of all details associated with a purchase order.
    
    The total price field is automatically calculated and set as readonly to prevent
    manual modifications.
    """
    
    model = PurchaseOrderDetail
    extra = 0
    readonly_fields = ('created_at', 'updated_at', 'total_price')


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(BaseAdmin):
    """
    Admin interface for managing :model:`apps.purchases_orders.PurchaseOrder` models.
    
    This admin interface provides comprehensive functionality for managing purchase orders:
    
    * View and edit purchase order details including date, amount, and status
    * Link to related sales orders using a searchable field
    * Filter orders by status
    * Manage order details inline through :class:`PurchaseOrderDetailInline`
    
    The interface inherits from :class:`base.admin.BaseAdmin` which provides
    automatic timestamp field handling.
    """
    
    raw_id_fields = ('sales_order',)
    list_display = (
        'purchase_date',
        'amount',
        'status',
        'notes'
    )
    search_fields = ('sales_order__external_id',)
    list_filter = ('status',)
    inlines = (PurchaseOrderDetailInline,)


class PurchaseOrderDetailShipmentInline(admin.TabularInline):
    """
    Inline admin for :model:`apps.purchases_orders.PurchaseOrderDetailShipment` model.
    
    This inline admin allows managing shipment details directly within the
    :model:`apps.purchases_orders.PurchaseOrderDetail` admin interface. It provides
    a tabular view of all shipments associated with a purchase order detail.
    """
    
    model = PurchaseOrderDetailShipment
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PurchaseOrderDetail)
class PurchaseOrderDetailAdmin(BaseAdmin):
    """
    Admin interface for managing :model:`apps.purchases_orders.PurchaseOrderDetail` models.
    
    This admin interface provides functionality to manage individual items within
    purchase orders:
    
    * View and edit item details
    * Manage shipments through :class:`PurchaseOrderDetailShipmentInline`
    * Track total price (readonly field)
    
    The interface inherits from :class:`base.admin.BaseAdmin` which provides
    automatic timestamp field handling.
    """
    list_display = ('purchase_order', 'product', 'quantity', 'unit_price', 'total_price')
    readonly_fields = ('total_price',)
    inlines = (PurchaseOrderDetailShipmentInline,)


class ShipmentTrackingInline(admin.TabularInline):
    """
    Inline admin for :model:`apps.purchases_orders.ShipmentTracking` model.
    
    This inline admin allows managing shipment tracking information directly within
    the :model:`apps.purchases_orders.PurchaseOrderDetailShipment` admin interface.
    It provides a tabular view of all tracking events associated with a shipment.
    """
    
    model = ShipmentTracking
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PurchaseOrderDetailShipment)
class PurchaseOrderDetailShipmentAdmin(BaseAdmin):
    """
    Admin interface for managing :model:`apps.purchases_orders.PurchaseOrderDetailShipment` models.
    
    This admin interface provides functionality to manage shipments of purchase order details:
    
    * View and edit shipment details
    * Track shipment status through :class:`ShipmentTrackingInline`
    * Monitor shipment progress and tracking information
    
    The interface inherits from :class:`base.admin.BaseAdmin` which provides
    automatic timestamp field handling.
    """
    
    inlines = (ShipmentTrackingInline,)
