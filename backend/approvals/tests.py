from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase

from approvals.approval_workflow import ApprovalWorkflow
from approvals.models import ApprovalAction


class ApprovalWorkflowPersistenceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="approval_requester_test",
            password="test-password-only",
        )
        self.executor = Mock(
            return_value={"status": "success", "message": "Test execution only"}
        )
        self.workflow = ApprovalWorkflow(executor=self.executor)

    @patch("approvals.approval_workflow.create_approval_pending_notification")
    @patch("approvals.approval_workflow.create_audit_log")
    def test_preview_persists_and_does_not_execute(self, mock_audit, mock_notification):
        preview = self.workflow.create_action_preview(
            agent_name="Sales Agent",
            tool_name="email_tool",
            action="send_email",
            parameters={
                "recipient": "test@example.com",
                "subject": "Test preview",
                "message": "Preview only",
            },
            user=self.user,
        )

        self.assertEqual(preview["status"], "pending")
        self.assertTrue(ApprovalAction.objects.filter(pk=preview["action_id"]).exists())

        # A separate workflow instance can retrieve the same database record.
        another_workflow = ApprovalWorkflow()
        saved_action = another_workflow.get_action(preview["action_id"])

        self.assertIsNotNone(saved_action)
        self.assertEqual(saved_action["status"], "pending")
        self.assertEqual(saved_action["requester_id"], self.user.pk)
        self.assertEqual(saved_action["parameters"]["subject"], "Test preview")

        # Preview creation must never execute the requested action.
        self.executor.assert_not_called()

    @patch("approvals.approval_workflow.create_approval_pending_notification")
    @patch("approvals.approval_workflow.create_audit_log")
    def test_edit_updates_database_parameters(self, mock_audit, mock_notification):
        preview = self.workflow.create_action_preview(
            "Sales Agent",
            "email_tool",
            "send_email",
            {"subject": "Original"},
            self.user,
        )

        result = self.workflow.edit_action(
            preview["action_id"],
            {"subject": "Updated"},
            user=self.user,
        )

        self.assertEqual(result["status"], "updated")

        record = ApprovalAction.objects.get(pk=preview["action_id"])
        self.assertEqual(record.parameters["subject"], "Updated")
        self.assertEqual(record.status, "pending")

    @patch("approvals.approval_workflow.create_approval_pending_notification")
    @patch("approvals.approval_workflow.create_audit_log")
    def test_cancel_updates_database_status(self, mock_audit, mock_notification):
        preview = self.workflow.create_action_preview(
            "Sales Agent",
            "email_tool",
            "send_email",
            {"subject": "Cancel test"},
            self.user,
        )

        result = self.workflow.cancel_action(
            preview["action_id"],
            user=self.user,
        )

        self.assertEqual(result["status"], "cancelled")

        record = ApprovalAction.objects.get(pk=preview["action_id"])
        self.assertEqual(record.status, "cancelled")

    @patch("approvals.approval_workflow.create_approval_executed_notification")
    @patch("approvals.approval_workflow.create_approval_pending_notification")
    @patch("approvals.approval_workflow.create_audit_log")
    def test_approval_persists_mock_execution_result(
        self, mock_audit, mock_pending_notification, mock_executed_notification
    ):
        preview = self.workflow.create_action_preview(
            "Sales Agent",
            "email_tool",
            "send_email",
            {"subject": "Mock execution test"},
            self.user,
        )

        result = self.workflow.approve_action(
            preview["action_id"],
            user=self.user,
        )

        self.assertEqual(result["status"], "approved")
        self.assertEqual(result["execution"]["status"], "success")

        record = ApprovalAction.objects.get(pk=preview["action_id"])
        self.assertEqual(record.status, "approved")
        self.assertEqual(record.execution_status, "success")
        self.assertEqual(
            record.execution_result["message"],
            "Test execution only",
        )

        self.executor.assert_called_once()
