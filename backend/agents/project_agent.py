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

    def get_required_permission(self, request, user=None):
        print("PROJECT AGENT PERMISSION REQUEST:", repr(request))
        request_lower = request.lower()
        employee_role = False

        if user is not None:
            try:
                employee_role = getattr(user.profile, "role", "").lower() == "employee"
            except Exception:
                employee_role = False
        print(
            "PROJECT AGENT EMPLOYEE ROLE CHECK:",
            repr(getattr(user.profile, "role", None)),
            employee_role,
        )

        own_data_phrases = [
            "my",
            "own",
            "assigned to me",
            "assigned for me",
            "for me",
            "to me",
            "am i working on",
            "i am working on",
            "i'm working on",
            "i work on",
            "am i assigned",
            "i am assigned",
            "i'm assigned",
        ]

        is_own_request = any(phrase in request_lower for phrase in own_data_phrases)
        project_names = [
            "vetri e-commerce",
            "ai dashboard",
            "crm system",
            "hr management system",
        ]
        is_project_entity_request = any(
            project_name in request_lower for project_name in project_names
        )
        print(
            "PROJECT PERMISSION STATE:",
            repr(request_lower),
            "contains_project=",
            "project" in request_lower,
            "is_own_request=",
            is_own_request,
            "employee_role=",
            employee_role,
        )
        # -------------------------------------------------
        # IMPORTANT:
        # Check explicit project requests BEFORE task
        # requests because project prompts may also contain
        # the word "task".
        # -------------------------------------------------
        if "project" in request_lower or is_project_entity_request:
            print(
                "PROJECT PERMISSION BRANCH:",
                repr(request_lower),
                "employee_role=",
                employee_role,
            )

            if is_own_request:
                return "view_own_projects"
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
            if employee_role:
                return "view_own_projects"

            return "view_projects"

        # -------------------------------------------------
        # Task requests
        # -------------------------------------------------

        if "task" in request_lower:

            if is_own_request:
                return "view_own_tasks"

            return "view_projects"

        # -------------------------------------------------
        # Project status requests without explicit project
        # -------------------------------------------------
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
        # EMPLOYEE'S OWN PROJECTS
        # =====================================================

        own_project_phrases = [
            "my projects",
            "my project",
            "projects assigned to me",
            "projects assigned for me",
            "projects for me",
            "projects i'm working on",
            "projects i am working on",
            "projects i'm working on",
            "which projects am i working on",
            "what projects am i working on",
            "currently working on",
            "currently assigned",
        ]

        is_own_project_request = any(
            phrase in request_lower for phrase in own_project_phrases
        )

        if is_own_project_request:
            result = self.project_tool.execute("get_projects", user)

            if result.get("status") == "success":
                data = result.get("data", {})
                projects = data.get("projects", [])

            if projects:
                details = []

                for project in projects:
                    name = project.get("name", "Unknown project")
                    status = project.get("status", "Unknown")
                    progress = project.get("progress", "Unknown")

                    details.append(f"{name} ({status}, {progress}% progress)")

                message = (
                    "These are the projects currently assigned to you: "
                    + "; ".join(details)
                    + "."
                )
            else:
                message = "You currently do not have any projects assigned to you."

            return {
                "agent": self.name,
                "status": "success",
                "data": data,
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
            "status": "unsupported",
            "data": {},
            "message": (
                "The requested project information " "is not currently supported."
            ),
        }
