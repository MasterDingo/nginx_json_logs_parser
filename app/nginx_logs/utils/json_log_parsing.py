import json
from datetime import datetime

from .log_types import LogRecord, ParsedRequest


LOG_DATETIME_FORMAT = "%d/%b/%Y:%H:%M:%S %z"


def parse_request_line(input: str) -> ParsedRequest | None:
    """Parse request string into method and URI.

    Args:
        input (str): Request string.

    Returnes:
        ParsedRequest named tuple or None if failed to parse.
    """
    if input.count(" ") == 2:
        # Input string must have at least 2 spaces: after HTTP method and before HTTP version
        first_space_idx = input.index(" ")
        last_space_idx = input.rindex(" ")
        method = input[:first_space_idx]
        uri = input[first_space_idx + 1 : last_space_idx]

        return ParsedRequest(method, uri)
    return None


def parse_json_log_record(line: str) -> LogRecord | None:
    """Parse a full JSON log line.

    Args:
        line (str): One line of JSON log

    Returns:
        LogRecord named tuple
    """
    try:
        item = json.loads(line)
    except json.JSONDecodeError:
        return None

    # Parse a `request` field into a method and URI
    # Early return if the dict has no such key
    if "request" in item:
        parsed_request = parse_request_line(item["request"])
        if parsed_request is not None:
            try:
                date = datetime.strptime(item["time"], LOG_DATETIME_FORMAT)
            except ValueError:
                return None

            return LogRecord(
                ip=item["remote_ip"],
                date=date,
                method=parsed_request.method,
                uri=parsed_request.uri,
                status=item["response"],
                bytes_sent=item["bytes"],
            )

    return None
