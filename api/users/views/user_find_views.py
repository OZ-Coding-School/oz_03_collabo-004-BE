from smtplib import SMTPException

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import BadHeaderError, send_mail
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.http import force_bytes, urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import (
    FindUsernameSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
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


# 비밀번호 재설정 요청뷰 (이메일 발송)
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data["username"]

        try:
            user = get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            return Response(
                {"error": "해당 아이디로 가입된 사용자가 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 이메일로 비밀번호 재설정 링크 전송
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        password_reset_url = reverse(
            "password_reset_confirm", kwargs={"uidb64": uid, "token": token}
        )
        full_url = f"{request.scheme}://{request.get_host()}{password_reset_url}"

        try:
            send_mail(
                "비밀번호 재설정",
                f"비밀번호를 재설정하려면 다음 링크를 클릭하세요: {full_url}",
                "no-reply@example.com",
                [user.email],
            )
        except BadHeaderError:
            return Response(
                {"error": "잘못된 헤더가 감지되었습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except SMTPException as e:
            return Response(
                {"error": f"이메일 전송에 실패했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"message": "비밀번호 재설정 링크가 이메일로 전송되었습니다."},
            status=status.HTTP_200_OK,
        )


# 비밀번호 재설정 확인 뷰
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(get_user_model(), pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            return Response(
                {"error": "잘못된 링크입니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        if default_token_generator.check_token(user, token):
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response(
                {"message": "비밀번호가 성공적으로 변경되었습니다."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "토큰이 유효하지 않습니다."}, status=status.HTTP_403_FORBIDDEN
            )
