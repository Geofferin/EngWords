from django.conf.urls import handler404
from django.urls import path, include
from first_app.views import page_not_found


urlpatterns = [
    path('', include('first_app.urls')),
    path('api/', include('first_app.api_urls', namespace='api')),
    path('users/', include('users.urls', namespace='users')),
]

handler404 = page_not_found
