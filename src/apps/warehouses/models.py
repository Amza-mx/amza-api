from django.db import models
from cities_light.models import Country, Region, SubRegion, City
from base.models import BaseModel


class Warehouse(BaseModel):
    """
    Warehouse model representing a warehouse.
    """
    name = models.CharField(max_length=255)
    address = models.TextField()
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    sub_region = models.ForeignKey(SubRegion, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    postal_code = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class WarehouseExchangeRate(BaseModel):
    """
    WarehouseExchangeRate model representing a warehouse exchange rate.
    """
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Warehouse Exchange Rate'
        verbose_name_plural = 'Warehouse Exchange Rates'
        ordering = ['-created_at']

    def __str__(self):
        return f"1 USD = {self.rate} WHC (active since: {self.created_at})"

    @classmethod
    def get_active_rate(cls):
        """
        Get the active rate for the warehouse.
        """
        return cls.objects.filter(is_active=True).first()
