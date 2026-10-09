from google.oauth2.credentials import Credentials

from myapp.google_calendar import get_calendar_service


class CalendarTool:
    """
    Tool for reading Google Calendar events.
    """

    name = "calendar_tool"
    description = "Handles Google Calendar operations."

    def execute(self, action, user=None, credentials=None):

        if not credentials:
            return {
                "status": "error",
                "message": "Google Calendar is not connected.",
            }

        supported_actions = [
            "get_today_events",
            "get_tomorrow_events",
            "get_day_after_tomorrow_events",
            "get_upcoming_events",
        ]

        if action not in supported_actions:
            return {
                "status": "error",
                "message": "Calendar action not supported.",
            }

        try:
            google_credentials = Credentials(
                token=credentials["token"],
                refresh_token=credentials.get("refresh_token"),
                token_uri=credentials["token_uri"],
                client_id=credentials["client_id"],
                client_secret=credentials["client_secret"],
                scopes=credentials["scopes"],
            )

            service = get_calendar_service(google_credentials)

            from datetime import datetime, timedelta
            from zoneinfo import ZoneInfo

            # Use India Standard Time for calendar date calculations.
            india_timezone = ZoneInfo("Asia/Kolkata")
            now = datetime.now(india_timezone)

            # Start of today in India.
            start_of_today = now.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )

            if action == "get_today_events":
                day_offset = 0
            elif action == "get_tomorrow_events":
                day_offset = 1
            elif action == "get_day_after_tomorrow_events":
                day_offset = 2
            else:
                day_offset = None

            if action == "get_upcoming_events":
                start_time = now
                end_time = now + timedelta(days=7)
            else:
                start_time = start_of_today + timedelta(days=day_offset)
                end_time = start_time + timedelta(days=1)

            events_result = (
                service.events()
                .list(
                    calendarId="primary",
                    timeMin=start_time.isoformat(),
                    timeMax=end_time.isoformat(),
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = []

            for event in events_result.get("items", []):
                start = event.get("start", {})

                event_time = start.get(
                    "dateTime",
                    start.get("date"),
                )

                events.append(
                    {
                        "id": event.get("id"),
                        "title": event.get(
                            "summary",
                            "Untitled event",
                        ),
                        "time": event_time,
                        "description": event.get("description"),
                    }
                )

            return {
                "status": "success",
                "events": events,
                "total": len(events),
            }

        except Exception as exc:
            return {
                "status": "error",
                "message": f"Calendar API error: {str(exc)}",
            }
