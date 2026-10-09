from django.conf import settings
from django.db import models


class ApprovalAction(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("cancelled", "Cancelled"),
    ]

    EXECUTION_STATUS_CHOICES = [
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approval_actions",
    )
    agent = models.CharField(max_length=255)
    tool = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    parameters = models.JSONField(default=dict)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
    )
    execution_status = models.CharField(
        max_length=20,
        choices=EXECUTION_STATUS_CHOICES,
        blank=True,
        null=True,
    )
    execution_result = models.JSONField(
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Approval #{self.pk} - {self.action} ({self.status})"
