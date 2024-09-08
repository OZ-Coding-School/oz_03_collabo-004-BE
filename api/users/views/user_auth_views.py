import os

from common.logger import logger
from django.contrib.auth import authenticate, get_user_model, update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from users.serializers import (
    EmptySerializer,
    FindUsernameSerializer,
    UserLoginSerializer,
    UserLogoutSerializer,
    UserRegisterSerializer,
    UserTokenRefreshSerializer,
)
from users.utils import GeneralAuthClass, HunsooKingAuthClass

User = get_user_model()


class UserRegisterView(generics.CreateAPIView):
    logger.info("User registration attempt")
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        logger.info("User registration attempt")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 이메일 인증을 위한 토큰 생성 및 인증 URL 생성
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_url = reverse(
            "verify_email", kwargs={"uidb64": uid, "token": token}
        )
        full_url = f"{request.scheme}://{request.get_host()}{verification_url}"

        # 이메일 발송
        send_mail(
            "이메일 인증 요청",
            f"이메일을 인증하려면 다음 링크를 클릭하세요: {full_url}",
            "no-reply@example.com",
            [user.email],
        )

        response = Response(
            {
                "username": user.username,
                "email": user.email,
                "nickname": user.nickname,
                "message": "회원가입이 완료되었습니다. 이메일 인증을 진행해주세요.",
                "created_at": user.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            status=status.HTTP_201_CREATED,
        )

        logger.info(f"User {user.email} registered successfully")
        return response


class UserLoginView(APIView):
    authentication_classes = []  # 일반 로그인에서는 별도의 인증 클래스 사용 안 함
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info("User login attempt")
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )

        if user is not None:

            # 이메일 인증 확인
            if not user.is_email_verified:
                logger.error(
                    f"User {user.email} attempted login without email verification"
                )
                return Response(
                    {"detail": "이메일을 인증해야 합니다."},
                    status=status.HTTP_409_CONFLICT,
                )

            user.last_login = timezone.now()
            user.save()

            jwt_tokens = GeneralAuthClass.set_auth_tokens_for_user(user)

            response_data = {
                "token": jwt_tokens["access"],
                "user_id": str(user.id),
                "nickname": user.nickname,
            }

            response = Response(response_data, status=status.HTTP_200_OK)
            response = GeneralAuthClass().set_jwt_auth_cookie(response, jwt_tokens)

            logger.info(f"User {user.email} logged in successfully")
            return response
        else:
            logger.error("Invalid credentials provided for login")
            return Response(
                {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


class UserTokenVerifyView(generics.GenericAPIView):
    serializer_class = EmptySerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info("POST /api/auth/token/verify")
        token = request.COOKIES.get("access")
        if not token:
            logger.error("/api/auth/token/verify: Access token not found in cookies")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            AccessToken(token)
            logger.info("/api/auth/token/verify: Access token is valid")
            return Response(status=status.HTTP_200_OK)
        except (InvalidToken, TokenError):
            logger.error("/api/auth/token/verify: Invalid access token")
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class UserTokenRefreshView(generics.GenericAPIView):
    serializer_class = UserTokenRefreshSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info("POST /api/auth/token/refresh")
        refresh_token = request.COOKIES.get("refresh")

        if not refresh_token:
            logger.error("/api/auth/token/refresh: Refresh token not found in cookies")
            return Response(
                {"detail": "Refresh token not found in cookies"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data={"refresh_token": refresh_token})
        serializer.is_valid(raise_exception=True)

        try:
            access_token = HunsooKingAuthClass.new_access_token_for_user(
                refresh_token=serializer.validated_data["refresh_token"]
            )
        except (InvalidToken, TokenError) as e:
            logger.error(f"/api/auth/token/refresh: {e}")
            return Response(
                data={"error occurs": "UserTokenRefreshView", "detail": str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = Response(
            data={"access": access_token, "message": "Token refreshed successfully"}
        )
        try:
            HunsooKingAuthClass.set_cookie_attributes(
                response=response, key="access", token=access_token
            )
        except ValueError:
            logger.error("/api/auth/token/refresh: Failed to set access token cookie")
            return Response(
                {"error occurs": "UserTokenRefreshView"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        logger.info("/api/auth/token/refresh: Token refreshed successfully")
        return response


class UserLogoutView(generics.GenericAPIView):
    serializer_class = UserLogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data={"refresh_token": request.COOKIES.get("refresh")}
        )
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = serializer.validated_data["refresh_token"]
            with transaction.atomic():
                refresh_token.blacklist()
            response = Response(status=status.HTTP_200_OK)
            response.delete_cookie(
                "access", domain=os.getenv("COOKIE_DOMAIN"), path="/"
            )
            response.delete_cookie(
                "refresh", domain=os.getenv("COOKIE_DOMAIN"), path="/"
            )
            logger.info("/api/auth/logout: Logout successful")
            return response
        except (InvalidToken, TokenError) as e:
            logger.error(f"/api/auth/logout: {e}")
            return Response(
                data={"message": "Invalid refresh token", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"/api/auth/logout: {str(e)}")
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# 유저 회원 탈퇴 뷰
class UserDeleteView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        logger.info(f"DELETE /api/auth/delete for user: {request.user.email}")

        # refresh_token을 쿠키에서 가져옴
        refresh_token = request.COOKIES.get("refresh")
        if not refresh_token:
            logger.error("Refresh token not found in cookies")
            return Response(
                {"detail": "Refresh token not found in cookies"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # 현재 로그인된 유저 정보 사용
            user = request.user
            with transaction.atomic():
                user.delete()
                # refresh_token 블랙리스트 처리
                RefreshToken(refresh_token).blacklist()

            # 쿠키에서 JWT 삭제
            response = Response(status=status.HTTP_204_NO_CONTENT)
            response.delete_cookie(
                "access", domain=os.getenv("COOKIE_DOMAIN"), path="/"
            )
            response.delete_cookie(
                "refresh", domain=os.getenv("COOKIE_DOMAIN"), path="/"
            )

            logger.info(f"User {user.email} deleted successfully")
            return response

        except (InvalidToken, TokenError) as e:
            logger.error(f"Invalid refresh token: {e}")
            return Response(
                {"detail": "Invalid refresh token", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.error(f"Error during user deletion: {str(e)}")
            return Response(
                {"detail": "An error occurred", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# 특정유저의 관리자와 일반유저 판단
class UserStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        status = 1 if user.is_superuser or user.is_staff else 0
        return Response({"status": status})


# 로그인 상태 확인
class LoginStatusView(GenericAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        is_authenticated = request.user.is_authenticated
        return Response({"login": is_authenticated})


# 이메일 인증 처리 view
def verify_email(request, uidb64, token):
    User = get_user_model()
    uid = urlsafe_base64_decode(uidb64).decode()
    user = get_object_or_404(User, pk=uid)

    if default_token_generator.check_token(user, token):
        user.is_email_verified = True
        user.save()
        return redirect("verification_success")
    else:
        return redirect("verification_failed")


# 이메일 인증 성공
def verification_success(request):
    return HttpResponse("이메일 인증에 성공했습니다. 로그인 후 이용해주세요.")


# 이메일 인증 실패
def verification_failed(request):
    return HttpResponse("이메일 인증에 실패했습니다. 다시 시도해 주세요.")


# 인증 이메일 발송
class SendVerificationEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"detail": "해당 사용자 이름으로 가입된 사용자가 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 이메일 인증 토큰 생성
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_url = reverse(
            "verify_email", kwargs={"uidb64": uid, "token": token}
        )
        full_url = f"{request.scheme}://{request.get_host()}{verification_url}"

        # 이메일 발송
        send_mail(
            "이메일 인증",
            f"이메일을 인증하려면 다음 링크를 클릭하세요: {full_url}",
            "no-reply@example.com",
            [user.email],
        )
        return Response(
            {f"detail : {user.email}로 비밀번호 재설정 메일이 발송되었습니다."},
            status=status.HTTP_200_OK,
        )


# 비밀번호 재설정 이메일 발송
class SendPasswordResetEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"detail": "해당 사용자 이름으로 가입된 사용자가 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 비밀번호 재설정 토큰 생성
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"https://hunsuking.yoyobar.xyz/password-reset/{uid}/{token}/"

        # 이메일 발송
        send_mail(
            "비밀번호 재설정 요청",
            f"비밀번호를 재설정하려면 다음 링크를 클릭하세요: {reset_url}",
            "no-reply@example.com",
            [user.email],
        )
        return Response(
            {f"detail : {user.email}로 비밀번호 재설정 메일이 발송되었습니다."},
            status=status.HTTP_200_OK,
        )


# 비밀번호 재설정
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        uidb64 = request.data.get("uidb64")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        if not all([uidb64, token, new_password]):
            return Response(
                {"detail": "모든 필드를 제공해야 합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"detail": "유효하지 않은 사용자입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if default_token_generator.check_token(user, token):
            user.set_password(new_password)  # 비밀번호 해시화 및 저장
            user.save()
            update_session_auth_hash(request, user)  # 로그인 유지
            return Response(
                {"detail": "비밀번호가 성공적으로 변경되었습니다."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"detail": "유효하지 않은 토큰입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )


# 아이디 찾기 이메일 확인뷰
class FindUsernameView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = FindUsernameSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]

        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            return Response(
                {"error": "해당 이메일로 가입된 사용자가 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        masked_username = user.username[:-3] + "***"
        return Response({"masked_username": masked_username}, status=status.HTTP_200_OK)
