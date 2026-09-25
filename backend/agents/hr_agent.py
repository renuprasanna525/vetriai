from .base_agent import BaseAgent
from tools.database_tool import DatabaseTool
from knowledge_base.rag import RAGSystem


class HRAgent(BaseAgent):

    name = "HR Agent"

    description = "Handles employee and HR-related questions"

    def __init__(self):
        self.database_tool = DatabaseTool()
        self.rag = RAGSystem()

    def can_handle(self, request):

        hr_keywords = [
            "hr",
            "employee",
            "employees",
            "staff",
            "profile",
            "my profile",
            "own profile",
            "leave",
            "on leave",
            "attendance",
            "absent",
            "team member",
            "team members",
            "work from home",
            "wfh",
            "salary",
            "salaries",
            "pay",
            "payment",
        ]

        request_lower = request.lower()

        return any(keyword in request_lower for keyword in hr_keywords)

    def get_required_permission(self, request):

        request_lower = request.lower()

        # -----------------------------------------
        # Own Profile
        # -----------------------------------------
        if "profile" in request_lower and (
            "my" in request_lower or "own" in request_lower
        ):
            return "view_own_profile"

        # -----------------------------------------
        # Salary Permission
        # -----------------------------------------
        if (
            "salary" in request_lower
            or "salaries" in request_lower
            or "pay" in request_lower
            or "payment" in request_lower
        ):
            return "view_employee_salary"

        # -----------------------------------------
        # Attendance Permission
        # -----------------------------------------
        if "attendance" in request_lower or "absent" in request_lower:
            return "view_attendance"

        # -----------------------------------------
        # Leave Permission
        # -----------------------------------------
        if "leave" in request_lower:
            return "view_leave"

        # -----------------------------------------
        # Employee Permission
        # -----------------------------------------
        if (
            "employee" in request_lower
            or "employees" in request_lower
            or "staff" in request_lower
            or "team member" in request_lower
            or "team members" in request_lower
        ):
            return "view_employees"

        return "view_employees"

    def process(self, request, user, credentials=None):

        print("HR REQUEST:", request)
        print("HR PERMISSION:", self.get_required_permission(request))

        request_lower = request.lower()

        # ==========================================
        # Knowledge Base / Policy Questions
        # ==========================================

        knowledge_keywords = [
            "policy",
            "how can",
            "how do",
            "how many days",
            "who approves",
            "work from home",
            "wfh",
            "planned leave",
            "emergency leave",
            "reporting manager",
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
        # Own Profile
        # ==========================================

        if "profile" in request_lower and (
            "my" in request_lower or "own" in request_lower
        ):

            result = self.database_tool.execute(
                "get_own_profile",
                user,
            )

            if result.get("status") == "success":

                data = result.get("data", {})
                profile = data.get("profile", {})

                message = (
                    f"My Profile:\n"
                    f"Username: {profile.get('username', '')}\n"
                    f"Email: {profile.get('email', '')}\n"
                    f"Role: {profile.get('role', '')}\n"
                    f"Status: {profile.get('status', '')}"
                )

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": data,
                    "message": message,
                }

        # ==========================================
        # Employees Currently on Leave
        # ==========================================

        if "leave" in request_lower:

            result = self.database_tool.execute(
                "get_employees_on_leave",
                user,
            )

            if result.get("status") == "success":

                data = result.get("data", {})
                employees = data.get("employees_on_leave", [])

                if not employees:
                    message = "There are no employees currently on leave."

                else:
                    names = [employee["name"] for employee in employees]

                    message = (
                        f"There are {len(employees)} employees "
                        f"currently on leave: " + ", ".join(names) + "."
                    )

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": data,
                    "message": message,
                }

        # ==========================================
        # Attendance
        # ==========================================

        if "attendance" in request_lower or "absent" in request_lower:

            result = self.database_tool.execute(
                "get_attendance",
                user,
            )

            if result.get("status") == "success":

                data = result.get("data", {})

                message = (
                    f"Today's attendance: "
                    f"{data.get('present', 0)} present, "
                    f"{data.get('absent', 0)} absent, "
                    f"{data.get('on_leave', 0)} on leave."
                )

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": data,
                    "message": message,
                }

        # ==========================================
        # Salary
        # ==========================================

        if (
            "salary" in request_lower
            or "salaries" in request_lower
            or "pay" in request_lower
            or "payment" in request_lower
        ):

            result = self.database_tool.execute(
                "get_employee_salary",
                user,
            )

            if result.get("status") == "success":

                data = result.get("data", {})
                salaries = data.get("salary_information", [])

                if not salaries:
                    message = "No salary information is currently available."

                else:
                    salary_lines = []

                    for employee in salaries:

                        salary_lines.append(
                            f"{employee['name']} - "
                            f"₹{employee['monthly_salary']} "
                            f"per month"
                        )

                    message = "Employee salary information:\n" + "\n".join(salary_lines)

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": data,
                    "message": message,
                }

        # ==========================================
        # Employees
        # ==========================================

        if (
            "employee" in request_lower
            or "employees" in request_lower
            or "staff" in request_lower
            or "team member" in request_lower
            or "team members" in request_lower
        ):

            result = self.database_tool.execute(
                "get_employees",
                user,
            )

            if result.get("status") == "success":

                data = result.get("data", {})
                employees = data.get("employees", [])

                if not employees:

                    message = "There are no employees available."

                else:

                    employee_names = [employee["name"] for employee in employees]

                    message = (
                        f"There are {len(employees)} employees: "
                        + ", ".join(employee_names)
                        + "."
                    )

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": data,
                    "message": message,
                }

        # ==========================================
        # HR Status / Summary
        # ==========================================

        hr_status_keywords = [
            "hr status",
            "hr summary",
            "current hr status",
            "current hr summary",
            "hr overview",
            "employee status",
            "employee summary",
            "employee overview",
        ]

        if any(keyword in request_lower for keyword in hr_status_keywords):

            result = self.database_tool.execute(
                "get_employees_on_leave",
                user,
            )

            if result.get("status") == "success":

                data = result.get("data", {})
                employees = data.get("employees_on_leave", [])

                if employees:
                    names = [employee["name"] for employee in employees]

                    message = (
                        "HR Summary:\n"
                        f"Employees currently on leave: {len(employees)}\n"
                        f"Employees on leave: {', '.join(names)}"
                    )

                else:
                    message = (
                        "HR Summary:\n" "There are currently no employees on leave."
                    )

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": data,
                    "message": message,
                }

        # ==========================================
        # Unsupported HR Request
        # ==========================================

        return {
            "agent": self.name,
            "status": "error",
            "data": {},
            "message": ("The requested HR information " "is not currently supported."),
        }
