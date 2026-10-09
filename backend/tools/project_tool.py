from datetime import date


class ProjectTool:
    """
    Controlled tool for project management operations.
    """

    name = "project_tool"
    description = "Provides controlled access to project information."

    def execute(self, action, user=None):

        # -------------------------------------------------
        # Employee-specific project data
        # -------------------------------------------------
        employee_projects = [
            {
                "name": "Vetri E-Commerce",
                "status": "Delayed",
                "progress": 75,
                "risk": "High",
            }
        ]

        employee_tasks = [
            {
                "project": "Vetri E-Commerce",
                "task": "Payment Integration",
                "status": "Pending",
                "due_date": "2026-09-04",
            }
        ]

        # -----------------------------------------
        # All Projects
        # -----------------------------------------
        if action == "get_projects":

            if user and not user.is_staff and not user.is_superuser:
                return {
                    "status": "success",
                    "data": {
                        "projects": employee_projects,
                        "total_projects": len(employee_projects),
                    },
                }

            return {
                "status": "success",
                "data": {
                    "projects": [
                        {
                            "name": "Vetri E-Commerce",
                            "status": "Delayed",
                            "progress": 75,
                            "risk": "High",
                        },
                        {
                            "name": "AI Dashboard",
                            "status": "Delayed",
                            "progress": 80,
                            "risk": "Medium",
                        },
                        {
                            "name": "CRM System",
                            "status": "Active",
                            "progress": 60,
                            "risk": "Low",
                        },
                        {
                            "name": "HR Management System",
                            "status": "Completed",
                            "progress": 100,
                            "risk": "Low",
                        },
                    ],
                    "total_projects": 4,
                },
            }

        # -----------------------------------------
        # Delayed Projects
        # -----------------------------------------
        if action == "get_delayed_projects":

            return {
                "status": "success",
                "data": {
                    "delayed_projects": [
                        {
                            "name": "Vetri E-Commerce",
                            "delay_days": 3,
                        },
                        {
                            "name": "AI Dashboard",
                            "delay_days": 2,
                        },
                    ],
                    "total_delayed": 2,
                },
            }

        # -----------------------------------------
        # Project Status
        # -----------------------------------------
        if action == "get_project_status":

            return {
                "status": "success",
                "data": {
                    "active_projects": 8,
                    "completed_projects": 15,
                    "delayed_projects": 2,
                },
            }

        # -----------------------------------------
        # Project Deadlines
        # -----------------------------------------
        if action == "get_project_deadlines":

            return {
                "status": "success",
                "data": {
                    "deadlines": [
                        {
                            "project": "Vetri E-Commerce",
                            "deadline": "2026-09-05",
                        },
                        {
                            "project": "AI Dashboard",
                            "deadline": "2026-09-08",
                        },
                        {
                            "project": "CRM System",
                            "deadline": "2026-09-15",
                        },
                    ]
                },
            }

        # -----------------------------------------
        # Project Tasks
        # -----------------------------------------
        if action == "get_project_tasks":

            if user and not user.is_staff and not user.is_superuser:
                return {
                    "status": "success",
                    "data": {
                        "tasks": employee_tasks,
                    },
                }

            return {
                "status": "success",
                "data": {
                    "tasks": [
                        {
                            "project": "Vetri E-Commerce",
                            "task": "Payment Integration",
                            "status": "Pending",
                            "due_date": "2026-09-04",
                        },
                        {
                            "project": "AI Dashboard",
                            "task": "Dashboard UI",
                            "status": "In Progress",
                            "due_date": "2026-10-07",
                        },
                        {
                            "project": "CRM System",
                            "task": "Customer Module",
                            "status": "Completed",
                            "due_date": "2026-09-15",
                        },
                    ],
                },
            }

        # -----------------------------------------
        # Overdue Tasks
        # -----------------------------------------
        if action == "get_overdue_tasks":

            today = date.today()

            all_tasks = [
                {
                    "project": "Vetri E-Commerce",
                    "task": "Payment Integration",
                    "status": "Pending",
                    "due_date": "2026-09-04",
                },
                {
                    "project": "AI Dashboard",
                    "task": "Dashboard UI",
                    "status": "In Progress",
                    "due_date": "2026-10-07",
                },
                {
                    "project": "CRM System",
                    "task": "Customer Module",
                    "status": "Completed",
                    "due_date": "2026-09-15",
                },
            ]

            overdue_tasks = []

            for task in all_tasks:

                if task["status"].lower() == "completed":
                    continue

                due_date = date.fromisoformat(task["due_date"])

                if due_date < today:
                    overdue_tasks.append(task)

            return {
                "status": "success",
                "data": {
                    "overdue_tasks": overdue_tasks,
                    "total_overdue": len(overdue_tasks),
                },
            }

        # -----------------------------------------
        # Unsupported Action
        # -----------------------------------------
        return {
            "status": "error",
            "message": "Project action not supported.",
        }
