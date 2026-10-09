from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from approvals.approval_workflow import ApprovalWorkflow
from approvals.models import ApprovalAction
from myapp.models import UserProfile


class ApprovalAPIPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.requester = self.create_user("approval_requester_api_test", "employee")
        self.other_employee = self.create_user("approval_other_api_test", "employee")
        self.manager = self.create_user("approval_manager_api_test", "manager")
        self.admin = self.create_user("approval_admin_api_test", "admin")

        # Use a separate workflow instance for creating test records.
        self.workflow = ApprovalWorkflow()

        self.preview = self.workflow.create_action_preview(
            agent_name="Sales Agent",
            tool_name="email_tool",
            action="send_email",
            parameters={
                "recipient": "test@example.com",
                "subject": "API permission test",
                "message": "Mock test only",
            },
            user=self.requester,
        )
        self.action_id = self.preview["action_id"]

    def create_user(self, username, role):
        user = User.objects.create_user(
            username=username,
            password="test-password-only",
        )
        UserProfile.objects.create(user=user, role=role)
        return user

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    @patch("approvals.views.tool_registry")
    def test_requester_can_edit_own_pending_action(self, mock_registry):
        # Use the real workflow for persistence and ownership.
        mock_registry.approval_workflow = self.workflow
        self.authenticate(self.requester)

        response = self.client.put(
            reverse("approval-edit", args=[self.action_id]),
            {"parameters": {"subject": "Updated by requester"}},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        record = ApprovalAction.objects.get(pk=self.action_id)
        self.assertEqual(record.parameters["subject"], "Updated by requester")

    @patch("approvals.views.tool_registry")
    def test_other_user_cannot_edit_requester_action(self, mock_registry):
        mock_registry.approval_workflow = self.workflow
        self.authenticate(self.other_employee)

        response = self.client.put(
            reverse("approval-edit", args=[self.action_id]),
            {"parameters": {"subject": "Unauthorized edit"}},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        record = ApprovalAction.objects.get(pk=self.action_id)
        self.assertEqual(record.parameters["subject"], "API permission test")

    @patch("approvals.views.tool_registry")
    def test_requester_can_cancel_own_pending_action(self, mock_registry):
        mock_registry.approval_workflow = self.workflow
        self.authenticate(self.requester)

        response = self.client.post(
            reverse("approval-cancel", args=[self.action_id]),
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        record = ApprovalAction.objects.get(pk=self.action_id)
        self.assertEqual(record.status, "cancelled")

    @patch("approvals.views.tool_registry")
    def test_other_user_cannot_cancel_requester_action(self, mock_registry):
        mock_registry.approval_workflow = self.workflow
        self.authenticate(self.other_employee)

        response = self.client.post(
            reverse("approval-cancel", args=[self.action_id]),
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        record = ApprovalAction.objects.get(pk=self.action_id)
        self.assertEqual(record.status, "pending")

    @patch("approvals.views.tool_registry")
    def test_employee_cannot_approve_action(self, mock_registry):
        mock_registry.approval_workflow = self.workflow
        self.authenticate(self.other_employee)

        response = self.client.post(
            reverse("approval-approve", args=[self.action_id]),
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        record = ApprovalAction.objects.get(pk=self.action_id)
        self.assertEqual(record.status, "pending")

    @patch("approvals.views.tool_registry")
    def test_manager_can_view_approval_list(self, mock_registry):
        mock_registry.approval_workflow = self.workflow
        self.authenticate(self.manager)

        response = self.client.get(reverse("approval-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    @patch("approvals.views.tool_registry")
    def test_admin_can_view_approval_list(self, mock_registry):
        mock_registry.approval_workflow = self.workflow
        self.authenticate(self.admin)

        response = self.client.get(reverse("approval-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    @patch("approvals.approval_workflow.create_approval_executed_notification")
    @patch("approvals.approval_workflow.create_audit_log")
    @patch("approvals.views.tool_registry")
    def test_manager_can_approve_with_mocked_execution(
        self, mock_registry, mock_audit, mock_notification
    ):
        executor = Mock(
            return_value={
                "status": "success",
                "message": "Mock execution only",
            }
        )
        self.workflow.executor = executor
        mock_registry.approval_workflow = self.workflow
        self.authenticate(self.manager)

        response = self.client.post(
            reverse("approval-approve", args=[self.action_id]),
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "approved")
        executor.assert_called_once()

        record = ApprovalAction.objects.get(pk=self.action_id)
        self.assertEqual(record.status, "approved")
        self.assertEqual(record.execution_status, "success")

    @patch("approvals.approval_workflow.create_approval_executed_notification")
    @patch("approvals.approval_workflow.create_audit_log")
    @patch("approvals.views.tool_registry")
    def test_admin_can_approve_with_mocked_execution(
        self, mock_registry, mock_audit, mock_notification
    ):
        executor = Mock(
            return_value={
                "status": "success",
                "message": "Mock execution only",
            }
        )
        self.workflow.executor = executor
        mock_registry.approval_workflow = self.workflow
        self.authenticate(self.admin)

        response = self.client.post(
            reverse("approval-approve", args=[self.action_id]),
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "approved")
        executor.assert_called_once()

        record = ApprovalAction.objects.get(pk=self.action_id)
        self.assertEqual(record.status, "approved")
        self.assertEqual(record.execution_status, "success")

    def test_manager_cannot_edit_another_users_action(self):
        self.authenticate(self.manager)

        response = self.client.put(
            reverse("approval-edit", args=[self.action_id]),
            data={"parameters": {"subject": "Unauthorized change"}},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        record = ApprovalAction.objects.get(pk=self.action_id)
        self.assertEqual(record.status, "pending")

    def test_admin_cannot_edit_another_users_action(self):
        self.authenticate(self.admin)

        response = self.client.put(
            reverse("approval-edit", args=[self.action_id]),
            data={"parameters": {"subject": "Unauthorized change"}},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        record = ApprovalAction.objects.get(pk=self.action_id)
        self.assertEqual(record.status, "pending")

    def test_manager_cannot_cancel_another_users_action(self):
        self.authenticate(self.manager)

        response = self.client.post(
            reverse("approval-cancel", args=[self.action_id]),
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        record = ApprovalAction.objects.get(pk=self.action_id)
        self.assertEqual(record.status, "pending")

    def test_admin_cannot_cancel_another_users_action(self):
        self.authenticate(self.admin)

        response = self.client.post(
            reverse("approval-cancel", args=[self.action_id]),
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        record = ApprovalAction.objects.get(pk=self.action_id)
        self.assertEqual(record.status, "pending")
