class CRMTool:
    """
    Controlled tool for CRM operations.
    """

    name = "crm_tool"
    description = "Provides controlled access to sales and CRM information."

    def execute(self, action, user=None):

        if action == "get_pending_followups":

            return {
                "status": "success",
                "data": {
                    "pending_followups": [
                        {
                            "customer": "ABC Technologies",
                            "days_pending": 4,
                            "priority": "Medium",
                        },
                        {
                            "customer": "XYZ Solutions",
                            "days_pending": 3,
                            "priority": "Medium",
                        },
                        {
                            "customer": "Global Systems",
                            "days_pending": 7,
                            "priority": "High",
                        },
                    ]
                },
            }

        if action == "get_leads":

            return {
                "status": "success",
                "data": {
                    "total_leads": 12,
                    "new_leads": 5,
                },
            }

        if action == "get_customers":

            return {
                "status": "success",
                "data": {
                    "customers": [
                        {
                            "name": "ABC Technologies",
                            "email": "contact@abc-technologies.com",
                            "status": "Active",
                        },
                        {
                            "name": "XYZ Solutions",
                            "email": "contact@xyz-solutions.com",
                            "status": "Active",
                        },
                        {
                            "name": "Global Systems",
                            "email": "contact@global-systems.com",
                            "status": "Active",
                        },
                    ],
                    "total_customers": 3,
                },
            }

        if action == "get_orders":

            return {
                "status": "success",
                "data": {
                    "orders": [
                        {
                            "order_id": "ORD-1001",
                            "customer": "ABC Technologies",
                            "amount": 25000,
                            "status": "Pending",
                        },
                        {
                            "order_id": "ORD-1002",
                            "customer": "XYZ Solutions",
                            "amount": 18000,
                            "status": "Completed",
                        },
                        {
                            "order_id": "ORD-1003",
                            "customer": "Global Systems",
                            "amount": 32000,
                            "status": "Pending",
                        },
                    ],
                    "total_orders": 3,
                    "pending_orders": 2,
                },
            }

        if action == "get_pending_orders":

            return {
                "status": "success",
                "data": {
                    "orders": [
                        {
                            "order_id": "ORD-1001",
                            "customer": "ABC Technologies",
                            "amount": 25000,
                            "status": "Pending",
                        },
                        {
                            "order_id": "ORD-1003",
                            "customer": "Global Systems",
                            "amount": 32000,
                            "status": "Pending",
                        },
                    ],
                    "pending_orders": 2,
                },
            }

        return {
            "status": "error",
            "message": "CRM action not supported.",
        }
