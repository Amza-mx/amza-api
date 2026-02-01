from django import forms

from .models import StoreProduct


class StoreProductUploadForm(forms.Form):
    MARKETPLACE_CHOICES = [
        ('US', 'Amazon USA'),
        ('MX', 'Amazon México'),
    ]

    file = forms.FileField(required=True)
    marketplace = forms.ChoiceField(
        choices=MARKETPLACE_CHOICES,
        required=True,
        initial='MX',
        label='Marketplace para notificaciones'
    )
    tracking_type = forms.ChoiceField(
        choices=StoreProduct.TrackingType.choices,
        required=True,
        initial=StoreProduct.TrackingType.REGULAR,
    )
    tracking_enabled = forms.BooleanField(required=False, initial=True)
    is_active = forms.BooleanField(required=False, initial=True)


class StoreProductAddForm(forms.Form):
    MARKETPLACE_CHOICES = [
        ('US', 'Amazon USA'),
        ('MX', 'Amazon México'),
    ]

    asin = forms.CharField(max_length=20, required=True)
    sku = forms.CharField(max_length=100, required=False)
    price_mxn = forms.DecimalField(required=False, max_digits=12, decimal_places=2)
    marketplace = forms.ChoiceField(
        choices=MARKETPLACE_CHOICES,
        required=True,
        initial='MX',
        label='Marketplace para notificaciones'
    )
    tracking_type = forms.ChoiceField(
        choices=StoreProduct.TrackingType.choices,
        required=True,
        initial=StoreProduct.TrackingType.REGULAR,
    )
    tracking_enabled = forms.BooleanField(required=False, initial=True)
    is_active = forms.BooleanField(required=False, initial=True)
