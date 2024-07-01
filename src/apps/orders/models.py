import decimal
from django.db.models import F
from django.db.models.fields.generated import GeneratedField
from django.db import models
from base.models import BaseModel
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.products.models import Product
from apps.warehouse.models import Warehouse


PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]


class Order(BaseModel):

	class StatusChoices(models.TextChoices):
		PENDING = 'PENDING', 'Pending'
		BOUGHT = 'BOUGHT', 'Bought'
		IN_WAREHOUSE = 'IN_WAREHOUSE', 'In warehouse'
		DELIVERY_PROCESS = 'DELIVERY_PROCESS', 'Delivery process'
		DELIVERED = 'DELIVERED', 'Delivered'
		CANCELLED = 'CANCELLED', 'Cancelled'

	status = models.CharField(max_length=50, choices=StatusChoices.choices, default=StatusChoices.PENDING)
	customer_state = models.CharField(max_length=50)
	customer_city = models.CharField(max_length=50)
	customer_zip_code = models.CharField(max_length=10)

	def __str__(self):
		return f'{self.id} - {self.status}'


class OrderDetail(BaseModel):
	class StatusChoices(models.TextChoices):
		PENDING = 'PENDING', 'Pending'
		BOUGHT = 'BOUGHT', 'Bought'
		IN_WAREHOUSE = 'IN_WAREHOUSE', 'In warehouse'
		DELIVERY_PROCESS = 'DELIVERY_PROCESS', 'Delivery process'
		DELIVERED = 'DELIVERED', 'Delivered'
		CANCELLED = 'CANCELLED', 'Cancelled'

	order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_details')
	product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_details')
	warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='orders')

	status = models.CharField(max_length=40, choices=StatusChoices.choices, default=StatusChoices.PENDING.value)
	link_order = models.URLField(blank=True, null=True)
	quantity = models.PositiveIntegerField()
	unit_price = models.DecimalField(max_digits=10, decimal_places=2)
	purchase_date = models.DateField(blank=True, null=True)

	def __str__(self):
		return f'{self.product.product_title} - {self.quantity}'


class OrderDetailCost(BaseModel):
	"""Model to store the cost of an order detail. It has a one-to-one relationship with OrderDetail."""

	order_detail = models.OneToOneField(
		OrderDetail, on_delete=models.CASCADE, related_name='order_cost'
	)

	# Costs
	product_cost = models.DecimalField(max_digits=10, decimal_places=2)

	# Fees
	fee_cost = GeneratedField(
		expression=F('product_cost') * decimal.Decimal(0.15),
		output_field=models.DecimalField(max_digits=10, decimal_places=2),
		db_persist=True
	)

	importation_cost = models.DecimalField(max_digits=10, decimal_places=2)
	importation_vat = GeneratedField(
		expression=F('importation_cost') * decimal.Decimal(0.0825),
		output_field=models.DecimalField(max_digits=10, decimal_places=2),
		db_persist=True
	)

	logistics_cost = GeneratedField(
		expression=(F('importation_cost') + F('importation_vat')) * decimal.Decimal(0.2),
		output_field=models.DecimalField(max_digits=10, decimal_places=2),
		db_persist=True
	)
	logistics_vat = GeneratedField(
		expression=F('logistics_cost') * decimal.Decimal(0.16),
		output_field=models.DecimalField(max_digits=10, decimal_places=2),
		db_persist=True
	)

	customer_shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self):
		return f'{self.id} - {self.order_detail.product.product_title}'

	@property
	def importation_total(self):
		return self.importation_cost + self.importation_vat

	@property
	def logistics_total(self):
		return self.logistics_cost + self.logistics_vat

	def get_total_comissions(self):
		return self.importation_total + self.logistics_total + self.customer_shipping_cost

	def get_total_cost(self):
		return (
			self.product_cost
			+ self.fee_cost
			+ self.importation_total
			+ self.logistics_total
			+ self.customer_shipping_cost
		)

	def get_margin(self):
		return (
			self.fee_cost
			- self.importation_total
			- self.customer_shipping_cost
			- self.logistics_total
		)

	def get_percentage_revenue(self):
		if not self.get_total_cost():
			return 0

		self.get_margin() / self.get_total_cost() * 100

	def get_roi(self):
		if not self.get_total_comissions():
			return 0

		return self.get_margin() / self.get_total_comissions() * 100


class OrderDetailShipment(BaseModel):
	order_detail = models.ForeignKey(
		OrderDetail, on_delete=models.CASCADE, related_name='shipments'
	)
	tracking_number = models.CharField(max_length=50)

	class CourierChoices(models.TextChoices):
		DHL = 'DHL', 'DHL'
		UPS = 'UPS', 'UPS'
		FEDEX = 'FEDEX', 'FedEx'
		ESTAFETA = 'ESTAFETA', 'Estafeta'
		OTHER = 'OTHER', 'Other'

	courier = models.CharField(max_length=40, choices=CourierChoices.choices, default=CourierChoices.OTHER)

	class StatusChoices(models.TextChoices):
		DISPATCHED = 'DISPATCHED', 'Dispatched'
		IN_TRANSIT = 'IN_TRANSIT', 'In transit'
		DELIVERED = 'DELIVERED', 'Delivered'
		CANCELLED = 'CANCELLED', 'Cancelled'

	status = models.CharField(max_length=40, choices=StatusChoices.choices, default=StatusChoices.DISPATCHED)

	dispatch_date = models.DateField()
	delivery_date = models.DateField(blank=True, null=True)

	def __str__(self):
		return f'{self.courier} - {self.tracking_number}'
