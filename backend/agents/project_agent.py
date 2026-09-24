from .base_agent import BaseAgent
from tools.project_tool import ProjectTool
from knowledge_base.rag import RAGSystem


class ProjectAgent(BaseAgent):
    name = "Project Agent"
    description = "Handles project status and project tracking questions"

    def __init__(self):
        self.project_tool = ProjectTool()
        self.rag = RAGSystem()

    def can_handle(self, request):
        project_keywords = [
            "project",
            "projects",
            "delayed",
            "delay",
            "deadline",
            "deadlines",
            "task",
            "tasks",
            "milestone",
            "milestones",
            "project status",
            "project policy",
            "project sop",
            "project process",
        ]

        request_lower = request.lower()

        return any(keyword in request_lower for keyword in project_keywords)

    def get_required_permission(self, request):
        request_lower = request.lower()

        if any(
            keyword in request_lower
            for keyword in [
                "status",
                "delayed",
                "delay",
                "deadline",
                "milestone",
            ]
        ):
            return "view_project_status"

        if "task" in request_lower:
            if "my" in request_lower or "own" in request_lower:
                return "view_own_tasks"

            return "view_projects"

        if "project" in request_lower:
            if "my" in request_lower or "own" in request_lower:
                return "view_own_projects"

            return "view_projects"

        return "view_projects"

    def process(self, request, user, credentials=None):
        request_lower = request.lower()

        # =====================================================
        # PROJECT KNOWLEDGE / RAG
        # =====================================================

        knowledge_keywords = [
            "project policy",
            "project sop",
            "project process",
            "project guidelines",
            "project procedure",
        ]

        if any(keyword in request_lower for keyword in knowledge_keywords):
            try:
                rag_result = self.rag.query(request)

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": rag_result,
                    "message": str(rag_result),
                }

            except Exception as e:
                return {
                    "agent": self.name,
                    "status": "error",
                    "data": {},
                    "message": f"Unable to retrieve project knowledge: {str(e)}",
                }

        # =====================================================
        # KNOWN PROJECT NAMES
        # =====================================================

        project_names = [
            "Vetri E-Commerce",
            "AI Dashboard",
            "CRM System",
            "HR Management System",
        ]

        requested_project = None

        for project_name in project_names:
            if project_name.lower() in request_lower:
                requested_project = project_name
                break

        # =====================================================
        # SPECIFIC PROJECT REQUEST
        # Example:
        # "Tell me about Vetri E-Commerce"
        # =====================================================

        if requested_project:
            result = self.project_tool.execute("get_projects", user)

            if result.get("status") == "success":
                data = result.get("data", {})
                projects = data.get("projects", [])

                matching_project = next(
                    (
                        project
                        for project in projects
                        if project.get("name", "").lower() == requested_project.lower()
                    ),
                    None,
                )

                if matching_project:
                    project_name = matching_project.get("name", requested_project)

                    project_status = matching_project.get("status", "Unknown")

                    progress = matching_project.get("progress", "Unknown")

                    message = (
                        f"{project_name} is currently "
                        f"{project_status} with "
                        f"{progress}% progress."
                    )

                    return {
                        "agent": self.name,
                        "status": "success",
                        "data": {"project": matching_project},
                        "message": message,
                    }

        # =====================================================
        # DELAYED PROJECTS
        # =====================================================

        if "delayed" in request_lower or "delay" in request_lower:
            result = self.project_tool.execute("get_delayed_projects", user)

            if result.get("status") == "success":
                data = result.get("data", {})
                delayed_projects = data.get("delayed_projects", [])

                if delayed_projects:
                    details = []

                    for project in delayed_projects:
                        name = project.get("name", "Unknown project")

                        delay_days = project.get("delay_days", 0)

                        details.append(f"{name} is delayed by " f"{delay_days} days")

                    message = (
                        "The currently delayed projects are: "
                        + ", ".join(details)
                        + "."
                    )
                else:
                    message = "There are currently no delayed projects."

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": data,
                    "message": message,
                }

        # =====================================================
        # PROJECT DEADLINES
        # =====================================================

        if "deadline" in request_lower or "deadlines" in request_lower:
            result = self.project_tool.execute("get_project_deadlines", user)

            if result.get("status") == "success":
                data = result.get("data", {})
                deadlines = data.get("deadlines", [])

                if deadlines:
                    details = []

                    for deadline in deadlines:
                        project = deadline.get("project", "Unknown project")

                        date = deadline.get("deadline", "Unknown")

                        details.append(f"{project}: {date}")

                    message = (
                        "Here are the project deadlines: " + "; ".join(details) + "."
                    )
                else:
                    message = "There are currently no project deadlines available."

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": data,
                    "message": message,
                }

        # =====================================================
        # PROJECT TASKS
        # =====================================================

        if "task" in request_lower or "tasks" in request_lower:
            result = self.project_tool.execute("get_project_tasks", user)

            if result.get("status") == "success":
                data = result.get("data", {})
                tasks = data.get("tasks", [])

                if tasks:
                    details = []

                    for task in tasks:
                        project = task.get("project", "Unknown project")

                        task_name = task.get("task", "Unknown task")

                        status = task.get("status", "Unknown")

                        details.append(f"{task_name} ({project}) - {status}")

                    message = (
                        "Here are the available project tasks: "
                        + "; ".join(details)
                        + "."
                    )
                else:
                    message = "There are currently no project tasks available."

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": data,
                    "message": message,
                }

        # =====================================================
        # PROJECT STATUS SUMMARY
        # =====================================================

        if "status" in request_lower:
            result = self.project_tool.execute("get_project_status", user)

            if result.get("status") == "success":
                data = result.get("data", {})

                active = data.get("active_projects", 0)

                completed = data.get("completed_projects", 0)

                delayed = data.get("delayed_projects", 0)

                message = (
                    f"Currently, there are {active} active projects, "
                    f"{completed} completed projects, and "
                    f"{delayed} delayed projects."
                )

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": data,
                    "message": message,
                }

        # =====================================================
        # ALL PROJECTS
        # =====================================================

        if "project" in request_lower:
            result = self.project_tool.execute("get_projects", user)

            if result.get("status") == "success":
                data = result.get("data", {})
                projects = data.get("projects", [])

                names = [project.get("name", "Unknown project") for project in projects]

                message = (
                    f"There are {len(projects)} projects: " + ", ".join(names) + "."
                )

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": data,
                    "message": message,
                }

        # =====================================================
        # UNSUPPORTED REQUEST
        # =====================================================

        return {
            "agent": self.name,
            "status": "error",
            "data": {},
            "message": (
                "The requested project information " "is not currently supported."
            ),
        }
