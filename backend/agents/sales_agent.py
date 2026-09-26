from .base_agent import BaseAgent
from tools.crm_tool import CRMTool
from knowledge_base.rag import RAGSystem


class SalesAgent(BaseAgent):

    name = "Sales Agent"

    description = "Handles sales, leads, follow-ups and orders"

    def __init__(self):
        self.crm_tool = CRMTool()
        self.rag = RAGSystem()

    def can_handle(self, request):

        sales_keywords = [
            "sales",
            "sale",
            "lead",
            "leads",
            "follow-up",
            "follow up",
            "followups",
            "customer",
            "customers",
            "order",
            "orders",
            "revenue",
            "sales policy",
            "sales sop",
            "sales process",
        ]

        request_lower = request.lower()

        return any(keyword in request_lower for keyword in sales_keywords)

    def get_required_permission(self, request):

        request_lower = request.lower()

        # Knowledge Base / Sales SOP questions
        knowledge_keywords = [
            "policy",
            "sop",
            "process",
            "procedure",
            "how can",
            "how do",
            "how soon",
            "follow-up process",
            "follow up process",
        ]

        is_knowledge_question = any(
            keyword in request_lower for keyword in knowledge_keywords
        )

        if is_knowledge_question:
            return None

        if "lead" in request_lower:
            return "view_leads"

        if "customer" in request_lower:
            return "view_customers"

        if "order" in request_lower:
            return "view_orders"

        if "sales" in request_lower or "sale" in request_lower:
            return "view_sales"

        if "revenue" in request_lower:
            return "view_sales"

        return "view_sales"

    def process(self, request, user, credentials=None):

        request_lower = request.lower()

        # ==========================================
        # Knowledge Base / Sales SOP Questions
        # ==========================================

        knowledge_keywords = [
            "policy",
            "sop",
            "process",
            "procedure",
            "how can",
            "how do",
            "how soon",
            "follow-up process",
            "follow up process",
        ]

        is_knowledge_question = any(
            keyword in request_lower for keyword in knowledge_keywords
        )

        if is_knowledge_question:

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

                followups = result.get("data", {}).get("pending_followups", [])

                if not followups:
                    message = "There are no pending follow-ups."

                else:
                    message = f"There are {len(followups)} " "pending follow-ups."

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": result.get("data", {}),
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
                    f"There are {data.get('total_leads', 0)} "
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
                customers = data.get("customers", [])

                if not customers:
                    message = "There are no customers in the CRM."

                else:

                    customer_names = [customer["name"] for customer in customers]

                    message = (
                        f"There are {len(customers)} customers: "
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

            # Pending orders
            if "pending" in request_lower:

                result = self.crm_tool.execute(
                    "get_pending_orders",
                    user,
                )

                if result.get("status") == "success":

                    data = result.get("data", {})
                    orders = data.get("orders", [])

                    if not orders:
                        message = "There are no pending orders."

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
                            "pending orders:\n" + "\n".join(order_lines)
                        )

                    return {
                        "agent": self.name,
                        "status": "success",
                        "data": data,
                        "message": message,
                    }

            # All orders
            else:

                result = self.crm_tool.execute(
                    "get_orders",
                    user,
                )

                if result.get("status") == "success":

                    data = result.get("data", {})

                    total_orders = data.get(
                        "total_orders",
                        0,
                    )

                    pending_orders = data.get(
                        "pending_orders",
                        0,
                    )

                    message = (
                        f"There are {total_orders} "
                        f"total orders, including "
                        f"{pending_orders} pending orders."
                    )

                    return {
                        "agent": self.name,
                        "status": "success",
                        "data": data,
                        "message": message,
                    }

        # ==========================================
        # General Sales Request
        # ==========================================

        if (
            "sales" in request_lower
            or "sale" in request_lower
            or "revenue" in request_lower
        ):

            # Get leads
            leads_result = self.crm_tool.execute(
                "get_leads",
                user,
            )
            # Get Pending Follow-ups
            followups_result = self.crm_tool.execute(
                "get_pending_followups",
                user,
            )
            # Get Customers
            customers_result = self.crm_tool.execute(
                "get_customers",
                user,
            )
            # Get Orders
            orders_result = self.crm_tool.execute(
                "get_orders",
                user,
            )

            leads_data = (
                leads_result.get("data", {})
                if leads_result.get("status") == "success"
                else {}
            )

            followups_data = (
                followups_result.get("data", {})
                if followups_result.get("status") == "success"
                else {}
            )

            customers_data = (
                customers_result.get("data", {})
                if customers_result.get("status") == "success"
                else {}
            )

            orders_data = (
                orders_result.get("data", {})
                if orders_result.get("status") == "success"
                else {}
            )

            total_leads = leads_data.get("total_leads", 0)
            new_leads = leads_data.get("new_leads", 0)

            pending_followups = followups_data.get("pending_followups", [])
            customers = customers_data.get("customers", [])
            total_orders = orders_data.get("total_orders", 0)
            pending_orders = orders_data.get("pending_orders", 0)

            message = (
                "Current sales summary: "
                f"{total_leads} total leads, "
                f"{new_leads} new leads, "
                f"{len(pending_followups)} pending follow-ups, "
                f"{len(customers)} customers, "
                f"{total_orders} total orders, "
                f"{pending_orders} pending orders."
            )

            data = {
                "total_leads": total_leads,
                "new_leads": new_leads,
                "pending_followups": pending_followups,
                "customers": customers,
                "total_orders": total_orders,
                "pending_orders": pending_orders,
            }

            return {
                "agent": self.name,
                "status": "success",
                "data": data,
                "message": message,
            }

        # ==========================================
        # Unsupported Request
        # ==========================================

        return {
            "agent": self.name,
            "status": "error",
            "data": {},
            "message": (
                "The requested sales information " "is not currently supported."
            ),
        }
