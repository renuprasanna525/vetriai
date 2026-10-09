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
            "team",
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
        # Team Permission
        # -----------------------------------------
        if "team" in request_lower:
            return "view_team"

        # -----------------------------------------
        # Employee Permission
        # -----------------------------------------
        if (
            "employee" in request_lower
            or "employees" in request_lower
            or "staff" in request_lower
            or "team member" in request_lower
            or "team members" in request_lower
            or "team" in request_lower
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
        # Unsupported HR Requests
        # ==========================================

        unsupported_keywords = [
            "performance review",
            "performance reviews",
            "performance appraisal",
            "performance appraisals",
            "appraisal",
            "appraisals",
            "employee rating",
            "employee ratings",
            "performance rating",
            "performance ratings",
            "performance score",
            "performance scores",
            "employee kpi",
            "employee kpis",
        ]
        if any(keyword in request_lower for keyword in unsupported_keywords):
            return {
                "agent": self.name,
                "status": "unsupported",
                "data": {},
                "message": (
                    "The requested HR information " "is not currently supported."
                ),
            }
        # ==========================================
        # Specific Employee Information
        # ==========================================

        result = self.database_tool.execute(
            "get_employees",
            user,
        )

        if result.get("status") == "success":

            data = result.get("data", {})
            employees = data.get("employees", [])

            # Find employee names dynamically from the database.
            # This avoids hardcoding names such as Priya or Divya.
            matching_employees = [
                employee
                for employee in employees
                if employee.get("name")
                and employee.get("name", "").lower() in request_lower
            ]

            if len(matching_employees) == 1 and not any(
                keyword in request_lower
                for keyword in [
                    "leave",
                    "salary",
                    "salaries",
                    "pay",
                    "payment",
                    "attendance",
                    "absent",
                ]
            ):

                matching_employee = matching_employees[0]

                name = matching_employee.get(
                    "name",
                    "Not available",
                )

                department = matching_employee.get(
                    "department",
                    "Not available",
                )

                role = matching_employee.get("role")
                status = matching_employee.get("status")

                message_parts = [f"{name} is in the {department} department."]

                if role:
                    message_parts.append(f"Role: {role}.")

                if status:
                    message_parts.append(f"Status: {status}.")

                message = " ".join(message_parts)

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": {
                        "employee": matching_employee,
                        "query_scope": "employee_specific",
                    },
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
        # Combined Attendance + Leave Summary
        # ==========================================

        if "attendance" in request_lower and "leave" in request_lower:

            attendance_result = self.database_tool.execute(
                "get_attendance",
                user,
            )

            leave_result = self.database_tool.execute(
                "get_employees_on_leave",
                user,
            )

            attendance_data = {}
            leave_data = {}

            if attendance_result.get("status") == "success":
                attendance_data = attendance_result.get("data", {})

            if leave_result.get("status") == "success":
                leave_data = leave_result.get("data", {})

            attendance_date = (
                attendance_data.get("date")
                or attendance_data.get("attendance_date")
                or attendance_data.get("record_date")
                or "Not available"
            )

            employees_on_leave = leave_data.get("employees_on_leave", [])

            leave_details = []

            for employee in employees_on_leave:
                name = employee.get("name", "Unknown")
                department = employee.get(
                    "department",
                    "Not available",
                )
                leave_type = employee.get(
                    "leave_type",
                    "Not available",
                )
                leave_date = employee.get(
                    "date",
                    "Not available",
                )

                detail = (
                    f"{name} - {department} department, "
                    f"{leave_type}, recorded date: {leave_date}"
                )

                approval_status = employee.get("approval_status")

                if approval_status:
                    detail += f", approval status: " f"{approval_status}"
                else:
                    detail += (
                        ", approval status: not available " "in the current HR data"
                    )

                detail += (
                    ". The record alone does not establish "
                    "whether the employee is currently on leave."
                )

                leave_details.append(detail)

            message = (
                "Employee Attendance and Leave Summary:\n\n"
                f"Attendance recorded for {attendance_date}:\n"
                f"Total employees: "
                f"{attendance_data.get('total_employees', 'Not available')}\n"
                f"Present: "
                f"{attendance_data.get('present', 'Not available')}\n"
                f"Absent: "
                f"{attendance_data.get('absent', 'Not available')}\n"
                f"On leave: "
                f"{attendance_data.get('on_leave', 'Not available')}\n\n"
                "Leave records:\n"
            )

            if leave_details:
                message += "\n".join(leave_details)
            else:
                message += (
                    "No employee leave records are available " "in the current HR data."
                )

            message += (
                "\n\nAttendance figures describe the stored "
                "attendance record and do not confirm today's "
                "attendance unless the record is dated today."
            )

            return {
                "agent": self.name,
                "status": "success",
                "data": {
                    "attendance": attendance_data,
                    "leave": leave_data,
                },
                "message": message,
            }

        # ==========================================
        # Employee Leave Information
        # ==========================================

        if "leave" in request_lower:

            result = self.database_tool.execute(
                "get_employees_on_leave",
                user,
            )

            if result.get("status") == "success":

                data = result.get("data", {})
                all_employees = data.get("employees_on_leave", [])
                total_recorded = len(all_employees)

                employees = all_employees.copy()

                # Identify the employee mentioned in the request.
                # This supports both direct questions and contextual follow-ups.
                employee_names = [
                    employee.get("name", "")
                    for employee in employees
                    if employee.get("name")
                ]

                # Prefer the explicitly identified employee in contextual requests.
                specific_employee = None
                context_marker = "specifically for the employee '"
                if context_marker in request_lower:
                    remaining = request_lower.split(context_marker, 1)[1]
                    specific_employee = remaining.split("'", 1)[0].strip()

                if specific_employee:
                    employees = [
                        employee
                        for employee in employees
                        if employee.get("name", "").lower() == specific_employee
                    ]
                else:
                    matched_names = [
                        name for name in employee_names if name.lower() in request_lower
                    ]
                    if matched_names:
                        employees = [
                            employee
                            for employee in employees
                            if employee.get("name") in matched_names
                        ]

                # Update the returned data to reflect the filtered results.
                data["employees_on_leave"] = employees
                data["total_on_leave"] = total_recorded
                data["total_recorded_leave_records"] = total_recorded
                data["matching_leave_records"] = len(employees)
                data["query_scope"] = (
                    "employee_specific"
                    if specific_employee or matched_names
                    else "all_leave_records"
                )

                if not employees:
                    message = (
                        "No matching employee leave records are "
                        "available in the current HR data. "
                        "This does not confirm whether an employee "
                        "is currently on leave."
                    )
                else:
                    leave_details = []

                    for employee in employees:
                        name = employee.get("name", "Unknown")
                        department = employee.get("department", "Not available")
                        leave_type = employee.get("leave_type", "Not available")
                        leave_date = employee.get("date", "Not available")

                        detail = (
                            f"{name} - {department} department, "
                            f"{leave_type}, recorded date: {leave_date}"
                        )
                        approval_status = employee.get("approval_status")
                        if approval_status:
                            detail += f", approval status: {approval_status}"
                        else:
                            detail += (
                                ", approval status: not available "
                                "in the current HR data"
                            )
                        detail += (
                            ". The record alone does not establish "
                            "whether the employee is currently on leave."
                        )
                        leave_details.append(detail)

                    message = "Available employee leave records:\n" + "\n".join(
                        leave_details
                    )
                # Add clarification for employee-specific results.
                if specific_employee or matched_names:
                    message += (
                        "\nThis response contains only the matching employee's "
                        "leave record. Other employees may also have leave records. "
                        "The available data does not confirm who is currently on leave."
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

                attendance_date = (
                    data.get("date")
                    or data.get("attendance_date")
                    or data.get("record_date")
                    or "Not available"
                )
                if attendance_date:
                    date_label = f"for {attendance_date}"
                else:
                    date_label = "(date not available in the record)"
                message = (
                    f"Attendance summary recorded for {attendance_date}:\n"
                    f"Total employees: {data.get('total_employees', 'Not available')}\n"
                    f"Present: {data.get('present', 'Not available')}\n"
                    f"Absent: {data.get('absent', 'Not available')}\n"
                    f"On leave: {data.get('on_leave', 'Not available')}\n\n"
                    "These figures describe the stored attendance record "
                    "and do not confirm today's attendance unless the "
                    "record is dated today. Employee profile status "
                    "such as Active or On Leave is not proof of attendance."
                )

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
            or "team" in request_lower
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
                    leave_details = []
                    for employee in employees:
                        name = employee.get("name", "Unknown")
                        department = employee.get("department", "Not available")
                        leave_type = employee.get("leave_type", "Not available")
                        leave_date = employee.get("date", "Date not available")

                        detail = (
                            f"{name} - {department} department, "
                            f"{leave_type}, recorded date: {leave_date}"
                        )

                        approval_status = employee.get("approval_status")

                        if approval_status:
                            detail += f", approval status: {approval_status}"
                        else:
                            detail += ", approval status not available"

                        leave_details.append(detail)

                    message = (
                        "HR Summary:\n"
                        f"Employees with leave records: {len(employees)}\n"
                        + "\n".join(leave_details)
                        + "\n\nThese are stored leave records. "
                        "They do not confirm who is currently on leave "
                        "or whether a leave request has been approved."
                    )
                else:
                    message = (
                        "HR Summary:\n"
                        "No employee leave records are available "
                        "in the current HR data. This does not confirm "
                        "that no employees are currently on leave."
                    )

                data["total_on_leave"] = len(employees)
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
            "status": "unsupported",
            "data": {},
            "message": ("The requested HR information " "is not currently supported."),
        }
