from base.models import BaseModel
from django.db import models


class Marketplace(BaseModel):
    """
    Marketplace model representing a marketplace with a unique name and a chosen platform.
    Attributes:
        name (str): The name of the marketplace with a maximum length of 50 characters.
        platform (str): The platform type of the marketplace, controlled by the PlatformChoices enum.
            It defaults to 'AMAZON' and can be either 'AMAZON' or 'WOOCOMMERCE'.
    PlatformChoices:
        A subclass that defines the allowed platform values:
            - AMAZON: Represents the 'AMAZON' platform, with a display value of 'amazon'.
            - WOOCOMMERCE: Represents the 'WOOCOMMERCE' platform, with a display value of 'woocommerce'.
    Methods:
        __str__():
            Returns a string representation of the marketplace in the format "name - platform".
    """
    name = models.CharField(max_length=50)

    class PlatformChoices(models.TextChoices):
        AMAZON = 'AMAZON', 'amazon'
        WOOCOMMERCE = 'WOOCOMMERCE', 'woocommerce'

    platform = models.CharField(
        max_length=50, choices=PlatformChoices, default=PlatformChoices.AMAZON.value
    )

    def __str__(self):
        return f'{self.name} - {self.platform}'
