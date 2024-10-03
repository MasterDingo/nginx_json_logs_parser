from collections.abc import Callable
from typing import Any, Iterator

from django.dispatch import Signal

from app.utils import BatchModelWriter
from nginx_logs.models import NginxLog

from .log_types import LogRecord


line_parsed = Signal()
malformed_line = Signal()
flushed = Signal()


class LogImporter:
    """Parses logs on line-by-line basis and stores them into DB in a bulk operations.

    Args:
        parser (Callable): A callable to parse one log line.
        batch_size (int): How many records to store in one bulk operation.
    """

    def __init__(self, parser: Callable[[str], LogRecord], batch_size: int) -> None:
        self.__parser = parser
        self.__batch_size = batch_size
        self.__writer = BatchModelWriter[NginxLog](NginxLog, batch_size)
        self.__total_lines = 0
        self.__skipped_lines = 0
        self.__subscribers: dict[str, list[Callable[[Any], None]]] = {}

    @property
    def current_batch_number(self) -> int:
        """A number of the current batch"""
        return self.__writer.current_batch_number

    def parse(self, lines: Iterator[str]) -> None:
        """Parse an iterable of log lines.

        Args:
            lines (Iterator[str]): Log lines.
        """
        for line in lines:
            self.parse_line(line)
        self.flush()

    def parse_line(self, line: str) -> int:
        """Adds one log line to parse.

        Args:
            line (str): New log line.

        Returns:
            A number of stored DB models this time or -1 if failed to parse the log string.
        """
        self.__total_lines += 1
        parsed_line = self.__parser(line)
        if parsed_line is not None:
            line_parsed.send_robust(
                self,
                batch_number=self.current_batch_number,
                line_number=self.__total_lines,
            )

            model = NginxLog(**(parsed_line._asdict()))
            records_stored = self.__writer.add(model)
            if records_stored > 0:
                flushed.send_robust(
                    self,
                    batch_number=self.current_batch_number - 1,
                    records_stored=records_stored,
                    batch_incomplete=records_stored < self.__batch_size,
                )
            return records_stored
        else:
            malformed_line.send_robust(
                self,
                batch_number=self.current_batch_number,
                line_number=self.__total_lines,
                text=line,
            )

            self.__skipped_lines += 1
            return -1

    def flush(self) -> int:
        """Immediately flushes incomplete batch.

        Returns:
            Stored records count.
        """
        records_stored = self.__writer.flush()
        flushed.send_robust(
            self,
            batch_number=self.current_batch_number - 1,
            records_stored=records_stored,
            batch_incomplete=records_stored < self.__batch_size,
        )
        return records_stored

    @property
    def stats(self):
        writer_stats = self.__writer.stats
        return {
            "total": self.__total_lines,
            "skipped": self.__skipped_lines,
            "stored": writer_stats["total"],
            "incomplete_batches": writer_stats["incomplete_batches"],
        }
