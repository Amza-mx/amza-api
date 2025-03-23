from apps.marketplaces.models import Marketplace
from .serializers import MarketplaceSerializer
from ..common.views import BaseModelViewSet


class MarketplaceViewSet(BaseModelViewSet):
    """
    ViewSet for viewing and editing marketplaces.
    """
    queryset = Marketplace.objects.all()
    serializer_class = MarketplaceSerializer
    search_fields = ['name', 'platform']
    filterset_fields = ['platform'] 
