from datetime import date
import os

import requests


class FinanceTool:
    """
    Controlled tool for company finance and FinTrack information.
    """

    name = "finance_tool"
    description = "Provides controlled finance information."

    FINTRACK_ACTIONS = {
        "get_fintrack_transactions": "transactions/",
        "get_fintrack_bills": "bills/",
        "get_fintrack_budgets": "budgets/",
        "get_fintrack_accounts": "accounts/",
        "get_fintrack_reports": "reports/",
    }

    def execute(self, action, user=None):

        # Preserve Vetri's existing company finance summary.
        if action == "get_finance_summary":
            return {
                "status": "success",
                "data": {
                    "total_revenue": 125000,
                    "total_expenses": 75000,
                    "net_profit": 50000,
                },
            }

        # FinTrack summary.
        if action == "get_fintrack_summary":
            result = self._get_fintrack_endpoint("summary/")

            if result.get("status") != "success":
                return result

            data = result["data"]
            required_fields = (
                "currency",
                "total_income",
                "total_expenses",
                "net_balance",
            )

            if not all(field in data for field in required_fields):
                return {
                    "status": "error",
                    "message": "FinTrack returned an incomplete finance summary.",
                }

            return {
                "status": "success",
                "source": "FinTrack",
                "data": {
                    "currency": data["currency"],
                    "total_income": data["total_income"],
                    "total_expenses": data["total_expenses"],
                    "net_balance": data["net_balance"],
                    "scope": data.get("scope", "all_time"),
                },
            }

        # FinTrack transactions, bills, budgets, accounts and reports.
        if action in self.FINTRACK_ACTIONS:
            endpoint = self.FINTRACK_ACTIONS[action]
            return self._get_fintrack_endpoint(endpoint)

        # Existing company payments-due-today logic.
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

    def _get_fintrack_endpoint(self, endpoint):
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

        # FINTRACK_API_URL currently points to the summary endpoint.
        if endpoint == "summary/":
            url = api_url
        else:
            base_url = api_url.rsplit("summary/", 1)[0]

            if base_url == api_url:
                return {
                    "status": "error",
                    "message": "FinTrack API URL must point to the summary endpoint.",
                }

            url = f"{base_url}{endpoint}"

        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=15,
            )
            response.raise_for_status()
            result = response.json()

            if not isinstance(result, dict):
                return {
                    "status": "error",
                    "message": "FinTrack returned an invalid response format.",
                }

            return {
                "status": "success",
                "source": "FinTrack",
                "data": result,
            }

        except requests.Timeout:
            print(f"FinTrack timeout: endpoint={endpoint}, timeout=15s")
            return {
                "status": "error",
                "message": "Unable to retrieve finance data from FinTrack.",
            }

        except requests.HTTPError as exc:
            status_code = (
                exc.response.status_code
                if exc.response is not None
                else "unknown"
            )
            print(
                f"FinTrack HTTP error: endpoint={endpoint}, "
                f"status={status_code}"
            )
            return {
                "status": "error",
                "message": "Unable to retrieve finance data from FinTrack.",
            }

        except requests.ConnectionError:
            print(f"FinTrack connection error: endpoint={endpoint}")
            return {
                "status": "error",
                "message": "Unable to retrieve finance data from FinTrack.",
            }

        except requests.RequestException as exc:
            print(
                f"FinTrack request error: endpoint={endpoint}, "
                f"type={type(exc).__name__}"
            )
            return {
                "status": "error",
                "message": "Unable to retrieve finance data from FinTrack.",
            }

        except (ValueError, TypeError):
            print(f"FinTrack response parsing error: endpoint={endpoint}")
            return {
                "status": "error",
                "message": "FinTrack returned an invalid response.",
            }