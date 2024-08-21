from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from tags.serializers import TagSerializer

from .models import Profile


class ProfileSerializer(ModelSerializer):
    selected_tags = TagSerializer(many=True)
    nickname = serializers.CharField(source="user.nickname")

    class Meta:
        model = Profile
        fields = [
            "bio",
            "profile_image",
            "nickname",
            "selected_tags",
            "warning_count",
            "hunsoo_level",
        ]

    def validate_hunsoo_level(self, value):
        if value < 1 or value > 10:  # 훈수 레벨의 범위를 1에서 10으로 제한
            raise serializers.ValidationError("Invalid hunsoo level")
        return value

    def __init__(self, *args, **kwargs):
        # 필드를 동적으로 설정할 수 있게 합니다.
        fields = kwargs.pop("fields", None)
        super(ProfileSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # 설정된 필드만 남기고 나머지는 제거합니다.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
