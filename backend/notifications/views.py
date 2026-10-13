from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer
from rest_framework.views import APIView
from rest_framework import status
from .utils import create_notification


class NotificationListView(generics.ListAPIView):
    """
    Returns notifications belonging to the logged-in user.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )


class NotificationDetailView(generics.RetrieveDestroyAPIView):
    """
    Returns a single notification belonging to the logged-in user.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationMarkReadView(generics.UpdateAPIView):
    """
    Marks a notification as read.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        notification = self.get_object()

        notification.is_read = True
        notification.save(update_fields=["is_read"])

        serializer = self.get_serializer(notification)

        return Response(serializer.data)


class WhatsAppTestNotificationView(APIView):
    """
    Creates a WhatsApp-channel test notification for the logged-in user.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = getattr(request.user, "profile", None)
        whatsapp_number = getattr(profile, "whatsapp_number", "")

        if not whatsapp_number:
            return Response(
                {
                    "detail": (
                        "Configure a WhatsApp number in your profile "
                        "before testing WhatsApp notifications."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        notification = create_notification(
            user=request.user,
            notification_type="whatsapp_test",
            title="WhatsApp Test Notification",
            message=(
                "Test notification from Vetri AI. "
                "WhatsApp notification workflow verification."
            ),
            priority="medium",
            channel="whatsapp",
        )

        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_201_CREATED,
        )
