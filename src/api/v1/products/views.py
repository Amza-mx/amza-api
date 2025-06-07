from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from apps.products.models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Product instances.

    This viewset leverages Django REST Framework's ModelViewSet to provide 
    CRUD operations (create, retrieve, update, and delete) for the Product model.
    It uses ProductSerializer for data serialization and deserialization.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
