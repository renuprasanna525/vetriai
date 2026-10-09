from .base_agent import BaseAgent


class MarketingAgent(BaseAgent):

    name = "Marketing Agent"

    description = (
        "Handles marketing, campaigns, leads, and marketing performance questions"
    )

    def can_handle(self, request):

        marketing_keywords = [
            "marketing",
            "campaign",
            "campaigns",
            "advertising",
            "advertisement",
            "promotion",
            "promotions",
            "marketing performance",
            "marketing summary",
            "conversion",
            "conversions",
            "clicks",
            "impressions",
        ]

        request_lower = request.lower()

        return any(keyword in request_lower for keyword in marketing_keywords)

    def get_required_permission(self, request):

        return "view_marketing"

    def process(self, request, user, credentials=None):

        request_lower = request.lower()

        marketing_keywords = [
            "marketing",
            "campaign",
            "campaigns",
            "advertising",
            "advertisement",
            "promotion",
            "promotions",
            "marketing performance",
            "marketing summary",
            "conversion",
            "conversions",
            "clicks",
            "impressions",
        ]

        if not any(keyword in request_lower for keyword in marketing_keywords):
            return {
                "agent": self.name,
                "status": "unsupported",
                "data": {},
                "message": (
                    "The requested marketing information " "is not currently supported."
                ),
            }

        data = {
            "total_campaigns": 12,
            "active_campaigns": 5,
            "total_leads": 350,
            "conversions": 75,
        }

        # =====================================================
        # Focused Responses
        # =====================================================

        # Active campaigns
        if (
            "active campaign" in request_lower
            or "active campaigns" in request_lower
            or "campaigns are active" in request_lower
            or "campaigns active" in request_lower
        ):
            message = f"There are {data['active_campaigns']} active campaigns."

            return {
                "agent": self.name,
                "status": "success",
                "data": {"active_campaigns": data["active_campaigns"]},
                "message": message,
            }

        # Total campaigns
        if (
            "total campaign" in request_lower
            or "total campaigns" in request_lower
            or "how many campaigns" in request_lower
        ):
            message = f"There are {data['total_campaigns']} total campaigns."

            return {
                "agent": self.name,
                "status": "success",
                "data": {"total_campaigns": data["total_campaigns"]},
                "message": message,
            }

        # Conversions
        if "conversion" in request_lower or "conversions" in request_lower:
            message = f"There are {data['conversions']} conversions."

            return {
                "agent": self.name,
                "status": "success",
                "data": {"conversions": data["conversions"]},
                "message": message,
            }

        # Leads
        if "lead" in request_lower or "leads" in request_lower:
            message = f"There are {data['total_leads']} total leads."

            return {
                "agent": self.name,
                "status": "success",
                "data": {"total_leads": data["total_leads"]},
                "message": message,
            }

        # Clicks
        if "click" in request_lower or "clicks" in request_lower:
            return {
                "agent": self.name,
                "status": "error",
                "data": {},
                "message": (
                    "Click data is not currently available " "in the marketing data."
                ),
            }

        # Impressions
        if "impression" in request_lower or "impressions" in request_lower:
            return {
                "agent": self.name,
                "status": "error",
                "data": {},
                "message": (
                    "Impression data is not currently available "
                    "in the marketing data."
                ),
            }

        # =====================================================
        # Marketing Summary
        # =====================================================

        message = (
            "Marketing Summary:\n"
            f"Total Campaigns: {data['total_campaigns']}\n"
            f"Active Campaigns: {data['active_campaigns']}\n"
            f"Total Leads: {data['total_leads']}\n"
            f"Conversions: {data['conversions']}"
        )

        return {
            "agent": self.name,
            "status": "success",
            "data": data,
            "message": message,
        }
