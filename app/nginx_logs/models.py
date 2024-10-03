from django.db import models


# Create your models here.


class NginxLog(models.Model):
    """A log record model."""

    ip: models.GenericIPAddressField = models.GenericIPAddressField(
        verbose_name="IP Address",
        unpack_ipv4=True,
        blank=False,
        null=False,
        db_index=True,
    )
    date: models.DateTimeField = models.DateTimeField(
        verbose_name="Date", blank=False, null=False, db_index=True
    )
    method: models.CharField = models.CharField(
        verbose_name="HTTP Method", max_length=12, db_index=True
    )
    uri: models.CharField = models.CharField(
        verbose_name="URI", max_length=8 * 1024, db_index=True
    )
    status: models.IntegerField = models.IntegerField(
        verbose_name="HTTP Status", db_index=True
    )
    bytes_sent: models.IntegerField = models.IntegerField(verbose_name="Bytes sent")

    def __str__(self) -> str:
        return f"{self.date} {self.ip} -> {self.method} {self.uri} ({self.status})"

    class Meta:
        verbose_name = "Nginx log record"
        ordering = ("-date",)
