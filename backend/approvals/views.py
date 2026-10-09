from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from permissions.permission_engine import PermissionEngine
from tools.registry import ToolRegistry

# Single shared registry instance.
# This preserves pending_actions between API requests
# while the Django process is running.
tool_registry = ToolRegistry()


def get_user_role(user):
    """Return the user's role using the existing project convention."""
    if user.is_superuser:
        return "admin"

    return getattr(
        getattr(user, "profile", None),
        "role",
        None,
    )


def require_approval_permission(user, permission):
    """Enforce an approval permission through PermissionEngine."""
    role = get_user_role(user)
    permission_engine = PermissionEngine()

    if not permission_engine.has_permission(role, permission):
        raise PermissionDenied(
            "You do not have permission to perform this approval operation."
        )


def is_action_requester(action, user):
    """Check whether the authenticated user created the action."""
    return (
        action.get("requester_id") is not None and action.get("requester_id") == user.pk
    )


class ApprovalListView(APIView):
    """List approval actions for managers and administrators."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        require_approval_permission(request.user, "view_approvals")

        actions = list(tool_registry.approval_workflow.pending_actions.values())

        status_filter = request.query_params.get("status")

        if status_filter:
            actions = [
                action for action in actions if action.get("status") == status_filter
            ]

        return Response(
            {
                "status": "success",
                "actions": actions,
                "count": len(actions),
            },
            status=status.HTTP_200_OK,
        )


class ApprovalPreviewView(APIView):
    """Create a sensitive action preview requiring approval."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        agent_name = request.data.get("agent_name")
        tool_name = request.data.get("tool_name")
        action = request.data.get("action")
        parameters = request.data.get("parameters", {})

        if not agent_name or not tool_name or not action:
            return Response(
                {
                    "status": "error",
                    "message": "agent_name, tool_name and action are required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(parameters, dict):
            return Response(
                {
                    "status": "error",
                    "message": "parameters must be a JSON object.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = tool_registry.request_action(
            agent_name=agent_name,
            tool_name=tool_name,
            action=action,
            parameters=parameters,
            user=request.user,
        )

        return Response(
            result,
            status=status.HTTP_200_OK,
        )


class ApprovalDetailView(APIView):
    """Get an approval action's state for managers and administrators."""

    permission_classes = [IsAuthenticated]

    def get(self, request, action_id):
        require_approval_permission(request.user, "view_approvals")

        action = tool_registry.approval_workflow.get_action(action_id)

        if action is None:
            return Response(
                {
                    "status": "error",
                    "message": "Action not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "status": "success",
                "action": action,
            },
            status=status.HTTP_200_OK,
        )


class ApprovalApproveView(APIView):
    """Approve and execute a pending action as a manager or administrator."""

    permission_classes = [IsAuthenticated]

    def post(self, request, action_id):
        require_approval_permission(request.user, "approve_actions")

        result = tool_registry.approval_workflow.approve_action(
            action_id=action_id,
            user=request.user,
        )

        if result.get("status") == "error":
            return Response(
                result,
                status=status.HTTP_400_BAD_REQUEST,
            )
        execution = result.get("execution", {})
        if execution.get("status") != "success":
            return Response(
                {
                    **result,
                    "message": "Action was approved, but execution failed.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            result,
            status=status.HTTP_200_OK,
        )


class ApprovalEditView(APIView):
    """Allow only the original requester to edit their pending action."""

    permission_classes = [IsAuthenticated]

    def put(self, request, action_id):
        action = tool_registry.approval_workflow.get_action(action_id)

        if action is None:
            return Response(
                {
                    "status": "error",
                    "message": "Action not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not is_action_requester(action, request.user):
            raise PermissionDenied("Only the requester can edit this approval action.")

        updated_parameters = request.data.get(
            "parameters",
            {},
        )

        if not isinstance(updated_parameters, dict):
            return Response(
                {
                    "status": "error",
                    "message": "parameters must be a JSON object.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = tool_registry.approval_workflow.edit_action(
            action_id=action_id,
            updated_parameters=updated_parameters,
            user=request.user,
        )

        if result.get("status") == "error":
            return Response(
                result,
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            result,
            status=status.HTTP_200_OK,
        )


class ApprovalCancelView(APIView):
    """Allow only the original requester to cancel their pending action."""

    permission_classes = [IsAuthenticated]

    def post(self, request, action_id):
        action = tool_registry.approval_workflow.get_action(action_id)

        if action is None:
            return Response(
                {
                    "status": "error",
                    "message": "Action not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not is_action_requester(action, request.user):
            raise PermissionDenied(
                "Only the requester can cancel this approval action."
            )

        result = tool_registry.approval_workflow.cancel_action(
            action_id=action_id,
            user=request.user,
        )

        if result.get("status") == "error":
            return Response(
                result,
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            result,
            status=status.HTTP_200_OK,
        )
