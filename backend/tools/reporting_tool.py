from tools.crm_tool import CRMTool
from tools.project_tool import ProjectTool
from tools.database_tool import DatabaseTool
from tools.finance_tool import FinanceTool


class ReportingTool:
    """
    Controlled tool for generating business reports
    by combining existing business tools.

    Daily, weekly, and monthly reports are management
    snapshots based on the currently available business data.
    """

    name = "reporting_tool"
    description = "Generates detailed business reports."

    SUPPORTED_ACTIONS = {
        "generate_daily_report": "daily",
        "generate_weekly_report": "weekly",
        "generate_monthly_report": "monthly",
    }

    def execute(self, action, user=None):

        if action not in self.SUPPORTED_ACTIONS:
            return {
                "status": "error",
                "message": "Reporting action not supported.",
            }

        report_period = self.SUPPORTED_ACTIONS[action]

        crm_tool = CRMTool()
        project_tool = ProjectTool()
        database_tool = DatabaseTool()
        finance_tool = FinanceTool()

        # Collect data from existing tools
        leads_result = crm_tool.execute("get_leads", user=user)
        followups_result = crm_tool.execute(
            "get_pending_followups",
            user=user,
        )
        customers_result = crm_tool.execute(
            "get_customers",
            user=user,
        )
        orders_result = crm_tool.execute(
            "get_orders",
            user=user,
        )
        pending_orders_result = crm_tool.execute(
            "get_pending_orders",
            user=user,
        )

        projects_result = project_tool.execute(
            "get_projects",
            user=user,
        )
        project_status_result = project_tool.execute(
            "get_project_status",
            user=user,
        )
        delayed_projects_result = project_tool.execute(
            "get_delayed_projects",
            user=user,
        )

        employees_result = database_tool.execute(
            "get_employees",
            user=user,
        )
        leave_result = database_tool.execute(
            "get_employees_on_leave",
            user=user,
        )

        finance_result = finance_tool.execute(
            "get_finance_summary",
            user=user,
        )

        results = [
            leads_result,
            followups_result,
            customers_result,
            orders_result,
            pending_orders_result,
            projects_result,
            project_status_result,
            delayed_projects_result,
            employees_result,
            leave_result,
            finance_result,
        ]

        # Do not silently produce a partial report if a tool fails.
        failed_results = [
            result for result in results if result.get("status") != "success"
        ]

        if failed_results:
            return {
                "status": "error",
                "message": "Unable to collect all business report data.",
                "errors": [
                    result.get(
                        "message",
                        "Unknown tool error.",
                    )
                    for result in failed_results
                ],
            }

        # Extract tool data
        leads = leads_result.get("data", {})
        followups = followups_result.get("data", {})
        customers = customers_result.get("data", {})
        orders = orders_result.get("data", {})
        pending_orders = pending_orders_result.get("data", {})

        projects = projects_result.get("data", {})
        project_status = project_status_result.get("data", {})
        delayed_projects = delayed_projects_result.get("data", {})

        employees = employees_result.get("data", {})
        leave = leave_result.get("data", {})
        finance = finance_result.get("data", {})

        # Build combined report
        report = {
            "report_period": report_period,
            "report_type": "management_snapshot",
            "finance": {
                "total_revenue": finance.get(
                    "total_revenue",
                    0,
                ),
                "total_expenses": finance.get(
                    "total_expenses",
                    0,
                ),
                "net_profit": finance.get(
                    "net_profit",
                    0,
                ),
            },
            "sales": {
                "total_leads": leads.get(
                    "total_leads",
                    0,
                ),
                "new_leads": leads.get(
                    "new_leads",
                    0,
                ),
                "pending_followups": followups.get(
                    "pending_followups",
                    [],
                ),
                "total_customers": customers.get(
                    "total_customers",
                    0,
                ),
                "orders": orders.get(
                    "orders",
                    [],
                ),
                "total_orders": orders.get(
                    "total_orders",
                    0,
                ),
                "pending_orders": pending_orders.get(
                    "pending_orders",
                    0,
                ),
            },
            "projects": {
                "projects": projects.get(
                    "projects",
                    [],
                ),
                "total_projects": projects.get(
                    "total_projects",
                    0,
                ),
                "active_projects": project_status.get(
                    "active_projects",
                    0,
                ),
                "completed_projects": project_status.get(
                    "completed_projects",
                    0,
                ),
                "delayed_projects": delayed_projects.get(
                    "delayed_projects",
                    [],
                ),
                "total_delayed": delayed_projects.get(
                    "total_delayed",
                    0,
                ),
            },
            "hr": {
                "employees": employees.get(
                    "employees",
                    [],
                ),
                "total_employees": employees.get(
                    "total_employees",
                    0,
                ),
                "employees_on_leave": leave.get(
                    "employees_on_leave",
                    [],
                ),
                "total_on_leave": leave.get(
                    "total_on_leave",
                    0,
                ),
            },
        }

        # Preserve the original daily-summary fields
        # for compatibility with existing ReportingAgent logic.
        report.update(
            {
                "new_leads": report["sales"]["new_leads"],
                "pending_followups": len(report["sales"]["pending_followups"]),
                "pending_orders": report["sales"]["pending_orders"],
                "delayed_projects": report["projects"]["total_delayed"],
                "employees_on_leave": report["hr"]["total_on_leave"],
            }
        )

        return {
            "status": "success",
            "data": report,
        }
