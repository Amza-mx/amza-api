from rest_framework import viewsets
from apps.prep_centers.models import PrepCenter
from api.v1.prep_centers.serializers import PrepCenterSerializer


class PrepCenterModelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing PrepCenter instances.

    This viewset leverages Django REST Framework's ModelViewSet to provide 
    CRUD operations (create, retrieve, update, and delete) for the PrepCenter model.
    It uses PrepCenterSerializer for data serialization and deserialization.

    Attributes:
        queryset (QuerySet): A collection of all PrepCenter instances.
        serializer_class (Serializer): The serializer that converts PrepCenter instances 
            to and from JSON.

    Note:
        The permission_classes attribute is currently commented out. Uncomment and
        adjust it as needed to enforce authentication or any other permission policies.
    """
    # permission_classes = [IsAuthenticated]
    queryset = PrepCenter.objects.all()
    serializer_class = PrepCenterSerializer
