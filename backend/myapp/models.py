from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):

    ROLE_CHOICES = [
        ("employee", "Employee"),
        ("sales", "Sales"),
        ("hr", "HR"),
        ("manager", "Manager"),
        ("admin", "Administrator"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="employee",
    )

    whatsapp_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Conversation(models.Model):
    """
    Stores one AI chat conversation belonging to one user.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="conversations",
    )

    title = models.CharField(
        max_length=255,
        default="New Conversation",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class ChatMessage(models.Model):
    """
    Stores individual user and AI messages
    inside a conversation.
    """

    SENDER_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    sender = models.CharField(
        max_length=20,
        choices=SENDER_CHOICES,
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return (
            f"{self.conversation.user.username} - "
            f"{self.sender} - "
            f"{self.created_at}"
        )
