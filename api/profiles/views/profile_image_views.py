import boto3
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Profile
from ..serializers import ProfileImageSerializer, ProfileSerializer

# 프로필 이미지 업데이트
# class UpdateProfileImageView(generics.UpdateAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = ProfileImageSerializer

#     def put(self, request, *args, **kwargs):
#         try:
#             profile = Profile.objects.get(user=request.user)
#         except Profile.DoesNotExist:
#             return Response(
#                 {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
#             )

#         # 기존 이미지를 삭제
#         if profile.profile_image:
#             profile.profile_image.delete()

#             # 새 이미지 업데이트
#             serializer = self.get_serializer(profile, data=request.data, partial=True)
#             if serializer.is_valid():
#                 if "profile_image" in request.data:
#                     serializer.save()
#                     return Response(serializer.data, status=status.HTTP_200_OK)
#                 else:
#                     return Response(
#                         {"error": "No image provided"},
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateProfileImageView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.all()
    serializer_class = ProfileImageSerializer

    def get_object(self):
        return self.request.user.profile

    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# 프로필 이미지 삭제(기본 이미지로 대체)
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
