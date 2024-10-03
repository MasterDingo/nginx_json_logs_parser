from collections import namedtuple


ParsedRequest = namedtuple("ParsedRequest", "method uri")
LogRecord = namedtuple("LogRecord", "ip date method uri status bytes_sent")
