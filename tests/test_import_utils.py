import pytest

from factories import NginxLogFactory
from nginx_logs.models import NginxLog
from app.utils import BatchModelWriter
from nginx_logs.utils.json_log_parsing import parse_json_log_record
from nginx_logs.utils.log_importer import LogImporter


def test_json_log_parsing(
    correct_json_log, json_log_no_brace, json_log_malformed_request, json_log_no_ip
):
    assert parse_json_log_record(correct_json_log) is not None
    assert parse_json_log_record(json_log_no_brace) is None
    assert parse_json_log_record(json_log_malformed_request) is None
    assert parse_json_log_record(json_log_no_ip) is None


def batch_writer_tester(batch_size: int):
    """Helper function to test ModelBatchWriter.

    Args:
        batch_size (int): A size of a batch to be used.

    Raises:
        AssertionError: If something is not as expected.
    """
    writer = BatchModelWriter[NginxLog](NginxLog, batch_size)
    # Ensure the models are not saved until the batch if full
    written_objects = 0
    for i in range(batch_size - 1):
        model = NginxLogFactory()
        written_objects += writer.add(model)
    assert written_objects == 0
    assert NginxLog.objects.count() == 0
    assert writer.current_batch_number == 1

    # Ensure all the models are saved in the end of the batch
    model = NginxLogFactory()
    written_objects = writer.add(model)
    assert written_objects == batch_size
    assert NginxLog.objects.count() == batch_size
    assert writer.current_batch_number == 2

    # Ensure flush() breaks the batch
    model = NginxLogFactory()
    written_objects = writer.add(model)
    assert written_objects == 0
    assert NginxLog.objects.count() == batch_size

    written_objects = writer.flush()
    assert written_objects == 1
    assert writer.current_batch_number == 3
    assert NginxLog.objects.count() == batch_size + 1


@pytest.mark.django_db
def test_batch_model_writer_3():
    batch_writer_tester(3)


@pytest.mark.django_db
def test_batch_model_writer_5():
    batch_writer_tester(5)


@pytest.mark.django_db
def test_log_importer(correct_json_log):
    importer = LogImporter(parse_json_log_record, 5)
    written_objects = 0
    for i in range(4):
        written_objects += importer.parse_line(correct_json_log)
    assert written_objects == 0
    assert NginxLog.objects.count() == 0
    assert importer.current_batch_number == 1

    # Ensure all the models are saved in the end of the batch
    written_objects = importer.parse_line(correct_json_log)
    assert written_objects == 5
    assert NginxLog.objects.count() == 5
    assert importer.current_batch_number == 2

    # Ensure flush() breaks the batch
    written_objects = importer.parse_line(correct_json_log)
    assert written_objects == 0
    assert NginxLog.objects.count() == 5

    written_objects = importer.flush()
    assert written_objects == 1
    assert importer.current_batch_number == 3
    assert NginxLog.objects.count() == 6
