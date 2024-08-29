from profiles.models import Profile
from profiles.s3instance import S3Instance
from profiles.serializers import ProfileSerializer
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class UpdateProfileImageView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def put(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        profile_image_file = request.FILES.get("profile_image")
        if not profile_image_file:
            return Response(
                {"error": "No profile image provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # S3에 이미지 업로드
        s3instance = S3Instance().get_s3_instance()
        profile_image_url = S3Instance.upload_file(
            s3instance, profile_image_file, profile.user.id
        )

        # 기존 이미지 삭제 (선택 사항: S3에서도 삭제하려면 추가 구현 필요)
        if profile.profile_image:
            profile.profile_image.delete()

        # 새 이미지 URL로 프로필 업데이트
        profile.profile_image = profile_image_url
        profile.save()

        # 응답에서 S3 URL 반환
        return Response(
            {
                "message": "Profile image updated successfully.",
                "profile_image": profile_image_url,  # S3 URL을 직접 반환
            },
            status=status.HTTP_200_OK,
        )


class DeleteProfileImageView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if profile.profile_image:
            profile.profile_image.delete()
            profile.profile_image = None
            profile.save()

        return Response({"message": "Profile image deleted"}, status=status.HTTP_200_OK)
