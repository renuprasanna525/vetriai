import re

from .base_agent import BaseAgent
from tools.cloud_storage_tool import CloudStorageTool


class CloudStorageAgent(BaseAgent):

    name = "Cloud Storage Agent"

    description = (
        "Handles cloud storage, files, folders, storage usage, "
        "and cloud document questions"
    )

    def __init__(self):
        self.cloud_storage_tool = CloudStorageTool()

    def can_handle(self, request):

        cloud_storage_keywords = [
            "cloud storage",
            "cloud storage summary",
            "storage",
            "storage summary",
            "files",
            "file",
            "folders",
            "folder",
            "documents",
            "document",
            "cloud files",
            "cloud documents",
            "recent files",
            "storage usage",
            "storage used",
        ]

        request_lower = request.lower()

        return any(
            re.search(
                rf"\b{re.escape(keyword)}\b",
                request_lower,
            )
            for keyword in cloud_storage_keywords
        )

    def get_required_permission(self, request):
        return "view_cloud_storage"

    def process(self, request, user, credentials=None):
        request_lower = request.lower()

        # -----------------------------------------
        # Storage Summary
        # -----------------------------------------
        if (
            "storage summary" in request_lower
            or "storage usage" in request_lower
            or "storage used" in request_lower
        ):
            result = self.cloud_storage_tool.execute(
                "get_storage_summary",
                user,
                credentials=credentials,
            )
            if result.get("status") == "success":

                data = result.get("data", {})

                message = (
                    "Cloud Storage Summary:\n"
                    f"Total Files: {data.get('total_files', 0)}\n"
                    f"Total Folders: {data.get('total_folders', 0)}\n"
                    f"Storage Used: {data.get('storage_used', '0 GB')}\n"
                    f"Storage Limit: {data.get('storage_limit', '0 GB')}"
                )

                return {
                    "agent": self.name,
                    "status": "success",
                    "data": data,
                    "message": message,
                }

        # -----------------------------------------
        # Unsupported File / Document Requests
        # -----------------------------------------
        if (
            "file" in request_lower
            or "document" in request_lower
            or "folder" in request_lower
        ):

            return {
                "agent": self.name,
                "status": "unsupported",
                "data": {},
                "message": (
                    "The requested cloud storage file, "
                    "document, or folder information "
                    "is not currently supported."
                ),
            }
        # -----------------------------------------
        # Unsupported Cloud Storage Request
        # -----------------------------------------
        return {
            "agent": self.name,
            "status": "unsupported",
            "data": {},
            "message": (
                "The requested cloud storage information " "is not currently supported."
            ),
        }
