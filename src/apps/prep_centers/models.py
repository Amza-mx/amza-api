from django.db import models
from cities_light.models import Country, Region, SubRegion, City
from base.models import BaseModel


class PrepCenter(BaseModel):
    """
    PrepCenter model representing a preparation center.
    Attributes:
        name (CharField): The name of the preparation center with a maximum length of 100 characters.
        address (TextField): The physical address of the preparation center.
        country (ForeignKey): A reference to the Country model; deletion of a country cascades.
        region (ForeignKey): A reference to the Region model; deletion of a region cascades.
        sub_region (ForeignKey): A reference to the SubRegion model; deletion of a sub-region cascades.
        city (ForeignKey): A reference to the City model; deletion of a city cascades.
        postal_code (CharField): The postal code of the preparation center with a maximum length of 10 characters.
        phone (CharField): An optional phone number for the preparation center with a maximum length of 20 characters.
    """
    name = models.CharField(max_length=100)
    address = models.TextField()
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='prep_centers', null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True, related_name='prep_centers')
    sub_region = models.ForeignKey(SubRegion, on_delete=models.CASCADE, null=True, blank=True, related_name='prep_centers')
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True, related_name='prep_centers')
    postal_code = models.CharField(max_length=10, null=True, blank=True, help_text='Postal code')
    phone = models.CharField(max_length=20, null=True, blank=True, help_text='Phone number')

    class Meta:
        verbose_name = 'Prep Center'
        verbose_name_plural = 'Prep Centers'

    def __str__(self):
        return self.name
