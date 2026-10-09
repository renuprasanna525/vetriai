from .base_agent import BaseAgent


class CustomerSupportAgent(BaseAgent):

    name = "Customer Support Agent"

    description = (
        "Handles customer support, customer issues, complaints, "
        "follow-ups, tickets, and support information"
    )

    def can_handle(self, request):

        support_keywords = [
            "customer support",
            "customer service",
            "support",
            "customer issue",
            "customer issues",
            "issue",
            "issues",
            "complaint",
            "complaints",
            "ticket",
            "tickets",
            "support request",
            "support requests",
            "customer problem",
            "customer problems",
            "customer complaint",
            "open issue",
            "open issues",
            "resolved issue",
            "resolved issues",
            "pending issue",
            "pending issues",
            "pending request",
            "pending requests",
        ]

        request_lower = request.lower()

        return any(keyword in request_lower for keyword in support_keywords)

    def get_required_permission(self, request):

        return "view_customer_support"

    def process(self, request, user, credentials=None):

        request_lower = request.lower()

        support_keywords = [
            "customer support",
            "customer service",
            "support",
            "customer issue",
            "customer issues",
            "issue",
            "issues",
            "complaint",
            "complaints",
            "ticket",
            "tickets",
            "support request",
            "support requests",
            "customer problem",
            "customer problems",
            "customer complaint",
            "open issue",
            "open issues",
            "resolved issue",
            "resolved issues",
            "pending issue",
            "pending issues",
            "pending request",
            "pending requests",
        ]

        if not any(keyword in request_lower for keyword in support_keywords):
            return {
                "agent": self.name,
                "status": "unsupported",
                "data": {},
                "message": (
                    "The requested customer support information "
                    "is not currently supported."
                ),
            }

        data = {
            "total_customers": 3,
            "open_issues": 4,
            "pending_requests": 3,
            "resolved_issues": 18,
        }

        # Focused: Open Issues

        if (
            "open issue" in request_lower
            or "open issues" in request_lower
            or "issues are open" in request_lower
        ):
            message = f"There are {data['open_issues']} open issues."

            return {
                "agent": self.name,
                "status": "success",
                "data": {"open_issues": data["open_issues"]},
                "message": message,
            }

        # Focused: Resolved Issues

        if (
            "resolved issue" in request_lower
            or "resolved issues" in request_lower
            or "issues are resolved" in request_lower
        ):
            message = f"There are {data['resolved_issues']} resolved issues."

            return {
                "agent": self.name,
                "status": "success",
                "data": {"resolved_issues": data["resolved_issues"]},
                "message": message,
            }

        # Focused: Pending Requests

        if (
            "pending request" in request_lower
            or "pending requests" in request_lower
            or "requests are pending" in request_lower
        ):
            message = f"There are {data['pending_requests']} pending requests."

            return {
                "agent": self.name,
                "status": "success",
                "data": {"pending_requests": data["pending_requests"]},
                "message": message,
            }

        # Focused: Total Customers

        if (
            "total customer" in request_lower
            or "total customers" in request_lower
            or "how many customers" in request_lower
        ):
            message = f"There are {data['total_customers']} customers."

            return {
                "agent": self.name,
                "status": "success",
                "data": {"total_customers": data["total_customers"]},
                "message": message,
            }

        # Default: Customer Support Summary

        message = (
            "Customer Support Summary:\n"
            f"Total Customers: {data['total_customers']}\n"
            f"Open Issues: {data['open_issues']}\n"
            f"Pending Requests: {data['pending_requests']}\n"
            f"Resolved Issues: {data['resolved_issues']}"
        )

        return {
            "agent": self.name,
            "status": "success",
            "data": data,
            "message": message,
        }
