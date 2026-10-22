from datetime import date
import os

import requests


class FinanceTool:
    """
    Controlled tool for finance-related operations.
    """

    name = "finance_tool"
    description = "Provides controlled finance information."

    def execute(self, action, user=None):

        if action == "get_finance_summary":
            # Preserve Vetri's existing company-finance summary.
            return {
                "status": "success",
                "data": {
                    "total_revenue": 125000,
                    "total_expenses": 75000,
                    "net_profit": 50000,
                },
            }

        if action == "get_fintrack_summary":
            api_url = os.getenv(
                "FINTRACK_API_URL",
                "https://finance-xnjh.onrender.com/api/finance/summary/",
            ).strip()
            api_key = os.getenv("FINTRACK_API_KEY", "").strip()

            if not api_key:
                return {
                    "status": "error",
                    "message": "FinTrack API authentication is not configured.",
                }

            try:
                response = requests.get(
                    api_url,
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=15,
                )
                response.raise_for_status()
                result = response.json()

                required_fields = (
                    "currency",
                    "total_income",
                    "total_expenses",
                    "net_balance",
                )
                if not all(field in result for field in required_fields):
                    return {
                        "status": "error",
                        "message": "FinTrack returned an incomplete finance summary.",
                    }

                return {
                    "status": "success",
                    "source": "FinTrack",
                    "data": {
                        "currency": result["currency"],
                        "total_income": result["total_income"],
                        "total_expenses": result["total_expenses"],
                        "net_balance": result["net_balance"],
                        "scope": result.get("scope", "all_time"),
                    },
                }

            except requests.RequestException:
                return {
                    "status": "error",
                    "message": "Unable to retrieve finance data from FinTrack.",
                }
            except (ValueError, TypeError):
                return {
                    "status": "error",
                    "message": "FinTrack returned an invalid finance response.",
                }

        # Payments Due Today
        if action == "get_payments_due_today":
            today = date.today()

            payments = [
                {
                    "payment_id": "PAY-1001",
                    "customer": "ABC Technologies",
                    "amount": 25000,
                    "due_date": "2026-10-05",
                    "status": "Due",
                },
                {
                    "payment_id": "PAY-1002",
                    "customer": "XYZ Solutions",
                    "amount": 18000,
                    "due_date": "2026-10-07",
                    "status": "Due",
                },
                {
                    "payment_id": "PAY-1003",
                    "customer": "Global Systems",
                    "amount": 32000,
                    "due_date": "2026-09-30",
                    "status": "Overdue",
                },
            ]

            payments_due_today = []

            for payment in payments:
                if payment["status"].lower() != "due":
                    continue

                due_date = date.fromisoformat(payment["due_date"])

                if due_date == today:
                    payments_due_today.append(payment)

            return {
                "status": "success",
                "data": {
                    "payments_due_today": payments_due_today,
                    "total_due_today": len(payments_due_today),
                },
            }

        return {
            "status": "error",
            "message": "Finance action not supported.",
        }
