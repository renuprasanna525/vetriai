
from django.contrib import admin

from .models import ApprovalAction


@admin.register(ApprovalAction)
class ApprovalActionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "requester",
        "agent",
        "tool",
        "action",
        "status",
        "execution_status",
        "created_at",
    )
    list_filter = ("status", "execution_status", "agent", "created_at")
    search_fields = (
        "requester__username",
        "agent",
        "tool",
        "action",
    )
    readonly_fields = ("created_at", "updated_at")