class PermissionEngine:
    """
    Handles role-based permissions for the
    Vetri AI Multi-Agent system.
    """

    ROLE_PERMISSIONS = {
        "employee": {
            "view_own_profile",
            "view_own_tasks",
            "view_own_projects",
        },
        "sales": {
            "view_sales",
            "view_leads",
            "view_customers",
            "view_orders",
        },
        "hr": {
            "view_employees",
            "view_attendance",
            "view_leave",
            "view_employee_salary",
        },
        "manager": {
            "view_sales",
            "view_leads",
            "view_customers",
            "view_orders",
            "view_projects",
            "view_project_status",
            "view_team",
            "view_github",
            "view_finance",
            "view_marketing",
            "view_developer",
            "view_qa",
            "view_operations",
            "view_customer_support",
            "view_cloud_storage",
        },
        "admin": {
            "view_sales",
            "view_leads",
            "view_customers",
            "view_orders",
            "view_crm",
            "view_employees",
            "view_attendance",
            "view_leave",
            "view_employee_salary",
            "view_projects",
            "view_project_status",
            "view_team",
            "view_reports",
            "view_github",
            "view_finance",
            "view_marketing",
            "view_developer",
            "view_qa",
            "view_operations",
            "view_own_profile",
            "view_own_tasks",
            "view_own_projects",
            "view_customer_support",
            "view_cloud_storage",
        },
    }

    def has_permission(self, role, permission):
        """
        Check whether a role has a specific permission.
        """

        permissions = self.ROLE_PERMISSIONS.get(role.lower(), set())

        return permission in permissions

    def check_permission(self, role, permission):
        """
        Return a structured permission result.
        """

        allowed = self.has_permission(role, permission)

        if allowed:
            return {
                "allowed": True,
                "role": role,
                "permission": permission,
                "message": "Permission granted.",
            }

        return {
            "allowed": False,
            "role": role,
            "permission": permission,
            "message": "Permission denied.",
        }
