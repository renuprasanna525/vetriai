from .models import Notification
from tools.email_tool import EmailTool
from tools.whatsapp_service import WhatsAppService


def _deliver_email_notification(notification):
    """
    Deliver a notification through the existing EmailTool.

    Email delivery is attempted only when the notification
    channel is explicitly set to "email".
    """

    recipient = notification.user.email

    if not recipient:
        return {
            "status": "error",
            "message": "User does not have an email address.",
        }

    email_tool = EmailTool()

    return email_tool.execute(
        action="send_email",
        user=notification.user,
        recipient=recipient,
        subject=notification.title,
        message=notification.message,
    )


def _deliver_whatsapp_notification(notification):
    """
    Deliver a notification through WhatsApp.

    WhatsApp delivery is handled by WhatsAppService.
    When Meta WhatsApp Cloud API credentials are unavailable,
    WhatsAppService uses simulated/mock delivery so the
    notification workflow can still be tested.
    """

    recipient = getattr(
        getattr(notification.user, "profile", None),
        "whatsapp_number",
        None,
    )
    if not recipient:
        return {
            "status": "error",
            "message": "User does not have a WhatsApp phone number.",
        }

    whatsapp_service = WhatsAppService()

    return whatsapp_service.send_message(
        recipient=recipient,
        message=notification.message,
    )


def create_notification(
    user,
    notification_type,
    title,
    message,
    priority="medium",
    channel="in_app",
    related_id=None,
):
    """
    Create a notification for a user.

    Supported channels:
    - in_app: Store the notification only.
    - email: Store the notification and send an email.
    - whatsapp: Store the notification and attempt WhatsApp delivery.

    WhatsApp delivery uses the Meta WhatsApp Cloud API when
    configured. Otherwise, simulated/mock delivery is used.
    """

    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        priority=priority,
        channel=channel,
        related_id=related_id,
    )

    if channel == "email":
        _deliver_email_notification(notification)

    if channel == "whatsapp":
        _deliver_whatsapp_notification(notification)

    return notification


def create_project_risk_notification(
    user,
    message,
    related_id=None,
):
    """
    Create a notification for a critical project risk.
    """

    return create_notification(
        user=user,
        notification_type="critical_project_risk",
        title="Critical Project Risk",
        message=message,
        priority="critical",
        channel="in_app",
        related_id=related_id,
    )


def create_high_priority_lead_notification(
    user,
    message,
    related_id=None,
):
    """
    Create a notification for a high-priority lead.
    """

    return create_notification(
        user=user,
        notification_type="high_priority_lead",
        title="High-Priority Lead",
        message=message,
        priority="high",
        channel="in_app",
        related_id=related_id,
    )


def create_overdue_payment_notification(
    user,
    message,
    related_id=None,
):
    """
    Create a notification for an overdue payment.
    """

    return create_notification(
        user=user,
        notification_type="overdue_payment",
        title="Overdue Payment",
        message=message,
        priority="high",
        channel="in_app",
        related_id=related_id,
    )


def create_customer_issue_notification(
    user,
    message,
    related_id=None,
):
    """
    Create a notification for an important customer issue.
    """

    return create_notification(
        user=user,
        notification_type="important_customer_issue",
        title="Important Customer Issue",
        message=message,
        priority="high",
        channel="in_app",
        related_id=related_id,
    )


def create_approval_pending_notification(
    user,
    message,
    related_id=None,
    channel="in_app",
):
    """
    Create a notification for a pending approval.

    Supported channels:
    - in_app
    - email
    - whatsapp

    WhatsApp delivery uses real Meta delivery when configured,
    otherwise simulated/mock delivery is used.
    """

    return create_notification(
        user=user,
        notification_type="approval_pending",
        title="Approval Required",
        message=message,
        priority="high",
        channel=channel,
        related_id=related_id,
    )


def create_deadline_notification(
    user,
    message,
    related_id=None,
):
    """
    Create a notification for an approaching deadline.
    """

    return create_notification(
        user=user,
        notification_type="deadline_approaching",
        title="Deadline Approaching",
        message=message,
        priority="high",
        channel="in_app",
        related_id=related_id,
    )


def create_approval_executed_notification(
    user,
    message,
    related_id=None,
):
    """
    Create a notification after an approved action is executed.
    """

    return create_notification(
        user=user,
        notification_type="approval_executed",
        title="Action Approved & Executed",
        message=message,
        priority="high",
        channel="in_app",
        related_id=related_id,
    )
