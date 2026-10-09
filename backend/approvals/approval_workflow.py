from audit_logs.utils import create_audit_log
from notifications.utils import (
    create_approval_pending_notification,
    create_approval_executed_notification,
)


class ApprovalWorkflow:
    """
    Handles human approval for sensitive AI actions.
    """

    SENSITIVE_ACTIONS = {
        "send_email",
        "send_bulk_message",
        "approve_leave",
        "financial_change",
        "deploy",
        "delete_data",
    }

    def __init__(self, executor=None):
        self.pending_actions = {}
        self.executor = executor

    def requires_approval(self, action):
        """
        Determine whether an action requires human approval.
        """

        return action in self.SENSITIVE_ACTIONS

    def create_action_preview(
        self, agent_name, tool_name, action, parameters=None, user=None
    ):
        """
        Create a pending action for human approval.
        """

        if parameters is None:
            parameters = {}

        if not self.requires_approval(action):

            result = {
                "status": "not_required",
                "message": "This action does not require approval.",
            }

            create_audit_log(
                user=user or "Unknown",
                agent=agent_name,
                request=action,
                tool=tool_name,
                action=action,
                approval="Not required",
                result=result["message"],
            )

            return result

        action_id = len(self.pending_actions) + 1

        preview = {
            "action_id": action_id,
            "status": "pending",
            "agent": agent_name,
            "tool": tool_name,
            "action": action,
            "parameters": parameters,
            "requester_id": getattr(user, "pk", None),
        }

        self.pending_actions[action_id] = preview

        create_audit_log(
            user=user or "Unknown",
            agent=agent_name,
            request=action,
            tool=tool_name,
            action=action,
            approval="Required - Pending",
            result=f"Approval requested for action {action_id}.",
        )

        # Create an in-app notification for pending approval
        # only when a valid Django User object is provided.
        if user:
            create_approval_pending_notification(
                user=user,
                message=(
                    f"{agent_name} requested approval for "
                    f"{action} using {tool_name}."
                ),
                related_id=str(action_id),
            )

        return preview

    def approve_action(self, action_id, user=None):
        """
        Approve a pending action and execute it through the
        Tool Registry executor.
        """

        action = self.pending_actions.get(action_id)

        if action is None:

            result = {
                "status": "error",
                "message": "Action not found.",
            }

            create_audit_log(
                user=user or "Unknown",
                agent="Unknown",
                request=f"Approve action {action_id}",
                action="Approve action",
                approval="Failed",
                result=result["message"],
            )

            return result

        if action["status"] != "pending":

            result = {
                "status": "error",
                "message": "Action is no longer pending.",
            }

            create_audit_log(
                user=user or "Unknown",
                agent=action["agent"],
                request=action["action"],
                tool=action["tool"],
                action="Approve action",
                approval="Failed",
                result=result["message"],
            )

            return result
        # Record the approval decision separately from execution.
        action["status"] = "approved"

        create_audit_log(
            user=user or "Unknown",
            agent=action["agent"],
            request=action["action"],
            tool=action["tool"],
            action=action["action"],
            approval="Approved",
            result=f"Action {action_id} approved.",
        )

        if not self.executor:
            action["execution_status"] = "failed"
            action["execution_result"] = {
                "status": "error",
                "message": "No executor is configured.",
            }
            create_audit_log(
                user=user or "Unknown",
                agent=action["agent"],
                request=action["action"],
                tool=action["tool"],
                action=action["action"],
                approval="Approved - Execution Failed",
                result=action["execution_result"]["message"],
            )
            return {
                "status": "approved",
                "action": action,
                "execution": action["execution_result"],
            }
        try:
            execution_result = self.executor(
                action["agent"],
                action["tool"],
                action["action"],
                action["parameters"],
                user,
            )
            if not isinstance(execution_result, dict):
                execution_result = {
                    "status": "error",
                    "message": "Executor returned an invalid result.",
                }
        except Exception:
            execution_result = {
                "status": "error",
                "message": "Approved action execution failed.",
            }
        action["execution_result"] = execution_result

        succeeded = execution_result.get("status") == "success"
        action["execution_status"] = "success" if succeeded else "failed"
        if succeeded and user:
            create_approval_executed_notification(
                user=user,
                message=(
                    f"{action['agent']} approved and executed "
                    f"{action['action']} successfully."
                ),
                related_id=str(action_id),
            )
        return {
            "status": "approved",
            "action": action,
            "execution": execution_result,
        }

    def edit_action(self, action_id, updated_parameters, user=None):
        """
        Edit a pending action before approval.
        """

        action = self.pending_actions.get(action_id)

        if action is None:

            result = {
                "status": "error",
                "message": "Action not found.",
            }

            create_audit_log(
                user=user or "Unknown",
                agent="Unknown",
                request=f"Edit action {action_id}",
                action="Edit action",
                approval="Failed",
                result=result["message"],
            )

            return result

        if action["status"] != "pending":

            result = {
                "status": "error",
                "message": "Only pending actions can be edited.",
            }

            create_audit_log(
                user=user or "Unknown",
                agent=action["agent"],
                request=action["action"],
                tool=action["tool"],
                action="Edit action",
                approval="Failed",
                result=result["message"],
            )

            return result

        action["parameters"].update(updated_parameters)

        create_audit_log(
            user=user or "Unknown",
            agent=action["agent"],
            request=action["action"],
            tool=action["tool"],
            action="Edit action",
            approval="Pending",
            result=f"Action {action_id} parameters updated.",
        )

        return {
            "status": "updated",
            "action": action,
        }

    def cancel_action(self, action_id, user=None):
        """
        Cancel a pending action.
        """

        action = self.pending_actions.get(action_id)

        if action is None:

            result = {
                "status": "error",
                "message": "Action not found.",
            }

            create_audit_log(
                user=user or "Unknown",
                agent="Unknown",
                request=f"Cancel action {action_id}",
                action="Cancel action",
                approval="Failed",
                result=result["message"],
            )

            return result

        if action["status"] != "pending":

            result = {
                "status": "error",
                "message": "Action is no longer pending.",
            }

            create_audit_log(
                user=user or "Unknown",
                agent=action["agent"],
                request=action["action"],
                tool=action["tool"],
                action="Cancel action",
                approval="Failed",
                result=result["message"],
            )

            return result

        action["status"] = "cancelled"

        create_audit_log(
            user=user or "Unknown",
            agent=action["agent"],
            request=action["action"],
            tool=action["tool"],
            action="Cancel action",
            approval="Cancelled",
            result=f"Action {action_id} cancelled.",
        )

        return {
            "status": "cancelled",
            "action": action,
        }

    def get_action(self, action_id):
        """
        Get the current state of an action.
        """

        return self.pending_actions.get(action_id)
