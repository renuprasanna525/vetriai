from django.core.management.base import BaseCommand, CommandError

from tools.reporting_tool import ReportingTool


class Command(BaseCommand):
    help = "Generate a daily, weekly, or monthly business report."

    VALID_PERIODS = {
        "daily": "generate_daily_report",
        "weekly": "generate_weekly_report",
        "monthly": "generate_monthly_report",
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "period",
            choices=self.VALID_PERIODS.keys(),
            help="Report period: daily, weekly, or monthly.",
        )

    def handle(self, *args, **options):
        period = options["period"]
        action = self.VALID_PERIODS[period]

        self.stdout.write(self.style.NOTICE(f"Generating {period} report..."))

        reporting_tool = ReportingTool()

        result = reporting_tool.execute(
            action,
            user=None,
        )

        if result.get("status") != "success":
            message = result.get(
                "message",
                "Unable to generate report.",
            )

            self.stdout.write(self.style.ERROR(message))

            errors = result.get("errors", [])

            for error in errors:
                self.stdout.write(self.style.ERROR(f"- {error}"))

            raise CommandError(f"{period.capitalize()} report generation failed.")

        report = result.get("data", {})

        self.stdout.write(
            self.style.SUCCESS(f"{period.capitalize()} report generated successfully.")
        )

        self.stdout.write(f"Report type: {report.get('report_type', 'unknown')}")

        self.stdout.write(f"Report period: {report.get('report_period', period)}")
