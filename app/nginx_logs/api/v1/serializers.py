from rest_framework import serializers

from nginx_logs.models import NginxLog


class NginxLogSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%d/%b/%Y:%H:%M:%S %z")

    class Meta:
        model = NginxLog
        fields = "__all__"
