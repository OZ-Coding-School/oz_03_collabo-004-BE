import requests
from common.logger import logger
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from users.models import User
from users.serializers import EmptySerializer
from users.utils import HunsooKingAuthClass


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

        # Google API를 통해 access token validity check
        token_info_url = "https://www.googleapis.com/oauth2/v3/tokeninfo"
        token_info_response = requests.get(
            f"{token_info_url}?access_token={access_token}"
        )

        if token_info_response.status_code != 200:
            return Response(
                {"message": "Invalid or expired access token"},
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
            user = User.objects.get(email=email)

            if user.social_platform == "general":
                # 이미 일반 회원가입으로 가입된 이메일인 경우 오류 반환
                return Response(
                    {"message": "이미 일반 회원가입으로 가입된 이메일입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            elif user.social_platform == "google":
                # 기존 구글 소셜 로그인 회원인 경우 로그인 처리
                user.last_login = timezone.now()
                user.save()
                created = False

        except User.DoesNotExist:
            # 신규 구글 소셜 로그인 회원인 경우 회원 가입 및 로그인 처리
            user = User.objects.create_user(
                email=email,
                username=None,
                password=None,
                nickname=name,
                social_platform="google",
                last_login=timezone.now(),
            )
            created = True

        response = Response(data={"message": "Login successful"})

        if not created:  # 기존 회원인 경우
            response.status_code = status.HTTP_200_OK
        else:  # 신규 회원인 경우
            response.status_code = status.HTTP_201_CREATED

        jwt_tokens = HunsooKingAuthClass.set_auth_tokens_for_user(user)
        response = HunsooKingAuthClass().set_jwt_auth_cookie(
            response=response, jwt_tokens=jwt_tokens
        )
        logger.info(f"/api/auth/google/receiver: {user}")
        return response

        # except Exception as e:
        #     logger.error(f"/api/auth/google/receiver: {str(e)}")
        #     return Response(
        #         {"message": f"{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        #     )
