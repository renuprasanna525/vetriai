import os
from unittest.mock import patch

from django.test import SimpleTestCase

from tools.email_tool import EmailTool


class EmailToolTests(SimpleTestCase):
    @patch("tools.email_tool.resend.Emails.send")
    def test_send_email_accepts_recipient_parameter(self, mock_send):
        mock_send.return_value = {"id": "email_test_123"}

        with patch.dict(
            os.environ,
            {
                "RESEND_API_KEY": "test_api_key",
                "RESEND_FROM_EMAIL": "onboarding@resend.dev",
            },
        ):
            result = EmailTool().execute(
                action="send_email",
                recipient="recipient@example.com",
                subject="Test subject",
                message="Test message",
            )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["recipient"], "recipient@example.com")
        mock_send.assert_called_once_with(
            {
                "from": "onboarding@resend.dev",
                "to": ["recipient@example.com"],
                "subject": "Test subject",
                "text": "Test message",
            }
        )

    @patch("tools.email_tool.resend.Emails.send")
    def test_send_email_accepts_to_parameter(self, mock_send):
        mock_send.return_value = {"id": "email_test_456"}

        with patch.dict(
            os.environ,
            {
                "RESEND_API_KEY": "test_api_key",
                "RESEND_FROM_EMAIL": "onboarding@resend.dev",
            },
        ):
            result = EmailTool().execute(
                action="send_email",
                to="edited@example.com",
                subject="Edited subject",
                message="Edited message",
            )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["recipient"], "edited@example.com")
        mock_send.assert_called_once_with(
            {
                "from": "onboarding@resend.dev",
                "to": ["edited@example.com"],
                "subject": "Edited subject",
                "text": "Edited message",
            }
        )
