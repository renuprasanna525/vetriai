from django.test import SimpleTestCase
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from myapp.models import UserProfile
from agents.orchestrator import AIOrchestrator


class GreetingResponseTests(SimpleTestCase):
    """Regression tests for standalone greeting requests."""

    def setUp(self):
        # Bypass agent initialization because greetings return early.
        self.orchestrator = AIOrchestrator.__new__(AIOrchestrator)

    def test_standalone_greetings_return_friendly_response(self):
        greetings = [
            "hi",
            "hello",
            "hey",
            "hi there",
            "hello there",
            "hey there",
            "good morning",
            "good afternoon",
            "good evening",
        ]

        for greeting in greetings:
            with self.subTest(greeting=greeting):
                result = self.orchestrator.process_request(
                    greeting,
                    user=None,
                    role=None,
                )

                self.assertEqual(result["status"], "success")
                self.assertEqual(result["intent"], "greeting")
                self.assertEqual(result["agent"], "Vetri AI")
                self.assertIn(
                    "How can I help you today?",
                    result["response"],
                )
                self.assertFalse(
                    result["data"]["conversation_context_used"]
                )

    def test_greeting_is_case_insensitive_and_accepts_punctuation(self):
        greetings = ["HELLO", "Hi!", "Hello.", "HEY?", "Good morning!"]

        for greeting in greetings:
            with self.subTest(greeting=greeting):
                result = self.orchestrator.process_request(
                    greeting,
                    user=None,
                    role=None,
                )

                self.assertEqual(result["intent"], "greeting")
                self.assertEqual(result["status"], "success")

    def test_greeting_reports_when_conversation_context_exists(self):
        result = self.orchestrator.process_request(
            "Hello",
            user=None,
            role=None,
            conversation_history=[{"role": "user", "content": "Hi"}],
        )

        self.assertEqual(result["intent"], "greeting")
        self.assertTrue(result["data"]["conversation_context_used"])

    def test_greeting_without_context_reports_no_context(self):
        result = self.orchestrator.process_request(
            "Hello",
            user=None,
            role=None,
            conversation_history=None,
        )

        self.assertFalse(result["data"]["conversation_context_used"])

class EmailApprovalRoutingTests(TestCase):
    """Regression tests for explicit email requests."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="email_sales_test",
            password="test-password-123",
        )

        UserProfile.objects.update_or_create(
            user=self.user,
            defaults={"role": "sales"},
        )

        self.orchestrator = AIOrchestrator()

        self.orchestrator.registry.get_agents = Mock(
            return_value=[
                SimpleNamespace(name="Sales Agent"),
            ]
        )

    @patch("agents.orchestrator.ToolRegistry")
    @patch("agents.orchestrator.create_audit_log")
    def test_sales_email_request_creates_pending_approval(
        self,
        mock_audit_log,
        mock_tool_registry_class,
    ):
        mock_tool_registry = mock_tool_registry_class.return_value
        mock_tool_registry.request_action.return_value = {
            "status": "pending",
            "action_id": 123,
            "message": "Approval created",
        }

        with patch.object(
            self.orchestrator,
            "check_agent_permission",
            return_value=True,
        ) as mock_permission:
            result = self.orchestrator.process_request(
                request=(
                    'Send an email to test@example.com '
                    'subject: "Test subject" '
                    'message: "Test body"'
                ),
                user=self.user,
                role="sales",
                conversation_history=[],
            )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["intent"], "Email Approval")
        self.assertIn("not been sent", result["response"].lower())

        mock_permission.assert_called_once()

        permission_kwargs = mock_permission.call_args.kwargs
        self.assertEqual(
            permission_kwargs["agent_name"],
            "Sales Agent",
        )

        mock_tool_registry.request_action.assert_called_once_with(
            agent_name="Sales Agent",
            tool_name="email_tool",
            action="send_email",
            parameters={
                "recipient": "test@example.com",
                "subject": "Test subject",
                "message": "Test body",
            },
            user=self.user,
        )
