import pytest
from django.shortcuts import reverse


@pytest.mark.django_db
def test_main_page(client):
    response = client.get(reverse("main-page"))
    assert response.status_code == 302
    assert response.headers["location"] == reverse("api-v1-swagger-ui")
