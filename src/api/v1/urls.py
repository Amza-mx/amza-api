from django.urls import path, include

paths = [
    # path('', include('apps.products.urls')),
    # path('', include('apps.customers.urls')),
    path('', include('api.v1.auth.urls')),
    path('', include('api.v1.sales_orders.urls')),
    path('', include('api.v1.prep_centers.urls')),
]

urlpatterns = [
    path('v1/', include(paths)),
]
