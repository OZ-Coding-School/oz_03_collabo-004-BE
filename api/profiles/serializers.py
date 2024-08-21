from rest_framework.serializers import ModelSerializer

from .models import Profile, Tag


class ProfileSerializer(ModelSerializer):
    selected_tags = TagSerializer(many=True)  # TagSerializer를 사용해 태그 정보 직렬화

    class Meta:
        model = Profile  # UserProfile에서 Profile로 변경
        fields = [
            "bio",
            "profile_image",
            "nickname",
            "selected_tags",
            "warning_count",
            "hunsoo_level",
        ]
