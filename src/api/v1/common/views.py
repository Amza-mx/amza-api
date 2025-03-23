from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet that includes common functionality:
    - Authentication
    - Rate limiting
    - Filtering
    - Searching
    - Ordering
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['created_at', 'updated_at']
    ordering_fields = ['created_at', 'updated_at', 'id']
    ordering = ['-created_at'] 