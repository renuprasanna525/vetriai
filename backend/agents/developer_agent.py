from .base_agent import BaseAgent


class DeveloperAgent(BaseAgent):

    name = "Developer Agent"

    description = (
        "Handles software development, code, technical, programming, "
        "deployment, bugs, tasks, and developer performance questions"
    )

    def can_handle(self, request):

        developer_keywords = [
            "developer",
            "development",
            "code",
            "coding",
            "programming",
            "python",
            "django",
            "react",
            "javascript",
            "bug",
            "bugs",
            "debug",
            "debugging",
            "error",
            "technical",
            "software",
            "api",
            "database",
            "deployment",
            "deployments",
            "deploy",
            "deployed",
            "active project",
            "active projects",
            "completed task",
            "completed tasks",
        ]

        request_lower = request.lower()

        return any(keyword in request_lower for keyword in developer_keywords)

    def get_required_permission(self, request):

        return "view_developer"

    def process(self, request, user, credentials=None):

        request_lower = request.lower()

        developer_keywords = [
            "developer",
            "development",
            "code",
            "coding",
            "programming",
            "python",
            "django",
            "react",
            "javascript",
            "bug",
            "bugs",
            "debug",
            "debugging",
            "error",
            "technical",
            "software",
            "api",
            "database",
            "deployment",
            "deployments",
            "deploy",
            "deployed",
            "active project",
            "active projects",
            "completed task",
            "completed tasks",
        ]

        if not any(keyword in request_lower for keyword in developer_keywords):
            return {
                "agent": self.name,
                "status": "unsupported",
                "data": {},
                "message": (
                    "The requested developer information " "is not currently supported."
                ),
            }

        data = {
            "active_projects": 4,
            "open_bugs": 8,
            "completed_tasks": 27,
            "deployments": 6,
        }

        # Focused: Bugs

        if "bug" in request_lower or "bugs" in request_lower:
            message = f"There are {data['open_bugs']} open bugs."

            return {
                "agent": self.name,
                "status": "success",
                "data": {"open_bugs": data["open_bugs"]},
                "message": message,
            }

        # Focused: Deployments

        if (
            "deployment" in request_lower
            or "deployments" in request_lower
            or "deploy" in request_lower
            or "deployed" in request_lower
        ):
            message = f"There are {data['deployments']} deployments."

            return {
                "agent": self.name,
                "status": "success",
                "data": {"deployments": data["deployments"]},
                "message": message,
            }

        # Focused: Active Projects

        if "active project" in request_lower or "active projects" in request_lower:
            message = f"There are {data['active_projects']} active projects."

            return {
                "agent": self.name,
                "status": "success",
                "data": {"active_projects": data["active_projects"]},
                "message": message,
            }

        # Focused: Completed Tasks

        if "completed task" in request_lower or "completed tasks" in request_lower:
            message = f"There are {data['completed_tasks']} completed tasks."

            return {
                "agent": self.name,
                "status": "success",
                "data": {"completed_tasks": data["completed_tasks"]},
                "message": message,
            }

        # Default: Developer Summary

        message = (
            "Developer Summary:\n"
            f"Active Projects: {data['active_projects']}\n"
            f"Open Bugs: {data['open_bugs']}\n"
            f"Completed Tasks: {data['completed_tasks']}\n"
            f"Deployments: {data['deployments']}"
        )

        return {
            "agent": self.name,
            "status": "success",
            "data": data,
            "message": message,
        }
