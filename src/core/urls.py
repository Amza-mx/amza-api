from django.contrib import admin
from django.urls import path, include

admin.site.site_header = 'Amza API'
admin.site.site_title = 'Amza API'
admin.site.index_title = 'Welcome to Amza API'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
