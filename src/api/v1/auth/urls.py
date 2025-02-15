from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


urlpatterns = [
    path(
        'auth/',
        include(
            [
                path('jwt/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
                path('jwt/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
                path('jwt/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
            ]
        ),
    )
]
