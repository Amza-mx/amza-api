import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

logger = logging.getLogger(__name__)


class HealthCheckAPIView(APIView):
    """
    Healthcheck endpoint to verify that the API is running.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        logger.info(f"Healthcheck accessed from {request.META.get('REMOTE_ADDR')}")
        return Response({"status": "ok"})
