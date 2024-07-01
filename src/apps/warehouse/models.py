from django.db import models


class Warehouse(models.Model):
	name = models.CharField(max_length=100)
	address = models.CharField(max_length=100)
