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
        profile = Profile.objects.get(user=request.user)
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Profile image updated successfully.",
                "profile_image": serializer.data["profile_image"],
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
