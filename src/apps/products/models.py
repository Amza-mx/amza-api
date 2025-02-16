from django.db import models
from base.models import BaseModel
from djmoney.models.fields import MoneyField


class Product(BaseModel):
    external_id = models.CharField(max_length=50, db_index=True, help_text='ASIN, WooCommerce ID')
    sku = models.CharField(max_length=50, db_index=True)
    title = models.CharField(max_length=500)
    description = models.TextField()
    inventory_quantity = models.PositiveIntegerField(default=0, help_text='Stock available')

    class CategoriesChoices(models.TextChoices):
        HEALTH_AND_HOUSEHOLD = 'HEALTH AND HOUSEHOLD', 'Health & household'
        TOYS_AND_GAMES = 'TOYS AND GAMES', 'Toys & Games'

    category = models.CharField(
        max_length=40,
        choices=CategoriesChoices.choices,
        default=CategoriesChoices.HEALTH_AND_HOUSEHOLD.value,
    )

    def __str__(self):
        return f'{self.title} ({self.sku}) - {self.external_id}'

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'


class ProductSeller(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sellers')
    seller = models.ForeignKey('sellers.Seller', on_delete=models.CASCADE)
    cost_price = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    availability = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.seller} - {self.product}'

    class Meta:
        verbose_name = 'Product Seller'
        verbose_name_plural = 'Product Sellers'


class ProductPrice(BaseModel):
    product = models.ForeignKey(Product, related_name='prices', on_delete=models.CASCADE)
    amount = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')

    def __str__(self):
        return f'{self.product} - ${self.amount}'

    class Meta:
        verbose_name = 'Product Price'
        verbose_name_plural = 'Product Prices'
