from django.contrib.auth import authenticate, get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .serializers import LoginSerializer, RegisterSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # JWT 토큰 생성
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # 응답에 쿠키 추가
        response = Response(
            {
                "username": user.username,
                "email": user.email,
                "nickname": user.nickname,
                "access_token": access_token,
                "refresh_token": str(refresh),
                "created_at": user.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            status=status.HTTP_201_CREATED,
        )

        # 응답에 쿠키 추가 및 데이터 반환
        response = Response(response_data, status=status.HTTP_201_CREATED)

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # 배포 환경에서는 True로 설정
            samesite="Strict",
        )

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,  # 배포 환경에서는 True로 설정
            samesite="Strict",
        )

        return response


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )

        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # 응답 데이터 구성
            response_data = {
                "token": access_token,
                "user_id": str(user.id),
                "nickname": user.nickname,
            }

            # 응답에 쿠키 추가 및 데이터 반환
            response = Response(response_data, status=status.HTTP_200_OK)

            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=False,  # 배포 환경에서는 True로 설정
                samesite="Strict",
                domain="localhost",  # 로컬 개발 시 사용, 배포 시 도메인 변경 필요
                path="/",
            )

            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=False,  # 배포 환경에서는 True로 설정
                samesite="Strict",
                domain="localhost",  # 로컬 개발 시 사용, 배포 시 도메인 변경 필요
                path="/",
            )

            return response
        else:
            return Response(
                {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            response = Response(status=status.HTTP_200_OK)

            # 쿠키를 삭제하는 응답 헤더 설정
            response.set_cookie(
                key="access_token",
                value="deleted",
                httponly=True,
                secure=False,  # 배포 환경에서는 True로 설정
                samesite="Strict",
                domain="localhost",
                path="/",
                max_age=0,
            )

            response.set_cookie(
                key="refresh_token",
                value="deleted",
                httponly=True,
                secure=False,  # 배포 환경에서는 True로 설정
                samesite="Strict",
                domain="localhost",
                path="/",
                max_age=0,
            )

            return response

        except (TokenError, InvalidToken):
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class DeleteAccountView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            user.delete()

            response = Response(status=status.HTTP_204_NO_CONTENT)
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return response
        except User.DoesNotExist:
            return Response(
                {"status": "error", "detail": "User does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get("access_token")

        if not access_token:
            return Response(
                {"detail": "토큰을 제공받지 못함"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = AccessToken(access_token)
            token.verify()  # 토큰의 유효성 검증

            return Response(status=status.HTTP_200_OK)

        except (TokenError, InvalidToken):
            return Response(
                {"detail": "유효하지 않은 토큰"}, status=status.HTTP_401_UNAUTHORIZED
            )

        except Exception as e:
            return Response(
                {"detail": "서버 에러"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserTokenRefreshView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "토큰을 제공받지 못함"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 기존의 refresh token을 사용해 새로운 access token과 refresh token 생성
            token = RefreshToken(refresh_token)
            new_access_token = str(token.access_token)
            new_refresh_token = str(token)

            # 응답에 쿠키로 새로운 토큰 전송
            response = Response(status=status.HTTP_200_OK)
            response.set_cookie(
                key="access_token",
                value=new_access_token,
                httponly=True,
                secure=False,  # 배포 환경에서는 True로 설정
                samesite="Lax",
                path="/",
            )

            response.set_cookie(
                key="refresh_token",
                value=new_refresh_token,
                httponly=True,
                secure=False,  # 배포 환경에서는 True로 설정
                samesite="Lax",
                path="/",
            )

            return response

        except (TokenError, InvalidToken):
            return Response(
                {"detail": "유효하지 않은 토큰"}, status=status.HTTP_401_UNAUTHORIZED
            )
