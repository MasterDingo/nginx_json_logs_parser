from django.contrib import admin
from django.db.models import Model as DBModel
from django.http import HttpRequest

from .models import NginxLog


# Register your models here.


class NginxLogAdmin(admin.ModelAdmin):
    """Admin panel view of NginxLog model."""

    list_display = ("date", "ip", "method", "uri", "status")
    list_filter = ("method", "uri", "status", "date")
    search_fields = ("uri", "ip", "date")
    ordering = ("-date",)

    def get_readonly_fields(
        self, request: HttpRequest, obj: DBModel | None = None
    ) -> list[str]:
        """Don't allow editing log records, but allow manually add them"""

        if obj:
            return list(self.readonly_fields) + [
                field.name for field in obj._meta.fields
            ]
        else:
            return list(self.readonly_fields)


admin.site.register(NginxLog, NginxLogAdmin)
