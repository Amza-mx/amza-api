from django.urls import path, include


urlpatterns = [
	path(
		'',
		include([
			path('', include('api.v1.urls'))
		])
	),
]