from django.test import SimpleTestCase

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
