from .base_agent import BaseAgent
from tools.finance_tool import FinanceTool


class FinanceAgent(BaseAgent):

    name = "Finance Agent"

    description = "Handles finance, financial summary, and payment questions"

    def __init__(self):
        self.finance_tool = FinanceTool()

    def can_handle(self, request):

        finance_keywords = [
            "finance",
            "financial",
            "revenue",
            "expense",
            "expenses",
            "profit",
            "financial summary",
            "payment",
            "payments",
            "payment due",
            "payments due",
            "due today",
        ]

        request_lower = request.lower()

        return any(keyword in request_lower for keyword in finance_keywords)

    def get_required_permission(self, request):

        return "view_finance"

    def process(self, request, user, credentials=None):

        request_lower = request.lower()

        # -----------------------------------------
        # Payments Due Today
        # -----------------------------------------
        if "payment" in request_lower and (
            "due" in request_lower or "today" in request_lower
        ):

            result = self.finance_tool.execute(
                "get_payments_due_today",
                user,
            )

            if result.get("status") == "success":

                data = result.get("data", {})

                payments = data.get("payments_due_today", [])
                total_due_today = data.get("total_due_today", 0)

                if payments:

                    payment_lines = []

                    for payment in payments:
                        payment_lines.append(
                            f"- {payment.get('customer', 'Unknown customer')}: "
                            f"{payment.get('amount', 0)} "
                            f"(Due: {payment.get('due_date', 'Unknown date')})"
                        )

                    message = f"Payments Due Today: {total_due_today}\n" + "\n".join(
                        payment_lines
                    )

                else:

                    message = "There are no payments due today."

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": data,
                    "message": message,
                }

        # -----------------------------------------
        # Finance Summary
        # -----------------------------------------
        if (
            "finance" in request_lower
            or "financial" in request_lower
            or "revenue" in request_lower
            or "expense" in request_lower
            or "expenses" in request_lower
            or "profit" in request_lower
            or "summary" in request_lower
        ):

            result = self.finance_tool.execute(
                "get_finance_summary",
                user,
            )

            if result.get("status") == "success":

                data = result.get("data", {})

                message = (
                    "Finance Summary:\n"
                    f"Total Revenue: {data.get('total_revenue', 0)}\n"
                    f"Total Expenses: {data.get('total_expenses', 0)}\n"
                    f"Net Profit: {data.get('net_profit', 0)}"
                )

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": data,
                    "message": message,
                }

        return {
            "agent": self.name,
            "status": "unsupported",
            "data": {},
            "message": "The requested finance information is not currently supported.",
        }
