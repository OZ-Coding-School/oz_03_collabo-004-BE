from notifications.models import Notification
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .serializers import AdminNotificationSerializer, NotificationSerializer


# 특정 사용자가 받은 모든 알림을 조회
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by(
            "-timestamp"
        )


# 특정 알림의 세부정보를 조회
class NotificationDetailView(generics.RetrieveAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(recipient=self.request.user)


# 특정 알림을 읽음 상태로 변경
class NotificationMarkAsReadView(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response(
            {"status": "알림이 읽음 상태로 변경되었습니다."}, status=status.HTTP_200_OK
        )


# 특정알림 삭제
class NotificationDeleteView(generics.DestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(recipient=self.request.user)


# 어드민 유저가 받은 모든 알림을 조회
class AdminNotificationListView(generics.ListAPIView):
    serializer_class = AdminNotificationSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Notification.objects.filter(is_admin=True).order_by("-timestamp")


# 어드민 특정 알림의 세부정보를 조회
class AdminNotificationDetailView(generics.RetrieveAPIView):
    queryset = Notification.objects.all()
    serializer_class = AdminNotificationSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return super().get_queryset().filter(is_admin=True)


# 어드민 특정 알림을 읽음 상태로 변경
class AdminNotificationMarkAsReadView(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = AdminNotificationSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response(
            {"status": "알림이 읽음 상태로 변경되었습니다."}, status=status.HTTP_200_OK
        )


# 어드민 특정알림 삭제
class AdminNotificationDeleteView(generics.DestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = AdminNotificationSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return super().get_queryset().filter(is_admin=True)
