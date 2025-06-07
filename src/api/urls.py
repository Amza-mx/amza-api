from django.urls import include, path
from api.v1.urls import router as v1_router

# Main URL Pattern for the API
urlpatterns = [
    path('v1/', include(v1_router.urls)),
]
