from django.db import models
from base.models import BaseModel


class ProductProvider(BaseModel):
	name = models.CharField(max_length=50)
	link = models.URLField()
	is_active = models.BooleanField(default=True)

	def __str__(self):
		return self.name
