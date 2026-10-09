from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import AuditLog
from .serializers import AuditLogSerializer
from permissions.permission_engine import PermissionEngine


class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.all().order_by("-timestamp")
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        role = getattr(
            getattr(user, "profile", None),
            "role",
            None,
        )

        permission_engine = PermissionEngine()

        if not permission_engine.has_permission(
            role,
            "view_audit_logs",
        ):
            raise PermissionDenied("You do not have permission to view audit logs.")

        return AuditLog.objects.all().order_by("-timestamp")
