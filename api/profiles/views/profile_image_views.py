from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Profile
from .serializers import ProfileSerializer

#프로필 이미지 업데이트
class UpdateProfileImageView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def put(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        # 기존 이미지를 삭제
        if profile.profile_image:
            profile.profile_image.delete()

        # 새 이미지 업데이트
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#프로필 이미지 삭제(기본 이미지로 대체)   
class DeleteProfileImageView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        
        if profile.profile_image:
            profile.profile_image.delete()
            profile.profile_image = None 
            profile.save()

        return Response({"message": "Profile image deleted"}, status=status.HTTP_200_OK)