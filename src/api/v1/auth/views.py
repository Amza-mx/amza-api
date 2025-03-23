from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework.decorators import action


class AuthViewSet(viewsets.ViewSet):
    """
    ViewSet for JWT authentication endpoints.

    This viewset provides endpoints for JWT (JSON Web Token) authentication operations.
    It includes endpoints for obtaining tokens, refreshing tokens, and verifying tokens.

    Endpoints:
        - POST /api/v1/auth/jwt/token/ - Obtain JWT token pair (access + refresh)
        - POST /api/v1/auth/jwt/token/refresh/ - Refresh an expired access token
        - POST /api/v1/auth/jwt/token/verify/ - Verify a token's validity
    """
    permission_classes = []

    @action(detail=False, methods=['post'], url_path='jwt/token')
    def token(self, request):
        """
        Endpoint for obtaining JWT token pair.

        Generates new access and refresh tokens.

        Required fields:
            - username: User's username
            - password: User's password
        """
        return TokenObtainPairView.as_view()(request)

    @action(detail=False, methods=['post'], url_path='jwt/token/refresh')
    def token_refresh(self, request):
        """
        Endpoint for refreshing JWT access token.

        Generates new access token using refresh token.

        Required fields:
            - refresh: Valid refresh token
        """
        return TokenRefreshView.as_view()(request)

    @action(detail=False, methods=['post'], url_path='jwt/token/verify')
    def token_verify(self, request):
        """
        Endpoint for verifying JWT token validity.

        Verifies the provided token.

        Required fields:
            - token: JWT token to verify
        """
        return TokenVerifyView.as_view()(request)
