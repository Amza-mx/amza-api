from rest_framework import viewsets
from apps.marketplaces.models import Marketplace
from .serializers import MarketplaceSerializer


class MarketplaceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Marketplace instances.

    This viewset leverages Django REST Framework's ModelViewSet to provide 
    CRUD operations (create, retrieve, update, and delete) for the Marketplace model.
    It uses MarketplaceSerializer for data serialization and deserialization.

    """
    # TODO: Add permission classes
    queryset = Marketplace.objects.all()
    serializer_class = MarketplaceSerializer
    search_fields = ['name', 'platform']
    filterset_fields = ['platform'] 
