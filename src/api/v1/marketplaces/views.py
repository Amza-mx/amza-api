from rest_framework import viewsets
from apps.marketplaces.models import Marketplace
from .serializers import MarketplaceSerializer


class MarketplaceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing marketplaces.
    """
    queryset = Marketplace.objects.all()
    serializer_class = MarketplaceSerializer
    search_fields = ['name', 'platform']
    filterset_fields = ['platform'] 
