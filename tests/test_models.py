import pytest

from nginx_logs.models import NginxLog


@pytest.mark.django_db
def test_string_representation(nginx_log):
    assert (
        str(nginx_log)
        == f"{nginx_log.date} {nginx_log.ip} -> {nginx_log.method} {nginx_log.uri} ({nginx_log.status}) - {nginx_log.bytes_sent} bytes"
    )
    assert NginxLog.objects.count() == 1
