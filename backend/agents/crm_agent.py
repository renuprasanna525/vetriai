from .base_agent import BaseAgent
from tools.crm_tool import CRMTool
from knowledge_base.rag import RAGSystem


class CRMAgent(BaseAgent):

    name = "CRM Agent"

    description = "Handles CRM, customers, leads, follow-ups and orders"

    def __init__(self):
        self.crm_tool = CRMTool()
        self.rag = RAGSystem()

    def can_handle(self, request):

        crm_keywords = [
            "crm",
            "crm status",
            "crm summary",
            "crm overview",
            "customer relationship",
            "customer relationships",
            "customer management",
            "customer records",
            "customer database",
        ]

        request_lower = request.lower()

        return any(keyword in request_lower for keyword in crm_keywords)

    def get_required_permission(self, request):

        request_lower = request.lower()

        if "lead" in request_lower:
            return "view_leads"

        if "customer" in request_lower:
            return "view_customers"

        if "order" in request_lower:
            return "view_orders"

        return "view_sales"

    def process(self, request, user, credentials=None):

        print("CRM REQUEST:", request)
        print(
            "CRM PERMISSION:",
            self.get_required_permission(request),
        )

        request_lower = request.lower()

        # ==========================================
        # CRM Knowledge / Policy Questions
        # ==========================================

        knowledge_keywords = [
            "policy",
            "sop",
            "process",
            "procedure",
            "how can",
            "how do",
            "crm process",
            "crm policy",
            "crm sop",
        ]

        if any(keyword in request_lower for keyword in knowledge_keywords):

            knowledge_answer = self.rag.generate_answer(request)

            if knowledge_answer:
                return {
                    "agent": self.name,
                    "status": "success",
                    "data": {
                        "knowledge_answer": knowledge_answer,
                    },
                    "message": knowledge_answer,
                }

        # ==========================================
        # CRM Status / Summary
        # ==========================================

        if "crm" in request_lower and (
            "status" in request_lower
            or "summary" in request_lower
            or "overview" in request_lower
        ):

            leads_result = self.crm_tool.execute(
                "get_leads",
                user,
            )

            customers_result = self.crm_tool.execute(
                "get_customers",
                user,
            )

            orders_result = self.crm_tool.execute(
                "get_orders",
                user,
            )

            followups_result = self.crm_tool.execute(
                "get_pending_followups",
                user,
            )

            leads_data = leads_result.get("data", {})
            customers_data = customers_result.get("data", {})
            orders_data = orders_result.get("data", {})
            followups_data = followups_result.get("data", {})

            total_leads = leads_data.get(
                "total_leads",
                0,
            )

            new_leads = leads_data.get(
                "new_leads",
                0,
            )

            total_customers = customers_data.get(
                "total_customers",
                0,
            )

            total_orders = orders_data.get(
                "total_orders",
                0,
            )

            pending_orders = orders_data.get(
                "pending_orders",
                0,
            )

            pending_followups = followups_data.get(
                "pending_followups",
                [],
            )

            message = (
                "Current CRM Summary:\n"
                f"Total Leads: {total_leads}\n"
                f"New Leads: {new_leads}\n"
                f"Total Customers: {total_customers}\n"
                f"Total Orders: {total_orders}\n"
                f"Pending Orders: {pending_orders}\n"
                f"Pending Follow-ups: {len(pending_followups)}"
            )

            return {
                "agent": self.name,
                "status": "success",
                "data": {
                    "leads": leads_data,
                    "customers": customers_data,
                    "orders": orders_data,
                    "followups": followups_data,
                },
                "message": message,
            }

        # ==========================================
        # Pending Follow-ups
        # ==========================================

        if (
            "follow-up" in request_lower
            or "follow up" in request_lower
            or "followups" in request_lower
        ):

            result = self.crm_tool.execute(
                "get_pending_followups",
                user,
            )

            if result.get("status") == "success":

                data = result.get("data", {})
                followups = data.get(
                    "pending_followups",
                    [],
                )

                if not followups:
                    message = "There are no pending CRM follow-ups."

                else:

                    lines = []

                    for followup in followups:
                        lines.append(
                            f"{followup['customer']} - "
                            f"{followup['days_pending']} days pending"
                        )

                    message = (
                        f"There are {len(followups)} "
                        "pending CRM follow-ups:\n" + "\n".join(lines)
                    )

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": data,
                    "message": message,
                }

        # ==========================================
        # Leads
        # ==========================================

        if "lead" in request_lower:

            result = self.crm_tool.execute(
                "get_leads",
                user,
            )

            if result.get("status") == "success":

                data = result.get("data", {})

                message = (
                    f"CRM has {data.get('total_leads', 0)} "
                    f"total leads, including "
                    f"{data.get('new_leads', 0)} new leads."
                )

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": data,
                    "message": message,
                }

        # ==========================================
        # Customers
        # ==========================================

        if "customer" in request_lower:

            result = self.crm_tool.execute(
                "get_customers",
                user,
            )

            if result.get("status") == "success":

                data = result.get("data", {})
                customers = data.get(
                    "customers",
                    [],
                )

                if not customers:

                    message = "There are no customers in the CRM."

                else:

                    customer_names = [customer["name"] for customer in customers]

                    message = (
                        f"There are {len(customers)} CRM customers: "
                        + ", ".join(customer_names)
                        + "."
                    )

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": data,
                    "message": message,
                }

        # ==========================================
        # Orders
        # ==========================================

        if "order" in request_lower:

            if "pending" in request_lower:

                result = self.crm_tool.execute(
                    "get_pending_orders",
                    user,
                )

                if result.get("status") == "success":

                    data = result.get("data", {})
                    orders = data.get(
                        "orders",
                        [],
                    )

                    if not orders:

                        message = "There are no pending CRM orders."

                    else:

                        order_lines = []

                        for order in orders:
                            order_lines.append(
                                f"{order['order_id']} - "
                                f"{order['customer']} - "
                                f"₹{order['amount']}"
                            )

                        message = (
                            f"There are {len(orders)} "
                            "pending CRM orders:\n" + "\n".join(order_lines)
                        )

                    return {
                        "agent": self.name,
                        "status": "success",
                        "data": data,
                        "message": message,
                    }

            else:

                result = self.crm_tool.execute(
                    "get_orders",
                    user,
                )

                if result.get("status") == "success":

                    data = result.get("data", {})

                    message = (
                        f"There are {data.get('total_orders', 0)} "
                        f"total CRM orders, including "
                        f"{data.get('pending_orders', 0)} "
                        "pending orders."
                    )

                    return {
                        "agent": self.name,
                        "status": "success",
                        "data": data,
                        "message": message,
                    }

        # ==========================================
        # Unsupported CRM Request
        # ==========================================

        return {
            "agent": self.name,
            "status": "error",
            "data": {},
            "message": ("The requested CRM information " "is not currently supported."),
        }
