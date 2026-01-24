from django.urls import include, path

# Main URL Pattern for the API
urlpatterns = [
    path('v1/', include('api.v1.urls')),
]
