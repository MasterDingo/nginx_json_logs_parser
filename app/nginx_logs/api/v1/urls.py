from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .views import NginxLogsView


urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="api-v1-schema"),
    path(
        "swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="api-v1-schema"),
        name="api-v1-swagger-ui",
    ),
    path("logs/", NginxLogsView.as_view(), name="api-v1-logs"),
]
