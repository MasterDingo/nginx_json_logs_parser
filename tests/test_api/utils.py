import json
import random


def field_wise_compare(json_dict, model):
    """
    Compares NginxLog model to JSON representation with assertions for each field.

    Args:
        json_dict (dict[str, any]): JSON representation.
        model (NginxLog): Django DB model.

    Raises:
        AssertionError: If any field's representations are not identical
    """
    assert model.ip == json_dict["ip"]
    assert model.date.strftime("%d/%b/%Y:%H:%M:%S %z") == json_dict["date"]
    assert model.method == json_dict["method"]
    assert model.uri == json_dict["uri"]
    assert model.status == json_dict["status"]
    assert model.bytes_sent == json_dict["bytes_sent"]


def api_filter_tester(client, url, models, field_name):
    """
    Helper function to test REST API filtering.

    Args:
        client: pytest's Client fixture.
        url (str): URL of API being tested.
        models (list[NginxLog]): a list of DB models which must be returned from API.
        field_name (str): model field and API query parameter name.

    Raises:
        AssertionError: If something is not as expected.
    """
    random_model = random.choices(models)[0]
    field_value = getattr(random_model, field_name)
    test_models = list(filter(lambda m: getattr(m, field_name) == field_value, models))

    response = client.get(f"{url}?{field_name}={field_value}&ordering=-date")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    json_resp = json.loads(response.content)
    assert json_resp["count"] == len(test_models)
    assert len(json_resp["results"]) == min(10, len(test_models))

    counter = 0
    for record in json_resp["results"]:
        field_wise_compare(record, test_models[counter])
        counter += 1


def api_search_tester(client, url, models, search):
    """
    Helper function to test REST API searching.

    Args:
        client: pytest's Client fixture
        url (str): URL of API being tested
        models (list[NginxLog]): a list of DB models which must be returned from API
        search (dict[str, str]): a dict with search terms with query parameter as a key and search term as a value

    Raises:
        AssertionError: If something is not as expected.
    """
    search_values = search.values()
    test_models = list(
        filter(
            lambda m: any(
                val in m.date.strftime("%d/%b/%Y:%H %M:%S") for val in search_values
            )
            or any(val in m.uri for val in search_values)
            or any(val in m.ip for val in search_values),
            models,
        )
    )

    search_params = "&".join([f"{field}={value}" for field, value in search.items()])
    response = client.get(f"{url}?{search_params}")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    json_resp = json.loads(response.content)
    assert json_resp["count"] == len(test_models)
    assert len(json_resp["results"]) == min(10, len(test_models))

    counter = 0
    for record in json_resp["results"]:
        field_wise_compare(record, test_models[counter])
        counter += 1
