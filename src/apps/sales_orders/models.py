from djmoney.models.fields import MoneyField
from django.db.models import F
from django.db.models.fields.generated import GeneratedField
from django.db import models
from base.models import BaseModel
from apps.products.models import Product
from base.choices import SalesOrderStatusChoices, ShipmentStatusChoices, CourierChoices


class SalesOrder(BaseModel):
    """
    Represents a sales order from a marketplace.
    This model encapsulates the key details of a sales order that originates from an external system (e.g. Amazon, WooCommerce), including identification, financial figures, status, and related dates.
    Attributes:
        external_id (str): Unique identifier for the sales order from the external system. Indexed for performance.
        marketplace (ForeignKey): Reference to the Marketplace model. Deletion of a referenced marketplace is protected.
        sale_date (date): The date on which the sale occurred.
        total_amount (Money): The total amount of the order, stored as a monetary value with 'MXN' as the default currency.
        status (str): Current status of the sales order. Allowed values are defined in SalesOrderStatusChoices, with "Pending" as the default.
        delivery_promised_date (Optional[date]): The promised date for delivery, if provided.
        shipping_deadline (Optional[date]): The latest date by which shipping should be completed, if provided.
    Meta:
        verbose_name: 'Sales Order'
        verbose_name_plural: 'Sales Orders'
    Returns:
        str: String representation of the sales order in the format "external_id - marketplace - status".
    """

    external_id = models.CharField(
        max_length=50,
        db_index=True,
        help_text='Order ID from the external system (e.g. Amazon, WooCommerce)',
    )
    marketplace = models.ForeignKey(
        'marketplaces.Marketplace', on_delete=models.PROTECT, related_name='sales_orders'
    )
    sale_date = models.DateField()
    total_amount = MoneyField(max_digits=10, decimal_places=2, default_currency='MXN')
    status = models.CharField(
        max_length=50,
        choices=SalesOrderStatusChoices.choices,
        default=SalesOrderStatusChoices.PENDING.value,
    )
    delivery_promised_date = models.DateField(blank=True, null=True)
    shipping_deadline = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = 'Sales Order'
        verbose_name_plural = 'Sales Orders'

    def __str__(self):
        return f'{self.external_id} - {self.marketplace} - {self.status}'


class SalesOrderDetail(BaseModel):
    """
    Model representing a product in a sales order.
    Attributes:
        sales_order (ForeignKey): A reference to the associated SalesOrder. Deletion cascades, and the reverse relation is available via the 'sales_orders_details' related name.
        product (ForeignKey): A reference to the associated Product. Uses PROTECT on deletion, and the reverse relation is available via the 'sales_orders_details' related name.
        status (CharField): The current status of the sales order detail. It uses preset choices from SalesOrderStatusChoices with a default value of PENDING.
        quantity (PositiveIntegerField): The quantity of the product ordered.
        unit_price (MoneyField): The unit price of the product, represented in MXN.
        total_price (GeneratedField): A computed field representing the total price calculated as unit_price multiplied by quantity. This is persisted in the database.
        dispatch_date (DateField): The date when the product is scheduled for dispatch; this field is optional.
        prep_center (ForeignKey): A reference to the associated prep center (from 'prep_centers.PrepCenter'). Uses PROTECT on deletion.
        prep_center_folio (CharField): An optional identifier (folio) for the prep center.
    Methods:
        __str__(): Returns a string representation combining the product and quantity details.
    """

    sales_order = models.ForeignKey(
        SalesOrder, on_delete=models.CASCADE, related_name='sales_orders_details'
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='sales_orders_details'
    )
    status = models.CharField(
        max_length=50,
        choices=SalesOrderStatusChoices.choices,
        default=SalesOrderStatusChoices.PENDING.value,
    )
    quantity = models.PositiveIntegerField()
    unit_price = MoneyField(max_digits=10, decimal_places=2, default_currency='MXN')
    total_price = GeneratedField(
        expression=F('unit_price') * F('quantity'),
        output_field=models.DecimalField(max_digits=10, decimal_places=2),
        db_persist=True,
    )
    dispatch_date = models.DateField(blank=True, null=True)
    prep_center = models.ForeignKey(
        'prep_centers.PrepCenter', on_delete=models.PROTECT, related_name='sales_orders_details'
    )
    prep_center_folio = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = 'Sales Order Detail'
        verbose_name_plural = 'Sales Order Details'

    def __str__(self):
        return f'{self.product} - {self.quantity}'


class SalesOrderDetailShipment(BaseModel):
    """
    Model representing a shipment associated with a specific sales order detail.
    Attributes:
        order_detail (SalesOrderDetail): A one-to-one relationship linking this shipment to the corresponding sales order detail.
        tracking_number (str): The tracking number for the shipment (maximum 50 characters).
        cost (Money): The cost of the shipment, stored as a money field with a maximum of 10 digits and 2 decimal places, defaulting to 'MXN' currency.
        courier (str): The courier handling the shipment, selected from defined CourierChoices; defaults to 'OTHER'.
        status (str): The current status of the shipment, selected from ShipmentStatusChoices; defaults to 'PENDING'.
        date_dispatched (date, optional): The date when the shipment was dispatched.
        estimated_delivery_date (date, optional): The expected delivery date of the shipment.
        delivery_date (date, optional): The actual delivery date of the shipment.
    Methods:
        __str__:
            Returns a string representation combining the tracking number and the courier.
    """

    order_detail = models.OneToOneField(
        SalesOrderDetail, on_delete=models.CASCADE, related_name='shipment'
    )
    tracking_number = models.CharField(max_length=50)
    cost = MoneyField(max_digits=10, decimal_places=2, default_currency='MXN')
    courier = models.CharField(
        max_length=40, choices=CourierChoices.choices, default=CourierChoices.OTHER.value
    )
    status = models.CharField(
        max_length=40,
        choices=ShipmentStatusChoices.choices,
        default=ShipmentStatusChoices.PENDING.value,
    )
    date_dispatched = models.DateField(blank=True, null=True)
    estimated_delivery_date = models.DateField(blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = 'Sales Order Detail Shipment'
        verbose_name_plural = 'Sales Order Detail Shipments'

    def __str__(self):
        return f'{self.tracking_number} - {self.courier}'


class ShipmentTracking(BaseModel):
    """
    Represents the tracking information associated with a shipment for a sales order.
    Attributes:
        sales_order_detail_shipment (SalesOrderDetailShipment):
            A foreign key linking to the detailed shipment record. This association ensures that each tracking record
            is tied to a specific shipment in the sales order.
        status (str):
            The current state of the shipment. It uses predefined choices from ShipmentStatusChoices, with a default
            value of 'PENDING'.
        status_date (datetime):
            The date and time when the shipment status was recorded, indicating the timing of the status change.
        message (str, optional):
            An optional detailed description or additional information regarding the shipment status.
    Methods:
        __str__():
            Provides a human-readable string representation of the shipment tracking record,
            typically combining the status and the status_date.
    """

    sales_order_detail_shipment = models.ForeignKey(
        SalesOrderDetailShipment, on_delete=models.CASCADE, related_name='tracking'
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
