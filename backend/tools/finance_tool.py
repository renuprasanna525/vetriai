from datetime import date


class FinanceTool:
    """
    Controlled tool for finance-related operations.

    Real finance/database integration can be added later.
    """

    name = "finance_tool"
    description = "Provides controlled finance information."

    def execute(self, action, user=None):

        if action == "get_finance_summary":

            return {
                "status": "success",
                "data": {
                    "total_revenue": 125000,
                    "total_expenses": 75000,
                    "net_profit": 50000,
                },
            }

        # -----------------------------------------
        # Payments Due Today
        # -----------------------------------------
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
