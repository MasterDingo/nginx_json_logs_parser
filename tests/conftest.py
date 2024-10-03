import json
import random
from datetime import datetime

import pytest
from django.utils.timezone import get_current_timezone
from faker import Factory as FakerFactory
from pytest_factoryboy import register

from factories import NginxLogFactory, SavedNginxLogFactory


faker = FakerFactory.create()


@pytest.fixture
def any_ip():
    return faker.ipv4() if random.choices([True, False]) else faker.ipv6()


@pytest.fixture
def now():
    return datetime.now()


@pytest.fixture
def json_log_dict(any_ip):
    return {
        "time": faker.date_time(tzinfo=get_current_timezone()).strftime(
            "%d/%b/%Y:%H:%M:%S %z"
        ),
        "request": f"{faker.http_method()} {'/' + faker.uri_path()} HTTP/1.1",
        "remote_ip": any_ip,
        "remote_user": "-",
        "response": faker.http_status_code(),
        "bytes": random.randint(0, 4096),
        "referrer": "-",
    }


@pytest.fixture
def correct_json_log(json_log_dict):
    return json.dumps(json_log_dict)


@pytest.fixture
def json_log_no_brace(correct_json_log):
    return correct_json_log.strip()[:-1]


@pytest.fixture
def json_log_malformed_request(json_log_dict):
    json_log_dict["request"] = json_log_dict["request"].replace(" ", "")
    return json.dumps(json_log_dict)


@pytest.fixture
def json_log_no_ip(json_log_dict):
    del json_log_dict["remote_ip"]
    return json.dumps(json_log_dict)


register(NginxLogFactory)
register(SavedNginxLogFactory)
