from apps.products.models import Product
from django.db.models.fields.generated import GeneratedField
from django.db import models
from django.db.models import F
from djmoney.models.fields import MoneyField
from base.models import BaseModel
from base.choices import PurchaseOrderStatusChoices, ShipmentStatusChoices, CourierChoices


class PurchaseOrder(BaseModel):
    sales_order = models.OneToOneField(
        'sales_orders.SalesOrder', on_delete=models.CASCADE, related_name='purchase_order'
    )
    purchase_date = models.DateField()
    amount = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    status = models.CharField(
        max_length=50,
        choices=PurchaseOrderStatusChoices.choices,
        default=PurchaseOrderStatusChoices.PENDING.value,
    )
    notes = models.TextField()

    class Meta:
        verbose_name = 'Purchase Order'
        verbose_name_plural = 'Purchase Orders'

    def __str__(self):
        return f'{self.purchase_date} - {self.status}'


class PurchaseOrderDetail(BaseModel):
    external_id = models.CharField(
        max_length=50,
        db_index=True,
        blank=True,
        null=True,
        help_text='Order ID from the external system (e.g. Amazon, WooCommerce)',
    )
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name='details'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    seller = models.ForeignKey('sellers.Seller', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')  # USD
    taxes = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    total_price = GeneratedField(
        expression=F('unit_price') * F('quantity') + F('taxes'),
        output_field=models.DecimalField(max_digits=10, decimal_places=2),
        db_persist=True,
    )  # USD
    link = models.URLField(
        blank=True, null=True, help_text='Link to the product in the seller website'
    )
    estimated_delivery_date = models.DateField(blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = 'Purchase Order Detail'
        verbose_name_plural = 'Purchase Order Details'

    def __str__(self):
        return f'{self.product} - {self.seller}'


class PurchaseOrderDetailShipment(BaseModel):
    """Model to represent a shipment of a purchase order detail"""

    order_detail = models.OneToOneField(
        PurchaseOrderDetail, on_delete=models.CASCADE, related_name='shipment'
    )
    tracking_number = models.CharField(max_length=50)
    cost = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    courier = models.CharField(
        max_length=40, choices=CourierChoices.choices, default=CourierChoices.OTHER.value
    )
    status = models.CharField(
        max_length=40,
        choices=ShipmentStatusChoices.choices,
        default=ShipmentStatusChoices.PENDING.value,
    )
    shipment_date = models.DateField(blank=True, null=True)
    estimated_delivery_date = models.DateField(blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = 'Purchase Order Detail Shipment'
        verbose_name_plural = 'Purchase Order Details Shipments'

    def __str__(self):
        return f'{self.order_detail} - {self.tracking_number}'


class ShipmentTracking(BaseModel):
    """Model to represent the tracking of a shipment"""

    sales_order_detail_shipment = models.ForeignKey(
        PurchaseOrderDetailShipment, on_delete=models.CASCADE, related_name='tracking'
    )
    status = models.CharField(
        max_length=50,
        choices=ShipmentStatusChoices.choices,
        default=ShipmentStatusChoices.PENDING.value,
    )
    status_date = models.DateTimeField()
    message = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Shipment Tracking'
        verbose_name_plural = 'Shipment Trackings'

    def __str__(self):
        return f'{self.status} - {self.status_date}'


class PurchaseOrderLogisticCost(BaseModel):
    purchase_order = models.OneToOneField(
        PurchaseOrder, on_delete=models.CASCADE, related_name='logistic_cost'
    )
    shipping_cost = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    customs_cost = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    other_costs = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    total_cost = GeneratedField(
        expression=F('shipping_cost') + F('customs_cost') + F('other_costs'),
        output_field=models.DecimalField(max_digits=10, decimal_places=2),
        db_persist=True,
    )

    class Meta:
        verbose_name = 'Purchase Order Logistic Cost'
        verbose_name_plural = 'Purchase Order Logistic Costs'

    def __str__(self):
        return f'{self.purchase_order} - {self.total_cost}'
