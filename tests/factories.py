import random

import factory
from django.utils.timezone import get_current_timezone
from factory.django import DjangoModelFactory as ModelFactory
from faker import Factory as FakerFactory

from nginx_logs.models import NginxLog


faker = FakerFactory.create()


class NginxLogFactory(ModelFactory):
    ip = factory.LazyAttribute(
        lambda x: faker.ipv4() if random.choices([True, False]) else faker.ipv6()
    )
    date = factory.LazyAttribute(
        lambda x: faker.date_time(tzinfo=get_current_timezone())
    )
    method = factory.LazyAttribute(lambda x: faker.http_method())
    status = factory.LazyAttribute(lambda x: faker.http_status_code())
    uri = factory.LazyAttribute(lambda x: "/" + faker.uri_path())
    bytes_sent = factory.LazyAttribute(lambda x: random.randint(120, 4096))

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return model_class(*args, **kwargs)

    class Meta:
        model = NginxLog


class SavedNginxLogFactory(NginxLogFactory):
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        instance.save()
        return instance

    class Meta:
        model = NginxLog
