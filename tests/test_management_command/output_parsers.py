import enum
import re


STDERR_SYS_STRING_REGEX = re.compile(
    r"Batch #(?P<batch_number>\d+): Skipping malformed line #(?P<line_number>\d+):"
)

STDOUT_STORE_REGEX = re.compile(
    r"Batch #(?P<batch_number>\d+): Stored (?P<record_count>\d+) records."
)
STDOUT_EXTRA_REGEX = re.compile(
    r"Stored extra (?P<extra_count>\d+) records from incomplete batch #(?P<last_batch_number>\d+)."
)
STDOUT_TOTAL_REGEX = re.compile(
    r"Total (?P<total_count>\d+) records read, (?P<skipped_count>\d+) skipped and (?P<stored_count>\d+) stored."
)
STDOUT_NO_RECORDS_REGEX = re.compile(r"No records were read.")

StdoutStatType = tuple[
    list[tuple[int, int]], tuple[int, int] | None, tuple[int, int, int]
]
StderrStatType = list[tuple[int, int, str]]


class StderrParsingState(enum.Enum):
    SYS_LINE = 0
    LOG_LINE = 1
    EMPTY_LINE = 2


def parse_stderr(text: str) -> StderrStatType:
    """Parses stderr output of the import command.

    Args:
        text (str): stderr output of the import management command.

    Returns:
        A list of tuples each of which contains a batch number, a wrong line number and the text of a wrong line.
    """
    output: list[tuple[int, int, str]] = []
    state = StderrParsingState.SYS_LINE

    batch_number = 0
    line_number = 0
    log_line = ""
    for line in text.splitlines():
        match state:
            case StderrParsingState.SYS_LINE:
                # Here we get the batch number and the line number
                parsed = STDERR_SYS_STRING_REGEX.match(line)
                if parsed is not None:
                    batch_number, line_number = (
                        int(parsed.group("batch_number")),
                        int(parsed.group("line_number")),
                    )
                state = StderrParsingState.LOG_LINE
            case StderrParsingState.LOG_LINE:
                # Just store the malformed log line
                log_line = line.strip()
                state = StderrParsingState.EMPTY_LINE
            case StderrParsingState.EMPTY_LINE:
                # Add the info we got to the output list
                output.append((batch_number, line_number, log_line))
                state = StderrParsingState.SYS_LINE

    return output


class StdoutParsingState(enum.Enum):
    STORE_LINE = 0
    EMPTY_LINE = 1
    TOTAL_LINE = 2


def parse_stdout(text: str) -> StdoutStatType:
    """Parses stdout output of the import command.

    Args:
        text (str): stderr output of the import management command.

    Returns:
        A tuple of the following entities:
            a list of tuples which contain a batch number and stored records count.
            a tuple of last (incomplete) batch number and stored records count, or None if there was no incomplete batch.
            a tuple of total statistics: total lines read, skipped lines count and stored lines count.
    """
    batch_lines: list[tuple[int, int]] = []
    extra_line = None
    total_line: tuple[int, int, int] = (0, 0, 0)
    state = StdoutParsingState.STORE_LINE

    for line in text.splitlines():
        match state:
            case StdoutParsingState.STORE_LINE:
                batch_stat = STDOUT_STORE_REGEX.match(line)
                if batch_stat is not None:
                    # This line tells about a normal batch flushing
                    batch_lines.append(
                        (
                            int(batch_stat.group("batch_number")),
                            int(batch_stat.group("record_count")),
                        )
                    )
                else:
                    if STDOUT_NO_RECORDS_REGEX.match(line):
                        # This line tells that no lines were read
                        total_line = (0, 0, 0)
                    else:
                        extra_stat = STDOUT_EXTRA_REGEX.match(line)
                        if extra_stat is not None:
                            # This line tells about a final (incomplete) batch flushing
                            extra_line = (
                                int(extra_stat.group("extra_count")),
                                int(extra_stat.group("last_batch_number")),
                            )
                            state = StdoutParsingState.EMPTY_LINE
                        else:
                            state = StdoutParsingState.TOTAL_LINE
            case StdoutParsingState.EMPTY_LINE:
                # Blank line before total statistics
                state = StdoutParsingState.TOTAL_LINE
            case StdoutParsingState.TOTAL_LINE:
                # Total statistics in the end of the importing process
                total_stat = STDOUT_TOTAL_REGEX.match(line)
                if total_stat is not None:
                    total_line = (
                        int(total_stat.group("total_count")),
                        int(total_stat.group("skipped_count")),
                        int(total_stat.group("stored_count")),
                    )

    return (batch_lines, extra_line, total_line)
