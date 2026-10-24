from .base_agent import BaseAgent
from tools.finance_tool import FinanceTool


class FinanceAgent(BaseAgent):

    name = "Finance Agent"
    description = (
        "Handles company finance, FinTrack personal finance, "
        "transactions, bills, budgets, accounts, reports, and payments."
    )

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
            "summary",
            "payment",
            "payments",
            "due today",
            "fintrack",
            "transaction",
            "transactions",
            "spend",
            "spent",
            "spending",
            "bill",
            "bills",
            "overdue",
            "budget",
            "budgets",
            "account balance",
            "accounts",
            "bank account",
            "top spending",
            "spending breakdown",
            "my income",
            "remaining balance",
            "left in my account",
        ]

        request_lower = request.lower()
        return any(keyword in request_lower for keyword in finance_keywords)

    def get_required_permission(self, request):
        return "view_finance"

    def _get_fintrack_response(self, action, user, title):
        result = self.finance_tool.execute(action, user)

        if result.get("status") != "success":
            return {
                "agent": self.name,
                "status": result.get("status", "error"),
                "source": "FinTrack",
                "data": {},
                "message": result.get(
                    "message",
                    "Unable to retrieve information from FinTrack.",
                ),
            }

        data = result.get("data", {})
        lines = [title]
        if action == "get_fintrack_budgets":
            lines.append(
                "Currency: INR (Indian Rupees, ₹). "
                "All budget amounts (spent, limit, and remaining) "
                "are in INR. Always display these amounts using ₹, "
                "never $ or USD."
            )

        list_labels = {
            "transactions": (
                "Transactions",
                [
                    "title",
                    "category",
                    "transaction_type",
                    "amount",
                    "transaction_date",
                    "payment_method",
                ],
            ),
            "bills": (
                "Bills",
                ["title", "amount", "due_date", "status", "category"],
            ),
            "budgets": (
                "Budgets",
                ["name", "spent", "limit", "remaining", "used_percentage", "status"],
            ),
            "accounts": (
                "Accounts",
                [
                    "bank_name",
                    "account_type",
                    "account_category",
                    "account_id",
                    "balance",
                ],
            ),
        }

        found_list = False

        for key, (label, fields) in list_labels.items():
            records = data.get(key)

            if isinstance(records, list):
                found_list = True
                lines.append(f"{label} found: {data.get('count', len(records))}")

                if not records:
                    lines.append(f"No {label.lower()} found.")
                    continue

                for index, record in enumerate(records, start=1):
                    if not isinstance(record, dict):
                        continue

                    details = [
                        f"{field.replace('_', ' ').title()}: {record[field]}"
                        for field in fields
                        if field in record and record[field] is not None
                    ]
                    lines.append(f"{index}. " + "; ".join(details))

                limit = data.get("limit")
                if isinstance(limit, int) and len(records) >= limit:
                    lines.append(f"Showing up to {limit} records returned by FinTrack.")

        # Reports endpoint contains several different sections.
        if isinstance(data.get("summaries"), list):
            found_list = True
            lines.append("Report summaries:")
            for item in data["summaries"]:
                if isinstance(item, dict):
                    lines.append(
                        f"- {item.get('title', 'Summary')}: "
                        f"{item.get('amount', 'Not provided')} "
                        f"{item.get('subtitle', '')}".strip()
                    )

        if isinstance(data.get("categories"), list):
            found_list = True
            lines.append("Spending categories:")
            for item in data["categories"]:
                if isinstance(item, dict):
                    lines.append(
                        f"- {item.get('name', 'Unknown category')}: "
                        f"{item.get('amount', 'Not provided')} "
                        f"({item.get('percentage', 'Not provided')}%)"
                    )

        if isinstance(data.get("top_spendings"), list):
            found_list = True
            lines.append("Top spendings:")
            for item in data["top_spendings"]:
                if isinstance(item, dict):
                    lines.append(
                        f"- {item.get('name', 'Unknown item')}: "
                        f"{item.get('amount', 'Not provided')} "
                        f"(Category: {item.get('category', 'Unknown')})"
                    )

        insights = data.get("insights")
        if isinstance(insights, dict):
            found_list = True
            lines.append(insights.get("title", "Finance insights"))
            for key in ("point_1", "point_2", "point_3"):
                if insights.get(key):
                    lines.append(f"- {insights[key]}")

        if not found_list:
            lines.append(
                "FinTrack returned data, but its response format was unexpected."
            )

        return {
            "agent": self.name,
            "status": "success",
            "source": "FinTrack",
            "data": data,
            "message": "\n".join(lines),
        }

    def process(self, request, user, credentials=None):
        request_lower = request.lower()

        # Specific FinTrack categories must be checked before the
        # general FinTrack summary keyword.
        category_actions = [
            (
                "get_fintrack_reports",
                "FinTrack Reports",
                [
                    "report",
                    "reports",
                    "spending breakdown",
                    "top spending",
                    "top spendings",
                    "spending category",
                    "spending categories",
                    "finance insights",
                ],
            ),
            (
                "get_fintrack_transactions",
                "FinTrack Transactions",
                [
                    "transaction",
                    "transactions",
                    "spend",
                    "spent",
                    "my income",
                    "my expenses",
                    "money spent",
                ],
            ),
            (
                "get_fintrack_bills",
                "FinTrack Bills",
                ["bill", "bills", "overdue bill", "due bills"],
            ),
            (
                "get_fintrack_budgets",
                "FinTrack Budgets",
                ["budget", "budgets", "budget usage", "budget limit"],
            ),
            (
                "get_fintrack_accounts",
                "FinTrack Accounts",
                [
                    "account",
                    "accounts",
                    "bank balance",
                    "account balance",
                    "left in my account",
                ],
            ),
        ]

        for action, title, keywords in category_actions:
            if any(keyword in request_lower for keyword in keywords):
                return self._get_fintrack_response(action, user, title)

        # Explicit FinTrack summary.
        fintrack_summary_keywords = [
            "fintrack",
            "my finance data",
            "my financial data",
            "my personal finance",
            "personal finance summary",
            "my financial summary",
            "remaining balance",
        ]

        if any(keyword in request_lower for keyword in fintrack_summary_keywords):
            result = self.finance_tool.execute("get_fintrack_summary", user)

            if result.get("status") == "success":
                data = result.get("data", {})
                currency = data.get("currency", "INR")

                message = (
                    "FinTrack Financial Summary:\n"
                    f"Total Income: {currency} {data.get('total_income', 0)}\n"
                    f"Total Expenses: {currency} {data.get('total_expenses', 0)}\n"
                    f"Net Balance: {currency} {data.get('net_balance', 0)}"
                )

                return {
                    "agent": self.name,
                    "status": "success",
                    "source": "FinTrack",
                    "data": data,
                    "message": message,
                }

            return {
                "agent": self.name,
                "status": result.get("status", "error"),
                "source": "FinTrack",
                "data": {},
                "message": result.get(
                    "message",
                    "Unable to retrieve FinTrack financial data.",
                ),
            }

        # Preserve the existing company payments-due-today behaviour.
        if "payment" in request_lower and (
            "due" in request_lower or "today" in request_lower
        ):
            result = self.finance_tool.execute("get_payments_due_today", user)

            if result.get("status") == "success":
                data = result.get("data", {})
                payments = data.get("payments_due_today", [])

                if payments:
                    payment_lines = [
                        f"- {payment.get('customer', 'Unknown customer')}: "
                        f"{payment.get('amount', 0)} "
                        f"(Due: {payment.get('due_date', 'Unknown date')})"
                        for payment in payments
                    ]
                    message = f"Payments Due Today: {len(payments)}\n" + "\n".join(
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

        # Preserve the existing Vetri company finance summary.
        if any(
            keyword in request_lower
            for keyword in (
                "finance",
                "financial",
                "revenue",
                "expense",
                "expenses",
                "profit",
                "summary",
            )
        ):
            result = self.finance_tool.execute("get_finance_summary", user)

            if result.get("status") == "success":
                data = result.get("data", {})
                message = (
                    "Company Finance Summary:\n"
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
            "message": (
                "The requested finance information is not currently supported."
            ),
        }
