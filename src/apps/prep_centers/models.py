from django.db import models
from base.models import BaseModel


class PrepCenter(BaseModel):
	name = models.CharField(max_length=100)
	address = models.CharField(max_length=100)

	class Meta:
		verbose_name = 'Prep Center'
		verbose_name_plural = 'Prep Centers'
