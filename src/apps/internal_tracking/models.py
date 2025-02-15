from django.db import models


class InternalTracking(models.Model):
    internal_id = models.CharField(max_length=100)
    us_amz_order = models.CharField(max_length=100)
    us_order_link = models.CharField(max_length=100)
    us_guide = models.CharField(max_length=100)
    estimated_arrival_date = models.CharField(max_length=100)
    arrival_date = models.CharField(max_length=100)
