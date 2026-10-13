from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
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

    Persists approval records, notifies requesters in-app, and emails
    eligible active manager/admin approvers when approvals are created
    or execution completes.
    """

    SENSITIVE_ACTIONS = {
        "send_email",
        "send_bulk_message",
        "approve_leave",
        "financial_change",
        "deploy",
        "delete_data",
    }

    APPROVER_ROLES = {"manager", "admin"}

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

    @classmethod
    def _get_approver_users(cls):
        """
        Return active manager/admin users, including superusers,
        who have an email address.

        Users without a profile or email address are skipped.
        """
        User = get_user_model()
        approvers = []

        users = (
            User.objects.filter(
                is_active=True,
            )
            .exclude(
                email__isnull=True,
            )
            .exclude(
                email="",
            )
        )

        for candidate in users:
            if candidate.is_superuser:
                approvers.append(candidate)
                continue

            try:
                profile = candidate.profile
                role = getattr(profile, "role", None)
            except (ObjectDoesNotExist, AttributeError):
                continue

            if role in cls.APPROVER_ROLES:
                approvers.append(candidate)

        return approvers

    @classmethod
    def _notify_approvers_by_email(
        cls,
        message,
        related_id,
        title="Approval Required",
    ):
        """
        Email eligible approvers using the existing notification helper.

        Notification failures must not interrupt approval creation
        or the result of an already-executed action.
        """
        for approver in cls._get_approver_users():
            try:
                create_approval_pending_notification(
                    user=approver,
                    message=message,
                    related_id=str(related_id),
                    channel="email",
                    title=title,
                )
            except Exception:
                # Do not fail the approval workflow because a notification
                # could not be delivered.
                continue

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

        message = (
            f"{agent_name} requested approval for "
            f"{action} using {tool_name}. "
            f"Approval ID: {record.pk}."
        )

        # Preserve the requester's existing in-app notification.
        if user:
            create_approval_pending_notification(
                user=user,
                message=(
                    f"{agent_name} requested approval for "
                    f"{action} using {tool_name}."
                ),
                related_id=str(record.pk),
            )

        # Notify active manager/admin approvers by email and WhatsApp.
        approvers = self._get_approver_users()

        self._notify_approvers_by_email(
            message=message,
            related_id=record.pk,
        )

        for approver in approvers:
            try:
                create_approval_pending_notification(
                    user=approver,
                    message=message,
                    related_id=str(record.pk),
                    channel="whatsapp",
                    title="Approval Required",
                )
            except Exception:
                # Notification failures must not interrupt approval creation.
                continue
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
                    "message",
                    "Approved action execution failed.",
                ),
            )

        # Preserve the existing requester's in-app success notification.
        if execution_status == "success" and record.requester_id:
            create_approval_executed_notification(
                user=record.requester,
                message=(
                    f"{action_data['agent']} approved and executed "
                    f"{action_data['action']} successfully."
                ),
                related_id=str(action_id),
            )

        # Email approvers for both successful and failed execution.
        completion_message = (
            f"Approval action {action_id} has completed execution.\n"
            f"Action: {action_data['action']}\n"
            f"Agent: {action_data['agent']}\n"
            f"Execution status: {execution_status}\n"
            f"Result: {execution_result.get('message', execution_status)}"
        )

        self._notify_approvers_by_email(
            message=completion_message,
            related_id=action_id,
            title=(
                "Approved Action Execution Successful"
                if execution_status == "success"
                else "Approved Action Execution Failed"
            ),
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
