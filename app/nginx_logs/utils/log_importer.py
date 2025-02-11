from collections.abc import Callable
from typing import Iterator

from django.dispatch import Signal

from app.utils import BatchModelWriter
from nginx_logs.models import NginxLog

from .log_types import LogRecord


line_parsed_signal = Signal()
malformed_line_signal = Signal()
flushed_signal = Signal()


class LogImporter:
    """
    A class to parse logs line-by-line and stores them into DB in bulk operations.

    Args:
        parser (Callable): A callable object to parse a log line.
        batch_size (int): The number of records to store in one bulk operation.

    Attributes:
        current_batch_number (property): The current batch number.
        stats (property): The statistics of log parsing and storing.
    """

    def __init__(self, parser: Callable[[str], LogRecord], batch_size: int) -> None:
        self.__parser = parser
        self.__batch_size = batch_size
        self.__writer = BatchModelWriter[NginxLog](NginxLog, batch_size)
        self.__total_lines = 0
        self.__skipped_lines = 0

    @property
    def current_batch_number(self) -> int:
        """The current batch number."""
        return self.__writer.current_batch_number

    @property
    def stats(self) -> dict[str, int]:
        """
        The statistics of log parsing and storing.

        Returns:
            dict: A dictionary containing the total lines, skipped lines, stored records, and incomplete batches.
        """
        writer_stats = self.__writer.stats
        return {
            "total": self.__total_lines,
            "skipped": self.__skipped_lines,
            "stored": writer_stats["total"],
            "incomplete_batches": writer_stats["incomplete_batches"],
        }

    def parse(self, lines: Iterator[str]) -> None:
        """
        Parse an iterable of log lines.

        Args:
            lines (Iterator[str]): An iterable of log lines.
        """
        for line in lines:
            self.parse_line(line)
        self.flush()

    def parse_line(self, line: str) -> int:
        """
        Parse a single log line.

        Args:
            line (str): The log line to be parsed.

        Returns:
            int: The number of stored DB models this time, or -1 if failed to parse the log string.
        """
        self.__total_lines += 1
        parsed_line = self.__parser(line)
        if parsed_line is None:
            malformed_line_signal.send_robust(
                self,
                batch_number=self.current_batch_number,
                line_number=self.__total_lines,
                text=line,
            )

            self.__skipped_lines += 1
            return -1

        line_parsed_signal.send_robust(
            self,
            batch_number=self.current_batch_number,
            line_number=self.__total_lines,
        )

        model = NginxLog(**(parsed_line._asdict()))
        records_stored = self.__writer.add(model)
        if records_stored > 0:
            flushed_signal.send_robust(
                self,
                batch_number=self.current_batch_number - 1,
                records_stored=records_stored,
                batch_incomplete=records_stored < self.__batch_size,
            )

        return records_stored

    def flush(self) -> int:
        """
        Immediately flush the incomplete batch.

        Returns:
            int: The number of stored records.
        """
        records_stored = self.__writer.flush()
        flushed_signal.send_robust(
            self,
            batch_number=self.current_batch_number - 1,
            records_stored=records_stored,
            batch_incomplete=records_stored < self.__batch_size,
        )
        return records_stored
