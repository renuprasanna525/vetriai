from django.test import SimpleTestCase
from unittest.mock import Mock, patch

from agents.finance_agent import FinanceAgent


class FinanceAgentFinTrackRoutingTests(SimpleTestCase):
    def setUp(self):
        self.agent = FinanceAgent()

    def test_fintrack_summary_uses_fintrack_summary_action(self):
        with patch.object(
            self.agent.finance_tool,
            "execute",
            return_value={
                "status": "success",
                "data": {
                    "currency": "INR",
                    "total_income": "50000.00",
                    "total_expenses": "20000.00",
                    "net_balance": "30000.00",
                    "scope": "all_time",
                },
            },
        ) as mock_execute:
            result = self.agent.process("Show my FinTrack summary", user=None)

        mock_execute.assert_called_once_with("get_fintrack_summary", None)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["source"], "FinTrack")
        self.assertIn("Total Income", result["message"])

    def test_fintrack_categories_use_the_expected_actions(self):
        cases = [
            ("Show my transactions", "get_fintrack_transactions"),
            ("Show my bills", "get_fintrack_bills"),
            ("Show my budgets", "get_fintrack_budgets"),
            ("Show my accounts", "get_fintrack_accounts"),
            ("Show my spending breakdown", "get_fintrack_reports"),
        ]

        for request, expected_action in cases:
            with self.subTest(request=request):
                with patch.object(
                    self.agent.finance_tool,
                    "execute",
                    return_value={
                        "status": "success",
                        "data": {},
                    },
                ) as mock_execute:
                    result = self.agent.process(request, user=None)

                self.assertEqual(
                    mock_execute.call_args.args,
                    (expected_action, None),
                )
                self.assertEqual(result["source"], "FinTrack")

    def test_fintrack_api_failure_is_not_reported_as_success(self):
        with patch.object(
            self.agent.finance_tool,
            "execute",
            return_value={
                "status": "error",
                "message": "FinTrack API authentication is not configured.",
            },
        ):
            result = self.agent.process("Show my FinTrack summary", user=None)

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["source"], "FinTrack")
        self.assertIn("authentication", result["message"].lower())
