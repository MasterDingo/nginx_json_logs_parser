from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics

from nginx_logs.models import NginxLog

from .serializers import NginxLogSerializer


class NginxLogsView(generics.ListAPIView):
    """Main API view."""

    queryset = NginxLog.objects.all()
    serializer_class = NginxLogSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filterset_fields = ("method", "uri", "status")
    search_fields = ("uri", "ip", "date")
