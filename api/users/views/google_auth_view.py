import requests
from common.logger import logger
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from users.models import User
from users.serializers import EmptySerializer
from users.utils import EmotreeAuthClass


class UserGoogleTokenReceiver(generics.GenericAPIView):
    serializer_class = EmptySerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info("UserGoogleTokenReceiver: POST /api/auth/google/receiver")
        try:
            access_token = request.data.get("access_token")
        except KeyError:
            logger.error("/api/auth/google/receiver: Access token is missing")
            return Response(
                {"message": "Access token is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Google API를 통해 사용자 정보 가져오기
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        userinfo_response = requests.get(
            userinfo_url, headers={"Authorization": f"Bearer {access_token}"}
        )

        if userinfo_response.status_code != 200:
            logger.error("/api/auth/google/receiver: Failed to get user info")
            return Response(
                {"message": "Failed to get user info"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        userinfo = userinfo_response.json()

        # 사용자 정보 저장 또는 업데이트
        email = userinfo.get("email")
        name = userinfo.get("name")

        try:
            with transaction.atomic():
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        "nickname": name,
                        "social_platform": "google",
                        "last_login": timezone.now(),
                    },
                )
                response = Response(
                    data={"message": "Login successful"}, status=status.HTTP_201_CREATED
                )

                if not created:
                    # 기존 회원이 존재하는 경우
                    user.last_login = timezone.now()
                    user.save()
                    response.status_code = status.HTTP_200_OK

                jwt_tokens = EmotreeAuthClass.set_auth_tokens_for_user(user)

            response = EmotreeAuthClass().set_jwt_auth_cookie(
                response=response, jwt_tokens=jwt_tokens
            )
            logger.info(f"/api/auth/google/receiver: {user}")
            return response

        except Exception as e:
            logger.error(f"/api/auth/google/receiver: {str(e)}")
            return Response(
                {"message": f"{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
