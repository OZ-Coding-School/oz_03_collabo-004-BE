from notifications.models import Notification
from rest_framework import serializers


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "recipient", "actor", "verb", "target", "read", "timestamp"]
        read_only_fields = ["id", "recipient", "actor", "verb", "target", "timestamp"]
