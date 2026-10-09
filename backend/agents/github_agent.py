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
            "repository",
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
        # Unsupported External GitHub Requests
        # -----------------------------------------

        unsupported_github_keywords = [
            "repository",
            "repositories",
            "repo",
            "repos",
            "pull request",
            "pull requests",
            "issue",
            "issues",
        ]
        if any(keyword in request_lower for keyword in unsupported_github_keywords):
            return {
                "agent": self.name,
                "status": "unsupported",
                "data": {},
                "message": (
                    "The requested GitHub repository, "
                    "issue, or pull request information "
                    "is not currently supported."
                ),
            }

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
            # Detect requested GitHub categories
            # -----------------------------------------

            wants_issues = "issue" in request_lower or "issues" in request_lower

            wants_pull_requests = (
                "pull request" in request_lower
                or "pull requests" in request_lower
                or " pr " in f" {request_lower} "
            )

            wants_repositories = (
                "repository" in request_lower
                or "repositories" in request_lower
                or "repo" in request_lower
                or "repos" in request_lower
            )

            # -----------------------------------------
            # Multiple GitHub categories
            # -----------------------------------------

            requested_categories = sum(
                [
                    wants_repositories,
                    wants_issues,
                    wants_pull_requests,
                ]
            )
            print(
                "GITHUB CATEGORY DEBUG:",
                {
                    "request": request_lower,
                    "wants_repositories": wants_repositories,
                    "wants_issues": wants_issues,
                    "wants_pull_requests": wants_pull_requests,
                    "requested_categories": requested_categories,
                },
            )

            if requested_categories > 1:

                parts = []
                response_data = {}

                if wants_repositories:
                    parts.append(f"GitHub repositories: {repositories}")
                    response_data["repositories"] = repositories

                if wants_issues:
                    parts.append(f"Open GitHub issues: {open_issues}")
                    response_data["open_issues"] = open_issues

                if wants_pull_requests:
                    parts.append(f"Open GitHub pull requests: " f"{open_pull_requests}")
                    response_data["open_pull_requests"] = open_pull_requests

                message = "\n".join(parts)

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": response_data,
                    "message": message,
                }

            # -----------------------------------------
            # Focused: Open Issues
            # -----------------------------------------

            if wants_issues:

                message = f"There are {open_issues} " f"open GitHub issues."

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": {"open_issues": open_issues},
                    "message": message,
                }

            # -----------------------------------------
            # Focused: Pull Requests
            # -----------------------------------------

            if wants_pull_requests:

                message = (
                    f"There are {open_pull_requests} " f"open GitHub pull requests."
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

            if wants_repositories:

                message = f"There are {repositories} " f"GitHub repositories."

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
            # Unsupported GitHub Summary / Status
            # -----------------------------------------

            if (
                "github" in request_lower
                or "git status" in request_lower
                or "repository status" in request_lower
                or "status" in request_lower
            ):

                return {
                    "agent": self.name,
                    "status": "unsupported",
                    "data": {},
                    "message": (
                        "GitHub repository, issue, and pull request "
                        "information is not currently supported."
                    ),
                }

        # -----------------------------------------
        # Unsupported Request
        # -----------------------------------------

        return {
            "agent": self.name,
            "status": "unsupported",
            "data": {},
            "message": (
                "The requested GitHub or Cloud "
                "information is not currently supported."
            ),
        }
