from django import forms

from .models import StoreProduct


class StoreProductUploadForm(forms.Form):
    file = forms.FileField(required=True)
    tracking_type = forms.ChoiceField(
        choices=StoreProduct.TrackingType.choices,
        required=True,
        initial=StoreProduct.TrackingType.REGULAR,
    )
    tracking_enabled = forms.BooleanField(required=False, initial=True)
    is_active = forms.BooleanField(required=False, initial=True)


class StoreProductAddForm(forms.Form):
    asin = forms.CharField(max_length=20, required=True)
    sku = forms.CharField(max_length=100, required=False)
    price_mxn = forms.DecimalField(required=False, max_digits=12, decimal_places=2)
    tracking_type = forms.ChoiceField(
        choices=StoreProduct.TrackingType.choices,
        required=True,
        initial=StoreProduct.TrackingType.REGULAR,
    )
    tracking_enabled = forms.BooleanField(required=False, initial=True)
    is_active = forms.BooleanField(required=False, initial=True)
