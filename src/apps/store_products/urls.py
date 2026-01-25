from django.urls import path

from .views import StoreProductListView

app_name = 'store_products'

urlpatterns = [
    path('', StoreProductListView.as_view(), name='list'),
]
