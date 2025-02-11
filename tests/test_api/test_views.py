import json
import random

import pytest
from django.shortcuts import reverse

from utils import api_filter_tester, api_search_tester, field_wise_compare


@pytest.fixture
def model_set(saved_nginx_log_factory):
    return sorted(
        (saved_nginx_log_factory() for i in range(100)),
        key=lambda model: model.date,
        reverse=True,
    )


@pytest.mark.django_db
def test_api_basic(client):
    url = reverse("api-v1-logs")
    response = client.get(url)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    json_resp = json.loads(response.content)
    assert "results" in json_resp
    assert "next" in json_resp
    assert "previous" in json_resp
    assert "count" in json_resp

    assert json_resp["count"] == 0
    assert json_resp["results"] == []


@pytest.mark.django_db
def test_api_content(client, model_set):
    url = reverse("api-v1-logs")
    response = client.get(url)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    json_resp = json.loads(response.content)
    counter = 0
    for record in json_resp["results"]:
        field_wise_compare(record, model_set[counter])
        counter += 1

    next_url = json_resp["next"]
    assert len(next_url) > 0
    assert json_resp["previous"] is None

    response = client.get(next_url)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    json_resp = json.loads(response.content)
    for record in json_resp["results"]:
        field_wise_compare(record, model_set[counter])
        counter += 1

    assert len(json_resp["previous"]) > 0


@pytest.mark.django_db
def test_api_filter_method(client, model_set):
    url = reverse("api-v1-logs")
    api_filter_tester(client, url, model_set, "method", 10)
    api_filter_tester(client, url, model_set, "method", 20)


@pytest.mark.django_db
def test_api_filter_uri(client, model_set):
    url = reverse("api-v1-logs")
    api_filter_tester(client, url, model_set, "uri", 10)
    api_filter_tester(client, url, model_set, "uri", 20)


@pytest.mark.django_db
def test_api_filter_status(client, model_set):
    url = reverse("api-v1-logs")
    api_filter_tester(client, url, model_set, "status", 10)
    api_filter_tester(client, url, model_set, "status", 20)


@pytest.mark.django_db
def test_api_search_by_ip(client, model_set):
    url = reverse("api-v1-logs")
    sample_model = random.choice(model_set)
    sample_ip = sample_model.ip
    api_search_tester(client, url, model_set, {"q": sample_ip}, 10)
    api_search_tester(client, url, model_set, {"q": sample_ip}, 20)


@pytest.mark.django_db
def test_api_search_by_uri(client, model_set):
    url = reverse("api-v1-logs")
    sample_model = random.choice(model_set)
    sample_uri = sample_model.uri
    api_search_tester(client, url, model_set, {"q": sample_uri}, 10)
    api_search_tester(client, url, model_set, {"q": sample_uri}, 20)


@pytest.mark.django_db
def test_api_search_by_date(client, settings, model_set):
    settings.USE_TZ = False
    url = reverse("api-v1-logs")
    sample_model = random.choice(model_set)
    sample_date = sample_model.date.strftime("%d/%b/%Y %H:%M:%S")
    api_search_tester(client, url, model_set, {"q": sample_date}, 10)
    api_search_tester(client, url, model_set, {"q": sample_date}, 20)
