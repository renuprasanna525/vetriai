from .base_agent import BaseAgent
from tools.calendar_tool import CalendarTool


class CalendarAgent(BaseAgent):

    name = "Calendar Agent"

    description = "Handles Google Calendar events and calendar-related questions"

    def __init__(self):
        self.calendar_tool = CalendarTool()

    def can_handle(self, request):

        calendar_keywords = [
            "calendar",
            "event",
            "events",
            "meeting",
            "meetings",
            "schedule",
            "scheduled",
            "appointment",
            "appointments",
        ]

        request_lower = request.lower()

        return any(keyword in request_lower for keyword in calendar_keywords)

    def get_required_permission(self, request):

        return "view_calendar"

    def process(self, request, user, credentials=None):

        request_lower = request.lower()

        # Tomorrow's events
        if (
            "tomorrow" in request_lower
            or "tomorrow's" in request_lower
            or "tomorrows" in request_lower
        ):

            action = "get_tomorrow_events"
            day_label = "tomorrow"

        # Today's events
        elif (
            "today" in request_lower
            or "today's" in request_lower
            or "todays" in request_lower
        ):

            action = "get_today_events"
            day_label = "today"

        else:

            return {
                "agent": self.name,
                "status": "error",
                "data": {},
                "message": (
                    "I can currently help you with "
                    "today's or tomorrow's Google Calendar events."
                ),
            }

        result = self.calendar_tool.execute(
            action,
            user,
            credentials=credentials,
        )

        if result.get("status") == "success":

            events = result.get("events", [])

            if not events:

                message = f"You have no calendar events scheduled for {day_label}."

            else:

                event_lines = []

                for event in events:

                    event_lines.append(f"{event['title']} at {event['time']}")

                message = (
                    f"Here are your Google Calendar events for {day_label}:\n"
                    + "\n".join(event_lines)
                )

            return {
                "agent": self.name,
                "status": "success",
                "data": result,
                "message": message,
            }

        return {
            "agent": self.name,
            "status": "error",
            "data": result,
            "message": result.get(
                "message",
                "Unable to retrieve Google Calendar events.",
            ),
        }
