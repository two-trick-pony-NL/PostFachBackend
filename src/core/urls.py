from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .swaggerview import CustomSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/emails/', include('emails.urls')),
    path(r'django_rq/', include("django_rq.urls")),
    path("search/", include("search.urls")),



    # OpenAPI schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI only
    path('swagger/', CustomSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
