import pytest

from import_command_tester import import_command_tester
from nginx_logs.models import NginxLog


def test_import_command_with_empty_logs(tmpdir, capsys):
    stdout_stat, stderr_stat = import_command_tester(
        tmpdir,
        capsys,
        0,
        5,
        "",
        [],
    )
    # no batches, no errors, 0 lines read, 0 skipped, 0 stored
    assert stdout_stat == ([], None, (0, 0, 0))
    # no errors
    assert stderr_stat == []


@pytest.mark.django_db
def test_import_command_with_extra(
    tmpdir, capsys, correct_json_log, json_log_malformed_request, json_log_no_brace
):
    stdout_stat, stderr_stat = import_command_tester(
        tmpdir,
        capsys,
        90,
        7,
        correct_json_log,
        [(11, json_log_malformed_request), (42, json_log_no_brace)],
    )
    assert stdout_stat == (
        [(i, 7) for i in range(1, 13)],  # 12 batches by 7 records
        (6, 13),  # 6 extra records from incomplete batch #13
        (92, 2, 90),  # total 92 lines read, 2 skipped and 90 stored
    )
    assert stderr_stat == [
        # Batch #2, line #11, log line with a malformed request field
        (
            2,
            11,
            json_log_malformed_request,
        ),
        # Batch #6, line #42, log line with absent closing curly bracket
        (
            6,
            42,
            json_log_no_brace,
        ),
    ]
    assert NginxLog.objects.count() == 90


@pytest.mark.django_db
def test_import_command_without_extra(
    tmpdir, capsys, correct_json_log, json_log_malformed_request, json_log_no_brace
):
    stdout_stat, stderr_stat = import_command_tester(
        tmpdir,
        capsys,
        90,
        5,
        correct_json_log,
        [(11, json_log_malformed_request), (42, json_log_no_brace)],
    )
    assert stdout_stat == (
        [(i, 5) for i in range(1, 19)],  # 18 batches by 5 records
        None,  # no incomplete batches
        (92, 2, 90),  # total 92 lines read, 2 skipped and 90 stored
    )
    assert stderr_stat == [
        # Batch #3, line #11, log line with a malformed request field
        (
            3,
            11,
            json_log_malformed_request,
        ),
        # Batch #9, line #42, log line with absent closing curly bracket
        (
            9,
            42,
            json_log_no_brace,
        ),
    ]
    assert NginxLog.objects.count() == 90


@pytest.mark.django_db
def test_import_command_with_extra_no_skip(
    tmpdir, capsys, correct_json_log, json_log_malformed_request, json_log_no_brace
):
    stdout_stat, stderr_stat = import_command_tester(
        tmpdir,
        capsys,
        90,
        7,
        correct_json_log,
        [],
    )
    assert stdout_stat == (
        [(i, 7) for i in range(1, 13)],  # 12 batches by 7 records
        (6, 13),  # 6 extra records from incomplete batch #13
        (90, 0, 90),  # total 90 lines read, 0 skipped and 90 stored
    )
    assert stderr_stat == []
    assert NginxLog.objects.count() == 90


@pytest.mark.django_db
def test_import_command_without_extra_no_skipped(
    tmpdir, capsys, correct_json_log, json_log_malformed_request, json_log_no_brace
):
    stdout_stat, stderr_stat = import_command_tester(
        tmpdir,
        capsys,
        90,
        5,
        correct_json_log,
        [],
    )
    assert stdout_stat == (
        [(i, 5) for i in range(1, 19)],  # 18 batches by 5 records
        None,  # no incomplete batches
        (90, 0, 90),  # total 90 lines read, 0 skipped and 90 stored
    )
    assert stderr_stat == []
    assert NginxLog.objects.count() == 90
