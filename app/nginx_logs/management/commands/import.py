from django.conf import settings
from django.core.management.base import BaseCommand

from nginx_logs.utils import (
    LogImporter,
    flushed_signal,
    malformed_line_signal,
    parse_json_log_record,
)


class Command(BaseCommand):
    """
    This Django management command imports Nginx log file into the database.
    It can read log data either from a file or standard input.
    """

    help = "Imports Nginx log file into the database. Log data may be read from a file or stdin."

    def add_arguments(self, parser):  # pragma: no cover
        """
        Adds filename argument and an optional batch size argument to the command line parser.

        Args:
            parser (django.core.management.base.ArgumentParser): The command line parser.

        Returns:
            None
        """
        parser.add_argument("filename", type=str)
        parser.add_argument(
            "--batch-size",
            type=int,
            default=None,
            help="The number of records to store into DB at once",
        )

    def handle(self, *args, **options):
        """
        Main function that runs the import process.
        It connects signal handlers for malformed_line and flushed signals,
        and then it uses the LogImporter utility to parse the JSON file and store the records
        in batches into the Django database.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments.

        Returns:
            None
        """
        filename = options["filename"]
        if filename.strip() == "-":
            # If we are told to use the standard input, use its handle as a file name
            filename = 0

        batch_size = options.get("batch_size", settings.LOG_BATCH_SIZE)
        try:
            importer = LogImporter(parse_json_log_record, batch_size)
        except Exception:
            return

        # Connect signal handlers for the importer instance
        malformed_line_signal.connect(self.malformed_line_handler, sender=importer)
        flushed_signal.connect(self.flushed_handler, sender=importer)

        try:
            # Do import
            importer.parse(open(filename, "r"))
        finally:
            # Print the final statistics
            stats = importer.stats
            if stats["total"] == 0:
                self.stdout.write("No records were read.")
            else:
                self.stdout.write(
                    f"\nTotal {stats['total']} records read, {stats['skipped']} skipped and {stats['stored']} stored."
                )

            # Disconnect signal handlers
            malformed_line_signal.disconnect(
                self.malformed_line_handler, sender=importer
            )
            flushed_signal.disconnect(self.flushed_handler, sender=importer)

    def malformed_line_handler(
        self, /, batch_number: int, line_number: int, text: str, **kwargs
    ):
        """
        Signal handler for malformed_line.
        Logs an error message indicating the skipped malformed line.

        Args:
            batch_number (int): The batch number.
            line_number (int): The line number of the malformed line.
            text (str): The text of the malformed line.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """
        self.stderr.write(
            f"Batch #{batch_number}: Skipping malformed line #{line_number}:\n{text}\n"
        )

    def flushed_handler(
        self,
        /,
        batch_number: int,
        records_stored: int,
        batch_incomplete: bool,
        **kwargs,
    ):
        """
        Signal handler for flushed.
        Logs a message indicating the number of records stored in the batch.

        Args:
            batch_number (int): The batch number.
            records_stored (int): The number of records stored in the batch.
            batch_incomplete (bool): Whether the batch is incomplete.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """
        if batch_incomplete:
            if records_stored > 0:
                self.stdout.write(
                    f"Stored extra {records_stored} records from incomplete batch #{batch_number}."
                )
        else:
            self.stdout.write(f"Batch #{batch_number}: Stored {records_stored} records.")
