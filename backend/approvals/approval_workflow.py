from django.db import transaction

from approvals.models import ApprovalAction
from audit_logs.utils import create_audit_log
from notifications.utils import (
    create_approval_pending_notification,
    create_approval_executed_notification,
)


class ApprovalWorkflow:
    """
    Handles human approval for sensitive actions.
    Approval records are persisted in the Django database.
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
        self.executor = executor

    def requires_approval(self, action):
        return action in self.SENSITIVE_ACTIONS

    @staticmethod
    def _serialize_action(record):
        """Convert a database record to the existing API dictionary format."""
        return {
            "action_id": record.pk,
            "status": record.status,
            "agent": record.agent,
            "tool": record.tool,
            "action": record.action,
            "parameters": record.parameters,
            "requester_id": record.requester_id,
            "execution_status": record.execution_status,
            "execution_result": record.execution_result,
        }

    def create_action_preview(
        self, agent_name, tool_name, action, parameters=None, user=None
    ):
        """Persist a pending action without executing it."""

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

        record = ApprovalAction.objects.create(
            requester=user if getattr(user, "pk", None) else None,
            agent=agent_name,
            tool=tool_name,
            action=action,
            parameters=parameters,
            status="pending",
        )
        preview = self._serialize_action(record)

        create_audit_log(
            user=user or "Unknown",
            agent=agent_name,
            request=action,
            tool=tool_name,
            action=action,
            approval="Required - Pending",
            result=f"Approval requested for action {record.pk}.",
        )

        if user:
            create_approval_pending_notification(
                user=user,
                message=(
                    f"{agent_name} requested approval for "
                    f"{action} using {tool_name}."
                ),
                related_id=str(record.pk),
            )

        return preview

    def approve_action(self, action_id, user=None):
        """Mark a pending action approved, then execute it once."""

        with transaction.atomic():
            record = (
                ApprovalAction.objects.select_for_update().filter(pk=action_id).first()
            )

            if record is None:
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

            if record.status != "pending":
                result = {
                    "status": "error",
                    "message": "Action is no longer pending.",
                }
                create_audit_log(
                    user=user or "Unknown",
                    agent=record.agent,
                    request=record.action,
                    tool=record.tool,
                    action="Approve action",
                    approval="Failed",
                    result=result["message"],
                )
                return result

            record.status = "approved"
            record.save(update_fields=["status", "updated_at"])

            action_data = self._serialize_action(record)

        create_audit_log(
            user=user or "Unknown",
            agent=action_data["agent"],
            request=action_data["action"],
            tool=action_data["tool"],
            action=action_data["action"],
            approval="Approved",
            result=f"Action {action_id} approved.",
        )

        if not self.executor:
            execution_result = {
                "status": "error",
                "message": "No executor is configured.",
            }
        else:
            try:
                execution_result = self.executor(
                    action_data["agent"],
                    action_data["tool"],
                    action_data["action"],
                    action_data["parameters"],
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

        execution_status = (
            "success" if execution_result.get("status") == "success" else "failed"
        )

        ApprovalAction.objects.filter(pk=action_id).update(
            execution_status=execution_status,
            execution_result=execution_result,
        )

        action_data["execution_status"] = execution_status
        action_data["execution_result"] = execution_result

        if execution_status == "failed":
            create_audit_log(
                user=user or "Unknown",
                agent=action_data["agent"],
                request=action_data["action"],
                tool=action_data["tool"],
                action=action_data["action"],
                approval="Approved - Execution Failed",
                result=execution_result.get(
                    "message", "Approved action execution failed."
                ),
            )

        if execution_status == "success" and user:
            create_approval_executed_notification(
                user=user,
                message=(
                    f"{action_data['agent']} approved and executed "
                    f"{action_data['action']} successfully."
                ),
                related_id=str(action_id),
            )

        return {
            "status": "approved",
            "action": action_data,
            "execution": execution_result,
        }

    def edit_action(self, action_id, updated_parameters, user=None):
        """Update parameters of a pending action."""

        with transaction.atomic():
            record = (
                ApprovalAction.objects.select_for_update().filter(pk=action_id).first()
            )

            if record is None:
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

            if record.status != "pending":
                result = {
                    "status": "error",
                    "message": "Only pending actions can be edited.",
                }
                create_audit_log(
                    user=user or "Unknown",
                    agent=record.agent,
                    request=record.action,
                    tool=record.tool,
                    action="Edit action",
                    approval="Failed",
                    result=result["message"],
                )
                return result

            parameters = dict(record.parameters)
            parameters.update(updated_parameters)
            record.parameters = parameters
            record.save(update_fields=["parameters", "updated_at"])
            action_data = self._serialize_action(record)

        create_audit_log(
            user=user or "Unknown",
            agent=action_data["agent"],
            request=action_data["action"],
            tool=action_data["tool"],
            action="Edit action",
            approval="Pending",
            result=f"Action {action_id} parameters updated.",
        )

        return {
            "status": "updated",
            "action": action_data,
        }

    def cancel_action(self, action_id, user=None):
        """Cancel a pending action."""

        with transaction.atomic():
            record = (
                ApprovalAction.objects.select_for_update().filter(pk=action_id).first()
            )

            if record is None:
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

            if record.status != "pending":
                result = {
                    "status": "error",
                    "message": "Action is no longer pending.",
                }
                create_audit_log(
                    user=user or "Unknown",
                    agent=record.agent,
                    request=record.action,
                    tool=record.tool,
                    action="Cancel action",
                    approval="Failed",
                    result=result["message"],
                )
                return result

            record.status = "cancelled"
            record.save(update_fields=["status", "updated_at"])
            action_data = self._serialize_action(record)

        create_audit_log(
            user=user or "Unknown",
            agent=action_data["agent"],
            request=action_data["action"],
            tool=action_data["tool"],
            action="Cancel action",
            approval="Cancelled",
            result=f"Action {action_id} cancelled.",
        )

        return {
            "status": "cancelled",
            "action": action_data,
        }

    def get_action(self, action_id):
        """Retrieve an action from the database."""

        record = ApprovalAction.objects.filter(pk=action_id).first()
        if record is None:
            return None
        return self._serialize_action(record)
