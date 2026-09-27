from .base_agent import BaseAgent
from tools.github_tool import GitHubTool


class GitHubAgent(BaseAgent):

    name = "GitHub Agent"

    description = (
        "Handles GitHub repositories, issues, pull requests, "
        "Git status, and cloud development questions"
    )

    def __init__(self):
        self.github_tool = GitHubTool()

    def can_handle(self, request):

        github_keywords = [
            "github",
            "git",
            "repository",
            "repositories",
            "repo",
            "repos",
            "pull request",
            "pull requests",
            "pr",
            "issue",
            "issues",
            "git status",
            "repository status",
            "cloud",
            "cloud deployment",
            "deployment",
            "deploy",
        ]

        request_lower = request.lower()

        return any(keyword in request_lower for keyword in github_keywords)

    def get_required_permission(self, request):

        return "view_github"

    def process(self, request, user, credentials=None):

        request_lower = request.lower()

        # -----------------------------------------
        # Get GitHub Repository Data
        # -----------------------------------------

        result = self.github_tool.execute(
            "get_repository_status",
            user,
        )

        if result.get("status") == "success":

            data = result.get("data", {})

            repositories = data.get("repositories", 0)
            open_issues = data.get("open_issues", 0)
            open_pull_requests = data.get(
                "open_pull_requests",
                0,
            )

            # -----------------------------------------
            # Focused: Open Issues
            # -----------------------------------------

            if "issue" in request_lower or "issues" in request_lower:
                message = f"There are {open_issues} open GitHub issues."

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": {"open_issues": open_issues},
                    "message": message,
                }

            # -----------------------------------------
            # Focused: Pull Requests
            # -----------------------------------------

            if (
                "pull request" in request_lower
                or "pull requests" in request_lower
                or " pr" in f" {request_lower}"
            ):
                message = (
                    f"There are {open_pull_requests} open " f"GitHub pull requests."
                )

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": {"open_pull_requests": open_pull_requests},
                    "message": message,
                }

            # -----------------------------------------
            # Focused: Repository Count
            # -----------------------------------------

            if (
                "repository" in request_lower
                or "repositories" in request_lower
                or "repo" in request_lower
                or "repos" in request_lower
                or "how many repositories" in request_lower
            ):
                message = f"There are {repositories} GitHub repositories."

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": {"repositories": repositories},
                    "message": message,
                }

            # -----------------------------------------
            # Cloud / Deployment Information
            # -----------------------------------------

            if (
                "cloud" in request_lower
                or "deployment" in request_lower
                or "deploy" in request_lower
            ):
                message = (
                    "Cloud deployment information is "
                    "currently available as an MVP feature."
                )

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": {"message": message},
                    "message": message,
                }

            # -----------------------------------------
            # GitHub Repository Summary
            # -----------------------------------------

            if (
                "github" in request_lower
                or "git status" in request_lower
                or "repository status" in request_lower
                or "status" in request_lower
            ):
                message = (
                    "GitHub Repository Status:\n"
                    f"Repositories: {repositories}\n"
                    f"Open Issues: {open_issues}\n"
                    f"Open Pull Requests: "
                    f"{open_pull_requests}"
                )

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": data,
                    "message": message,
                }

        # -----------------------------------------
        # Unsupported Request
        # -----------------------------------------

        return {
            "agent": self.name,
            "status": "error",
            "data": {},
            "message": (
                "The requested GitHub or Cloud "
                "information is not currently supported."
            ),
        }
