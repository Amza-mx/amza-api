from django.urls import path
from api.v1.healthcheck.views import HealthCheckAPIView

urlpatterns = [
    path('healthcheck/', HealthCheckAPIView.as_view(), name='healthcheck'),
]
