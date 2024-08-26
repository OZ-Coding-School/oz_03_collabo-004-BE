from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True)
    target_object = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "actor_username",
            "verb",
            "target_object",
            "read",
            "timestamp",
        ]

    def get_target_object(self, obj):
        # 객체의 문자열 표현을 반환하거나 필요에 따라 객체의 세부 사항을 반환
        return str(obj.target)
