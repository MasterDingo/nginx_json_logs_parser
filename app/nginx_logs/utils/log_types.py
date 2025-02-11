from typing import NamedTuple
from datetime import datetime


class ParsedRequest(NamedTuple):
    """
    Represents a parsed Nginx request.

    :ivar method: HTTP method (e.g., GET, POST)
    :ivar uri: Request URI
    """

    method: str
    uri: str


class LogRecord(NamedTuple):
    """
    Represents a parsed Nginx log record.

    :ivar ip: Client IP address
    :ivar date: Date and time of the log entry
    :ivar method: HTTP method (e.g., GET, POST)
    :ivar uri: Request URI
    :ivar status: HTTP status code
    :ivar bytes_sent: Number of bytes sent by the server
    """

    ip: str
    date: datetime
    method: str
    uri: str
    status: int
    bytes_sent: int
