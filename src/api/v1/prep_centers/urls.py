from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.v1.prep_centers.views import PrepCenterModelViewSet


router = DefaultRouter()
router.register(r'prep-centers', PrepCenterModelViewSet, 'prep-center')

urlpatterns = [
    path('', include(router.urls)),
]
