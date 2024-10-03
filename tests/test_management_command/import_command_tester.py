import importlib

from output_parsers import (
    StderrStatType,
    StdoutStatType,
    parse_stderr,
    parse_stdout,
)


# import is a reserved word in Python, so we go another way around
Command = importlib.import_module("nginx_logs.management.commands.import").Command


def import_command_tester(
    tmpdir_or_monkeypatch,
    capsys,
    good_records_count: int,
    batch_size: int,
    good_log: str,
    bad_records: list[tuple[int, str]],
    use_stdin: bool = False,
) -> tuple[StdoutStatType, StderrStatType]:
    """Helper function for management command testing

    :param tmpdir_or_monkeypatch: one of pytest's fixtures: Tmpdir or Monkeypatch
    :param capsys: pytest's Capsys fixture
    :param int good_records_count: a total number of valid log records to send into the command
    :param int batch_size: a number of lines to be processed in one batch
    :param str good_log: valid log line
    :param bad_records: a list of tuples with line number and content of invalid log records
    :param bool use_stdin: whether to use a temp file for input (first parameter must be a Tmpdir) or STDIN (with Monkeypatch as a first parameter)
    :return: a tuple with parsed STDOUT and STDERR output (see parsing functions in output_parsers.py for details)
    """
    rest_good_recs = good_records_count
    line_number = 0
    logs = []

    # Create log file records
    for bad_pos, bad_line in sorted(bad_records, key=lambda rec: rec[0]):
        bad_pos = bad_pos - line_number
        if bad_pos > rest_good_recs:
            # Improper bad_records argument
            assert False, f"Invalid bad records offset {bad_pos} with only {good_records_count} good records"
        logs.append("\n".join((good_log for i in range(bad_pos - 1))))
        logs.append(bad_line)
        line_number += bad_pos
        rest_good_recs -= bad_pos - 1

    logs.append("\n".join((good_log for i in range(rest_good_recs))))
    logs_string = "\n".join(logs)
    file_path: str
    if use_stdin:
        from io import StringIO

        file_path = "-"
        # Change `open` function
        tmpdir_or_monkeypatch.setattr(
            "builtins.open",
            lambda fd, mode: StringIO(logs_string) if fd == 0 else open(fd, mode),
        )
    else:
        # Make temporary file
        log_file = tmpdir_or_monkeypatch.join("json_log.txt")
        log_file.write(logs_string)
        file_path = log_file.strpath

    command = Command()
    command.handle(filename=file_path, batch_size=batch_size)

    output = capsys.readouterr()
    stdout_stat = parse_stdout(output.out)
    stderr_stat = parse_stderr(output.err)

    return (stdout_stat, stderr_stat)
