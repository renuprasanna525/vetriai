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

        return any(
            keyword in request_lower
            for keyword in sales_keywords
        )

    def get_required_permission(self, request):

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
            keyword in request_lower
            for keyword in knowledge_keywords
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

        # =====================================================
        # IMPORTANT:
        # Contextual requests from the Orchestrator can contain
        # previous user/assistant messages.
        #
        # Example:
        #
        # Previous assistant message:
        # Current sales summary...
        #
        # Current user question:
        # What about the orders?
        #
        # We must use ONLY the current user question for
        # Sales intent detection.
        # =====================================================

        if "current user question:" in request_lower:

            current_question = request_lower.split(
                "current user question:",
                1
            )[1].strip()

        else:

            current_question = request_lower

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
            keyword in current_question
            for keyword in knowledge_keywords
        )

        if is_knowledge_question:

            knowledge_answer = self.rag.generate_answer(
                request
            )

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
        # General Sales Request
        # ==========================================
        #
        # IMPORTANT:
        # Use current_question instead of request_lower.
        #
        # This prevents previous assistant messages such as:
        #
        # "Current sales summary..."
        #
        # from incorrectly turning:
        #
        # "What about the orders?"
        #
        # into a complete sales summary.
        # ==========================================

        is_general_sales_request = (
            "sales" in current_question
            or "sale" in current_question
            or "sales status" in current_question
            or "sales summary" in current_question
            or "sales overview" in current_question
            or "current sales" in current_question
            or "sales information" in current_question
            or "revenue" in current_question
        )

        if is_general_sales_request:

            # ------------------------------------------
            # Get Leads
            # ------------------------------------------

            leads_result = self.crm_tool.execute(
                "get_leads",
                user,
            )

            # ------------------------------------------
            # Get Pending Follow-ups
            # ------------------------------------------

            followups_result = self.crm_tool.execute(
                "get_pending_followups",
                user,
            )

            # ------------------------------------------
            # Get Customers
            # ------------------------------------------

            customers_result = self.crm_tool.execute(
                "get_customers",
                user,
            )

            # ------------------------------------------
            # Get Orders
            # ------------------------------------------

            orders_result = self.crm_tool.execute(
                "get_orders",
                user,
            )

            # ------------------------------------------
            # Extract Leads Data
            # ------------------------------------------

            leads_data = (
                leads_result.get("data", {})
                if leads_result.get("status") == "success"
                else {}
            )

            # ------------------------------------------
            # Extract Follow-up Data
            # ------------------------------------------

            followups_data = (
                followups_result.get("data", {})
                if followups_result.get("status") == "success"
                else {}
            )

            # ------------------------------------------
            # Extract Customer Data
            # ------------------------------------------

            customers_data = (
                customers_result.get("data", {})
                if customers_result.get("status") == "success"
                else {}
            )

            # ------------------------------------------
            # Extract Order Data
            # ------------------------------------------

            orders_data = (
                orders_result.get("data", {})
                if orders_result.get("status") == "success"
                else {}
            )

            # ------------------------------------------
            # Prepare Summary Values
            # ------------------------------------------

            total_leads = leads_data.get(
                "total_leads",
                0,
            )

            new_leads = leads_data.get(
                "new_leads",
                0,
            )

            pending_followups = followups_data.get(
                "pending_followups",
                [],
            )

            customers = customers_data.get(
                "customers",
                [],
            )

            total_orders = orders_data.get(
                "total_orders",
                0,
            )

            pending_orders = orders_data.get(
                "pending_orders",
                0,
            )

            # ------------------------------------------
            # Build Natural Sales Summary
            # ------------------------------------------

            message = (
                "Current sales summary: "
                f"{total_leads} total leads, "
                f"{new_leads} new leads, "
                f"{len(pending_followups)} pending follow-ups, "
                f"{len(customers)} customers, "
                f"{total_orders} total orders, "
                f"{pending_orders} pending orders."
            )

            # ------------------------------------------
            # Return Combined Sales Data
            # ------------------------------------------

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
        # Pending Follow-ups
        # ==========================================

        if (
            "follow-up" in current_question
            or "follow up" in current_question
            or "followups" in current_question
        ):

            result = self.crm_tool.execute(
                "get_pending_followups",
                user,
            )

            if result.get("status") == "success":

                followups = (
                    result.get("data", {})
                    .get("pending_followups", [])
                )

                if not followups:

                    message = (
                        "There are no pending follow-ups."
                    )

                else:

                    followup_lines = []

                    for followup in followups:

                        customer = followup.get(
                            "customer",
                            "Unknown customer",
                        )

                        days_pending = followup.get(
                            "days_pending",
                            0,
                        )

                        followup_lines.append(
                            f"{customer}: "
                            f"{days_pending} days pending"
                        )

                    message = (
                        f"There are currently "
                        f"{len(followups)} customers "
                        "requiring follow-up:\n"
                        + "\n".join(followup_lines)
                    )

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": result.get(
                        "data",
                        {},
                    ),
                    "message": message,
                }

        # ==========================================
        # Leads
        # ==========================================

        if "lead" in current_question:

            result = self.crm_tool.execute(
                "get_leads",
                user,
            )

            if result.get("status") == "success":

                data = result.get(
                    "data",
                    {},
                )

                message = (
                    f"There are "
                    f"{data.get('total_leads', 0)} "
                    "total leads, including "
                    f"{data.get('new_leads', 0)} "
                    "new leads."
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

        if "customer" in current_question:

            result = self.crm_tool.execute(
                "get_customers",
                user,
            )

            if result.get("status") == "success":

                data = result.get(
                    "data",
                    {},
                )

                customers = data.get(
                    "customers",
                    [],
                )

                if not customers:

                    message = (
                        "There are no customers "
                        "in the CRM."
                    )

                else:

                    customer_names = [
                        customer["name"]
                        for customer in customers
                    ]

                    message = (
                        f"There are {len(customers)} "
                        "customers: "
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

        if "order" in current_question:

            # ------------------------------------------
            # Pending Orders
            # ------------------------------------------

            if "pending" in current_question:

                result = self.crm_tool.execute(
                    "get_pending_orders",
                    user,
                )

                if result.get("status") == "success":

                    data = result.get(
                        "data",
                        {},
                    )

                    orders = data.get(
                        "orders",
                        [],
                    )

                    if not orders:

                        message = (
                            "There are no pending "
                            "orders."
                        )

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
                            "pending orders:\n"
                            + "\n".join(order_lines)
                        )

                    return {
                        "agent": self.name,
                        "status": "success",
                        "data": data,
                        "message": message,
                    }

            # ------------------------------------------
            # All Orders
            # ------------------------------------------

            else:

                result = self.crm_tool.execute(
                    "get_orders",
                    user,
                )

                if result.get("status") == "success":

                    data = result.get(
                        "data",
                        {},
                    )

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
                        "total orders, including "
                        f"{pending_orders} "
                        "pending orders."
                    )

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
                "The requested sales information "
                "is not currently supported."
            ),
        }