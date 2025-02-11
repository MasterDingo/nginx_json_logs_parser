from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.pagination import PageNumberPagination

from nginx_logs.models import NginxLog

from .serializers import NginxLogSerializer

class NginxLogsPagination(PageNumberPagination):
    """Pagination class for Nginx logs."""
    page_size = 20
    page_query_param = 'page'
    page_size_query_param = 'size'
    max_page_size = 1000

class NginxLogsView(generics.ListAPIView):
    """API view for listing Nginx logs."""

    queryset = NginxLog.objects.all()
    serializer_class = NginxLogSerializer
    pagination_class = NginxLogsPagination
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filterset_fields = ("method", "uri", "status")
    search_fields = ("uri", "ip", "date")
