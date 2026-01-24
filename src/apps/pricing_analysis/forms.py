from django import forms


class BrandRestrictionForm(forms.Form):
    name = forms.CharField(max_length=255, required=True)
    is_allowed = forms.BooleanField(required=False)


class BrandRestrictionToggleForm(forms.Form):
    brand_id = forms.IntegerField(required=True)
    is_allowed = forms.BooleanField(required=False)


class BrandRestrictionUploadForm(forms.Form):
    file = forms.FileField(required=True)
