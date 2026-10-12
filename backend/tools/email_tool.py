import os

import resend


class EmailTool:
    """
    Controlled tool for email-related operations.

    Sends email through Resend's HTTPS API only when the action
    reaches the tool execution stage. Approval is handled separately
    by ApprovalWorkflow.
    """

    name = "email_tool"
    description = "Handles approved email operations."

    def execute(
        self,
        action,
        user=None,
        recipient=None,
        subject=None,
        message=None,
        to=None,
    ):
        recipient = recipient or to

        if action != "send_email":
            return {
                "status": "error",
                "message": "Email action not supported.",
            }

        if not recipient:
            return {
                "status": "error",
                "message": "Recipient is required.",
            }

        if not subject:
            return {
                "status": "error",
                "message": "Subject is required.",
            }

        if not message:
            return {
                "status": "error",
                "message": "Message is required.",
            }

        api_key = os.getenv("RESEND_API_KEY")
        from_email = os.getenv("RESEND_FROM_EMAIL")

        if not api_key or not from_email:
            return {
                "status": "error",
                "message": (
                    "Email service is not configured. "
                    "Set RESEND_API_KEY and RESEND_FROM_EMAIL."
                ),
            }

        try:
            resend.api_key = api_key

            response = resend.Emails.send(
                {
                    "from": from_email,
                    "to": [recipient],
                    "subject": subject,
                    "text": message,
                }
            )

            email_id = (
                response.get("id")
                if isinstance(response, dict)
                else getattr(response, "id", None)
            )

            if email_id:
                return {
                    "status": "success",
                    "message": f"Email accepted by Resend for {recipient}.",
                    "recipient": recipient,
                    "subject": subject,
                    "email_id": email_id,
                }

            return {
                "status": "error",
                "message": "Resend did not return an email ID.",
            }

        except Exception:
            return {
                "status": "error",
                "message": (
                    "Email sending failed through Resend. "
                    "Check the service configuration and provider logs."
                ),
            }
