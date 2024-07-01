from django.db import models
from base.models import BaseModel


class Product(BaseModel):
	"""Model to store the products that are going to be sold."""

	sku = models.CharField(
		max_length=50,
		help_text='Stock Keeping Unit (SKU) is a unique code that you can assign to each product in your inventory.',
	)
	product_title = models.CharField(max_length=100)
