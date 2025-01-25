from base.models import BaseModel
from django.db import models



class Marketplace(BaseModel):
    name = models.CharField(max_length=50)

    class PlatformChoices(models.TextChoices):
        AMAZON = 'AMAZON', 'amazon'
        WOOCOMMERCE = 'WOOCOMMERCE', 'woocommerce'

    platform = models.CharField(max_length=50, choices=PlatformChoices, default=PlatformChoices.AMAZON.value)

    def __str__(self):
        return f"{self.name} - {self.platform}"