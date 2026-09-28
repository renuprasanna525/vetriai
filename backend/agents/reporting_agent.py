from .base_agent import BaseAgent
from knowledge_base.rag import RAGSystem
from tools.reporting_tool import ReportingTool


class ReportingAgent(BaseAgent):

    name = "Reporting Agent"

    description = "Handles detailed business reports and summaries"

    def __init__(self):
        self.rag = RAGSystem()
        self.reporting_tool = ReportingTool()

    def can_handle(self, request):

        reporting_keywords = [
            "report",
            "reports",
            "reporting",
            "summary",
            "summarize",
            "business report",
            "daily report",
            "bo report",
        ]

        request_lower = request.lower()

        return any(keyword in request_lower for keyword in reporting_keywords)

    def get_required_permission(self, request):

        request_lower = request.lower()

        knowledge_keywords = [
            "policy",
            "sop",
            "process",
            "procedure",
            "how can",
            "how do",
            "how should",
            "reporting process",
            "reporting sop",
            "business reporting",
        ]

        is_knowledge_question = any(
            keyword in request_lower for keyword in knowledge_keywords
        )

        if is_knowledge_question:
            return None

        return "view_reports"

    def process(
        self,
        request,
        user,
        credentials=None,
    ):

        request_lower = request.lower()

        # -----------------------------------------
        # Knowledge Base / Reporting SOP Questions
        # -----------------------------------------

        knowledge_keywords = [
            "policy",
            "sop",
            "process",
            "procedure",
            "how can",
            "how do",
            "how should",
            "reporting process",
            "reporting sop",
            "business reporting",
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

        # -----------------------------------------
        # Generate Business Report
        # -----------------------------------------

        report_result = self.reporting_tool.execute(
            "generate_daily_report",
            user=user,
        )

        if report_result.get("status") != "success":

            return {
                "agent": self.name,
                "status": "error",
                "data": {},
                "message": report_result.get(
                    "message",
                    "Unable to generate the business report.",
                ),
            }

        report = report_result.get("data", {})

        # -----------------------------------------
        # Extract Report Sections
        # -----------------------------------------

        finance = report.get("finance", {})
        sales = report.get("sales", {})
        projects = report.get("projects", {})
        hr = report.get("hr", {})

        followups = sales.get("pending_followups", [])
        project_list = projects.get("projects", [])
        delayed_list = projects.get("delayed_projects", [])
        employees_on_leave = hr.get("employees_on_leave", [])

        # -----------------------------------------
        # Finance
        # -----------------------------------------

        revenue = finance.get("total_revenue", 0)
        expenses = finance.get("total_expenses", 0)
        profit = finance.get("net_profit", 0)

        message = (
            "Today's Detailed Business Performance Report\n\n"
            "FINANCE\n"
            f"- Total revenue: ₹{revenue:,}\n"
            f"- Total expenses: ₹{expenses:,}\n"
            f"- Net profit: ₹{profit:,}\n\n"
        )

        # -----------------------------------------
        # Sales
        # -----------------------------------------

        message += (
            "SALES\n"
            f"- Total leads: {sales.get('total_leads', 0)}\n"
            f"- New leads: {sales.get('new_leads', 0)}\n"
            f"- Pending follow-ups: {len(followups)}\n"
            f"- Total customers: {sales.get('total_customers', 0)}\n"
            f"- Total orders: {sales.get('total_orders', 0)}\n"
            f"- Pending orders: {sales.get('pending_orders', 0)}\n\n"
        )

        if followups:
            message += "Pending follow-up details:\n"

            for followup in followups:
                message += (
                    f"- {followup.get('customer', 'Unknown customer')}: "
                    f"{followup.get('days_pending', 0)} days pending\n"
                )

            message += "\n"

        # -----------------------------------------
        # Projects
        # -----------------------------------------

        message += (
            "PROJECTS\n"
            f"- Total projects: {projects.get('total_projects', 0)}\n"
            f"- Active projects: {projects.get('active_projects', 0)}\n"
            f"- Completed projects: {projects.get('completed_projects', 0)}\n"
            f"- Delayed projects: {projects.get('total_delayed', 0)}\n"
        )

        if project_list:
            message += "\nProject details:\n"

            for project in project_list:
                message += (
                    f"- {project.get('name', 'Unnamed project')}: "
                    f"{project.get('status', 'Status unavailable')}, "
                    f"{project.get('progress', 0)}% complete\n"
                )

        if delayed_list:
            message += "\nDelayed project details:\n"

            for project in delayed_list:
                message += (
                    f"- {project.get('name', 'Unnamed project')}: "
                    f"{project.get('delay_days', 0)} days delayed\n"
                )

        message += "\n"

        # -----------------------------------------
        # Human Resources
        # -----------------------------------------

        message += (
            "HR\n"
            f"- Total employees: {hr.get('total_employees', 0)}\n"
            f"- Employees currently on leave: "
            f"{hr.get('total_on_leave', 0)}\n"
        )

        if employees_on_leave:
            message += "\nEmployees on leave:\n"

            for employee in employees_on_leave:
                message += (
                    f"- {employee.get('name', 'Name unavailable')} "
                    f"({employee.get('department', 'Department unavailable')})"
                    f" - {employee.get('leave_type', 'Leave type unavailable')}\n"
                )

        # -----------------------------------------
        # Return Detailed Report
        # -----------------------------------------

        return {
            "agent": self.name,
            "status": "success",
            "data": report,
            "message": message,
        }
