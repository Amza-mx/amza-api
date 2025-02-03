from djmoney.models.fields import MoneyField
from django.db.models import F
from django.db.models.fields.generated import GeneratedField
from django.db import models
from base.models import BaseModel
from apps.products.models import Product
from base.choices import SalesOrderStatusChoices, ShipmentStatusChoices, CourierChoices


class SalesOrder(BaseModel):
	"""Model to represent a sales order from a marketplace"""
	external_id = models.CharField(max_length=50, db_index=True, help_text='Order ID from the external system (e.g. Amazon, WooCommerce)')
	marketplace = models.ForeignKey('marketplaces.Marketplace', on_delete=models.PROTECT, related_name='sales_orders')
	sale_date = models.DateField()
	total_amount = MoneyField(max_digits=10, decimal_places=2, default_currency='MXN')
	status = models.CharField(max_length=50, choices=SalesOrderStatusChoices.choices, default=SalesOrderStatusChoices.PENDING.value)
	delivery_promised_date = models.DateField(blank=True, null=True)
	shipping_deadline = models.DateField(blank=True, null=True)

	class Meta:
		verbose_name = 'Sales Order'
		verbose_name_plural = 'Sales Orders'


	def __str__(self):
		return f'{self.external_id} - {self.marketplace} - {self.status}'	


class SalesOrderDetail(BaseModel):
	"""Model to represent a product in a sales order"""
	sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='sales_orders_details')
	product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sales_orders_details')
	status = models.CharField(max_length=50, choices=SalesOrderStatusChoices.choices, default=SalesOrderStatusChoices.PENDING.value)
	quantity = models.PositiveIntegerField()
	unit_price = MoneyField(max_digits=10, decimal_places=2, default_currency='MXN')
	total_price = GeneratedField(
		expression=F('unit_price') * F('quantity'),
		output_field=models.DecimalField(max_digits=10, decimal_places=2),
		db_persist=True
	)
	dispatch_date = models.DateField(blank=True, null=True)
	prep_center = models.ForeignKey('prep_centers.PrepCenter', on_delete=models.PROTECT, related_name='sales_orders_details')
	prep_center_folio = models.CharField(max_length=50, blank=True, null=True)

	class Meta:
		verbose_name = 'Sales Order Detail'
		verbose_name_plural = 'Sales Order Details'


	def __str__(self):
		return f'{self.product} - {self.quantity}'



class SalesOrderDetailShipment(BaseModel):
	"""Model to represent a shipment of a sales order detail"""
	order_detail = models.OneToOneField(SalesOrderDetail, on_delete=models.CASCADE, related_name='shipment')
	tracking_number = models.CharField(max_length=50)
	cost = MoneyField(max_digits=10, decimal_places=2, default_currency='MXN')
	courier = models.CharField(max_length=40, choices=CourierChoices.choices, default=CourierChoices.OTHER.value)
	status = models.CharField(max_length=40, choices=ShipmentStatusChoices.choices, default=ShipmentStatusChoices.PENDING.value)
	date_dispatched = models.DateField(blank=True, null=True)
	estimated_delivery_date = models.DateField(blank=True, null=True)
	delivery_date = models.DateField(blank=True, null=True)

	class Meta:
		verbose_name = 'Sales Order Detail Shipment'
		verbose_name_plural = 'Sales Order Detail Shipments'


	def __str__(self):
		return f'{self.tracking_number} - {self.courier}'
	

class ShipmentTracking(BaseModel):
	"""Model to represent the tracking of a shipment"""
	sales_order_detail_shipment = models.ForeignKey(SalesOrderDetailShipment, on_delete=models.CASCADE, related_name='tracking')
	status = models.CharField(max_length=50, choices=ShipmentStatusChoices.choices, default=ShipmentStatusChoices.PENDING.value)
	status_date = models.DateTimeField()
	message = models.TextField(blank=True, null=True)

	class Meta:
		verbose_name = 'Shipment Tracking'
		verbose_name_plural = 'Shipment Trackings'


	def __str__(self):
		return f'{self.status} - {self.status_date}'	
