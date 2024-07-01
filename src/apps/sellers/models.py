from django.db import models
from base.models import BaseModel


class Seller(BaseModel):
	"""Model to store the sellers the company works with."""

	name = models.CharField(max_length=50)
	is_active = models.BooleanField(default=True)

	def __str__(self):
		return self.name
