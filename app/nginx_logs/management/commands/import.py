from django.conf import settings
from django.core.management.base import BaseCommand

from nginx_logs.utils import (
    LogImporter,
    flushed,
    malformed_line,
    parse_json_log_record,
)


class Command(BaseCommand):
    help = "Imports Nginx log file into the database. Log data may be read from a file or stdin."

    def add_arguments(self, parser):  # pragma: no cover
        """Add filename argument"""
        parser.add_argument("filename", type=str)
        parser.add_argument(
            "--batch-size",
            type=int,
            default=None,
            help="The number of records to store into DB at once",
        )

    def handle(self, *args, **options):
        """Make import"""
        filename = options["filename"]
        if filename.strip() == "-":
            # If we are told to use the standard input, use its handle as a file name
            filename = 0

        batch_size = options.get("batch_size") or settings.LOG_BATCH_SIZE
        importer = LogImporter(parse_json_log_record, batch_size)

        # Connect signal handlers for the importer instance
        malformed_line.connect(self.malformed_line_handler, sender=importer)
        flushed.connect(self.flushed_handler, sender=importer)

        # Do import
        importer.parse(open(filename, "r"))

        stats = importer.stats
        if stats["total"] == 0:
            self.stdout.write("No records were read.")
        else:
            self.stdout.write(
                f"\nTotal {stats['total']} records read, {stats['skipped']} skipped and {stats['stored']} stored."
            )

    def malformed_line_handler(self, /, batch_number, line_number, text, **kwargs):
        """Signal handler for malformed_line"""
        self.stderr.write(
            f"Batch #{batch_number}: Skipping malformed line #{line_number}:\n{text}\n"
        )

    def flushed_handler(
        self, /, batch_number, records_stored, batch_incomplete, **kwargs
    ):
        """Signal handler for flushed"""
        if batch_incomplete:
            if records_stored > 0:
                self.stdout.write(
                    f"Stored extra {records_stored} records from incomplete batch #{batch_number}."
                )
        else:
            self.stdout.write(
                f"Batch #{batch_number}: Stored {records_stored} records."
            )
