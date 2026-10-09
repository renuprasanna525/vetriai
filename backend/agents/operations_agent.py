from .base_agent import BaseAgent


class OperationsAgent(BaseAgent):

    name = "Operations Agent"

    description = (
        "Handles operations, processes, workflows, "
        "productivity, and operational performance questions"
    )

    def can_handle(self, request):

        operations_keywords = [
            "operations",
            "operation",
            "operational",
            "workflow",
            "workflows",
            "process",
            "processes",
            "operational performance",
            "operations summary",
            "productivity",
            "efficiency",
            "active workflow",
            "active workflows",
            "completed process",
            "completed processes",
            "pending task",
            "pending tasks",
        ]

        request_lower = request.lower()

        return any(keyword in request_lower for keyword in operations_keywords)

    def get_required_permission(self, request):

        return "view_operations"

    def process(self, request, user, credentials=None):

        request_lower = request.lower()

        operations_keywords = [
            "operations",
            "operation",
            "operational",
            "workflow",
            "workflows",
            "process",
            "processes",
            "operational performance",
            "operations summary",
            "productivity",
            "efficiency",
            "active workflow",
            "active workflows",
            "completed process",
            "completed processes",
            "pending task",
            "pending tasks",
        ]

        if not any(keyword in request_lower for keyword in operations_keywords):
            return {
                "agent": self.name,
                "status": "unsupported",
                "data": {},
                "message": (
                    "The requested operations information "
                    "is not currently supported."
                ),
            }

        data = {
            "active_workflows": 8,
            "completed_processes": 42,
            "pending_tasks": 15,
            "efficiency": "88%",
        }

        # Focused: Active Workflows

        if (
            "active workflow" in request_lower
            or "active workflows" in request_lower
            or "how many workflows" in request_lower
            or "how many workflow" in request_lower
        ):
            message = f"There are {data['active_workflows']} active workflows."

            return {
                "agent": self.name,
                "status": "success",
                "data": {"active_workflows": data["active_workflows"]},
                "message": message,
            }

        # Focused: Completed Processes

        if (
            "completed process" in request_lower
            or "completed processes" in request_lower
            or "how many processes" in request_lower
        ):
            message = f"There are {data['completed_processes']} completed processes."

            return {
                "agent": self.name,
                "status": "success",
                "data": {"completed_processes": data["completed_processes"]},
                "message": message,
            }

        # Focused: Pending Tasks

        if "pending task" in request_lower or "pending tasks" in request_lower:
            message = f"There are {data['pending_tasks']} pending tasks."

            return {
                "agent": self.name,
                "status": "success",
                "data": {"pending_tasks": data["pending_tasks"]},
                "message": message,
            }

        # Focused: Efficiency

        if (
            "efficiency" in request_lower
            or "operational performance" in request_lower
            or "productivity" in request_lower
        ):
            message = f"Operations efficiency is {data['efficiency']}."

            return {
                "agent": self.name,
                "status": "success",
                "data": {"efficiency": data["efficiency"]},
                "message": message,
            }

        # Default: Operations Summary

        message = (
            "Operations Summary:\n"
            f"Active Workflows: {data['active_workflows']}\n"
            f"Completed Processes: {data['completed_processes']}\n"
            f"Pending Tasks: {data['pending_tasks']}\n"
            f"Efficiency: {data['efficiency']}"
        )

        return {
            "agent": self.name,
            "status": "success",
            "data": data,
            "message": message,
        }
