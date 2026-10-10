# Vetri AI Multi-Agent

## Admin Guide

**Project:** Vetri AI Multi-Agent Business Operations Assistant
**Frontend:** React + Vite
**Backend:** Django + Django REST Framework
**Authentication:** JWT
**Deployment:** Render

---

# 1. Introduction

This guide is intended for administrators responsible for managing and maintaining the Vetri AI Multi-Agent application.

Administrators are responsible for:

* User and role management
* Permission management
* Monitoring AI agents
* Monitoring approvals
* Reviewing notifications
* Reviewing audit records
* Managing integrations
* Monitoring automation
* Supporting deployment and configuration
* Troubleshooting application issues

---

# 2. Administrator Responsibilities

The administrator should regularly monitor:

* Application availability
* User access
* User roles
* Permissions
* AI agent functionality
* Approval requests
* Notifications
* Audit records
* External integrations
* Automation
* System errors

---

# 3. User Management

The application provides a User Roles API for retrieving user-role information.

**Endpoint**

```http
GET /api/user-roles/
```

**Authentication:** Required.

Administrators should ensure that users are assigned appropriate roles according to their responsibilities.

Users should not receive permissions that are unnecessary for their work.

---

# 4. Role Management

Roles are used to control access to business functionality.

The role and permission system should follow the principle of least privilege.

Administrators should:

1. Review available users.
2. Review their assigned roles.
3. Verify that the assigned permissions are appropriate.
4. Remove unnecessary access.
5. Review access whenever a user's responsibilities change.

---

# 5. Permission Management

The Permission Engine controls access to business operations.

**Endpoint**

```http
GET /api/permissions/
```

**Authentication:** Required.

Administrators should verify that restricted operations are accessible only to authorized users.

Permission checks are particularly important for sensitive business actions.

---

# 6. AI Agent Management

The application uses a multi-agent architecture.

Registered agents include:

* Calendar Agent
* HR Agent
* Sales Agent
* CRM Agent
* Project Agent
* Finance Agent
* Marketing Agent
* Developer Agent
* Customer Support Agent
* QA Agent
* Operations Agent
* Reporting Agent
* GitHub Agent
* Cloud Storage Agent

The Agent Registry API can be used to retrieve the available agents.

**Endpoint**

```http
GET /api/agents/
```

**Authentication:** Required.

Administrators should verify that expected agents are available after deployment or configuration changes.

---

# 7. AI Agent Monitoring

When troubleshooting AI requests, administrators should check the following flow:

```text
User Request
     ↓
Django Chat API
     ↓
AI Orchestrator
     ↓
Agent Registry
     ↓
Specialized Agent
     ↓
Tool / Data Source
     ↓
Response
```

If an AI request fails, determine which layer produced the error.

Possible problem areas include:

* Authentication
* Orchestrator routing
* Agent processing
* Tool execution
* Database access
* External integrations
* AI/LLM configuration

---

# 8. Approval Workflow Administration

Sensitive actions defined in `ApprovalWorkflow.SENSITIVE_ACTIONS` require approval before execution. These include:

- `send_email`
- `send_bulk_message`
- `approve_leave`
- `financial_change`
- `deploy`
- `delete_data`

The workflow is:

Sensitive Request
    |
    v
Approval Preview Created
    |
    v
Pending Notification and Audit Record
    |
    v
Authorized Review
    |
    v
Approve / Edit / Cancel
    |
    v
Execution Attempt (after approval)
    |
    v
Execution Result Recorded
    |
    v
Audit Record

**Authorization rules:**

- Authenticated users can request approval previews through the API.
- Managers and administrators have the `approve_actions` permission.
- Only the original requester can edit or cancel their own pending approval.
- Actions that are no longer pending cannot be edited, cancelled, or approved through the workflow.
- Approval does not guarantee successful execution. The execution result must be checked separately.

Administrators should review pending approvals and investigate failed executions. Do not assume an action was successfully executed merely because its approval status is `approved`.

---

# 9. Approval API

The approval system provides these authenticated endpoints:

**List approvals**

```http
GET /api/approvals/
```

**Filter approvals**

```http
GET /api/approvals/?status=pending
```

**Create an approval preview**

```http
POST /api/approvals/preview/
```

**View an approval**

```http
GET /api/approvals/<action_id>/
```

**Approve an action**

```http
POST /api/approvals/<action_id>/approve/
```

**Edit a pending approval**

```http
PUT /api/approvals/<action_id>/edit/
```

**Cancel a pending approval**

```http
POST /api/approvals/<action_id>/cancel/
```

All approval endpoints require authentication. Viewing approvals and approving actions are additionally controlled by the Permission Engine:

- `view_approvals`: granted to manager and admin roles.
- `approve_actions`: granted to manager and admin roles.
- Editing and cancellation: restricted by the API to the original requester of the pending action.

Requests that fail authorization should be rejected. Administrators should not bypass the requester-ownership rules when managing another user's pending action.

---

# 10. Approval Failure Handling

Approval status and execution status represent different stages of the workflow.

- `pending`: the action is awaiting a decision.
- `approved`: the action was approved. Execution may still succeed or fail.
- `cancelled`: the pending action was cancelled.
- `execution_status = success`: the executor returned a successful result.
- `execution_status = failed`: execution failed or no executor was configured.

When an approved action fails during execution, the workflow records the failure result and creates an audit record identifying the execution failure. The approval status remains `approved`, while the separate execution status records `failed`.

Administrators investigating a failure should review:

- Approval status and execution status
- Saved action parameters
- Executor configuration
- Stored execution result
- Related audit records

An approved action must not be reported as successfully executed unless its execution result confirms success. Notifications indicating successful execution should likewise be interpreted according to the recorded result.

The approval test suite verifies the core API authorization and workflow persistence behavior. Real external action delivery must be tested separately before it is reported as production-verified.

---

# 11. Notification Management

Notifications provide information about important application events.

Notifications may be delivered through supported notification channels, including in-app notifications, email, and WhatsApp when configured.

Notifications can include:

- Approval requests
- Approved actions
- Executed actions
- Project risks
- High-priority leads
- Overdue payments
- Customer issues

Notification APIs are restricted to the authenticated user's notifications.

---

# 12. Notification APIs

### List Notifications

```http
GET /api/notifications/
```

### Notification Details

```http
GET /api/notifications/<id>/
```

### Mark Notification as Read

```http
PUT /api/notifications/<id>/read/
```

All notification endpoints require authentication.

---

# 13. Audit Logging

The audit logging system provides traceability for important system operations.

Audit records contain:

* User
* Agent
* Request
* Data accessed
* Tool
* Action
* Approval
* Result
* Timestamp

The audit log API is:

```http
GET /api/audit-logs/
```

The audit log view requires authentication and checks the user's view_audit_logs permission through the Permission Engine. Users without this permission are denied access.

Administrators should protect audit information because it may contain sensitive operational details.

---

# 14. Reviewing Audit Records

Audit records can be used to investigate:

* Who performed an action
* Which agent processed the request
* Which tool was used
* What action was requested
* Whether approval was required
* Whether approval was granted
* Whether execution succeeded or failed
* When the action occurred

A typical approval workflow may produce audit records such as:

```text
Required - Pending
        |
        v
Approved
```

If execution fails after approval, the workflow records an execution-failure audit entry, such as:

```text
Approved - Execution Failed
```

The exact audit records depend on the outcome of the action. Administrators should review the execution result and related audit records rather than assuming that approval means successful execution.

---

# 15. Google Calendar Administration

The application integrates with Google Calendar using OAuth 2.0.

The available endpoints are:

```http
GET /api/calendar/login/
GET /api/calendar/oauth2callback/
GET /api/calendar/test/
```

The OAuth flow is:

```text
Application
     |
     v
Google OAuth Login
     |
     v
User Authorization
     |
     v
OAuth Callback
     |
     v
Credentials Stored in Session
     |
     v
Calendar API
```

---

# 16. Google Calendar Troubleshooting

Common OAuth problems include:

### Redirect URI Mismatch

If Google reports:

```text
redirect_uri_mismatch
```

verify that the callback URL configured in Google Cloud exactly matches the callback URL used by the application.

### Access Denied

If Google reports:

```text
access_denied
```

check:

* OAuth consent configuration
* Test users
* Google Cloud project configuration
* Requested permissions

### Calendar Connection Failure

Use the Calendar Test endpoint:

```http
GET /api/calendar/test/
```

Review the backend logs if the integration fails.

---

# 17. Automation Administration

Vetri AI provides automation endpoints for generating reminders and intelligent alerts.

## Generate Reminders

```http
POST /api/automation/reminders/
```

**Authentication:** Required.

The endpoint generates automated reminders based on available business information.

## Generate Intelligent Alerts

```http
POST /api/automation/alerts/
```

**Authentication:** Required.

The endpoint generates alerts based on important business conditions.

---

# 18. Automation Monitoring

Administrators should monitor automated reminders and alerts for:

* Duplicate notifications
* Incorrect information
* Missing business data
* Unexpected alert volume
* Failed generation
* Incorrect business conditions

Automation should be reviewed after major changes to business data or agent logic.

---

# 19. Backend Administration

The Django backend can be checked using:

```powershell
python manage.py check
```

Run database migrations when required:

```powershell
python manage.py makemigrations
python manage.py migrate
```

**Migration guidance:**

- Run `makemigrations` when model changes require new database migrations.
- Review generated migration files before applying them.
- Run `migrate` to apply pending migrations to the configured database.
- Back up important production data before applying migrations.
- Avoid generating migrations unnecessarily when no model changes require them.

The application should be restarted after relevant backend configuration changes.

---

# 20. Production Configuration

Production configuration should be stored securely.

Administrators should manage:

* Django secret key
* Debug configuration
* Allowed hosts
* CORS configuration
* Database configuration
* OAuth credentials
* Email configuration
* WhatsApp configuration
* AI/LLM credentials
* Other required environment variables

### WhatsApp Configuration and Delivery Status

The WhatsApp notification service supports a simulated delivery mode. Real delivery through the Meta WhatsApp Cloud API requires valid provider configuration and a successful provider delivery test.

The following production environment variables are required for real WhatsApp delivery:

- `WHATSAPP_API_URL`
- `WHATSAPP_ACCESS_TOKEN`
- `WHATSAPP_PHONE_NUMBER_ID`

The service includes configuration validation and delivery error handling. A simulated result confirms only that the mock flow ran; it does not confirm delivery through Meta.

Real Meta WhatsApp message delivery remains unverified until valid credentials are configured and a successful provider delivery test is completed.

Sensitive credentials must never be committed to GitHub.

---

# 21. Security Administration

Administrators should:

* Use strong authentication credentials.
* Apply least-privilege access.
* Protect sensitive business operations.
* Review approval requests.
* Monitor audit records.
* Protect API credentials.
* Protect OAuth credentials.
* Avoid exposing secrets in frontend code.
* Configure production CORS correctly.
* Use HTTPS.
* Keep dependencies updated.
* Disable debug mode in production.
* Monitor failed authentication and unexpected operations.

---

# 22. Deployment Administration

The application is deployed using Render and source code is maintained in GitHub.

A typical deployment workflow is:

```text
Code Changes
     |
     v
Git Commit
     |
     v
Git Push
     |
     v
GitHub
     |
     v
Render Build
     |
     v
Render Deployment
     |
     v
Production Verification
```

After deployment, administrators should verify that the application is working correctly.

---

# 23. Deployment Verification

After each deployment, run the following checks and record the actual result. Do not mark a check as passed until it has been tested in the target environment.

### Backend

- Confirm the Django service is running.
- Check that Gunicorn starts successfully.
- Confirm required database migrations are applied.
- Verify that the required API endpoints are reachable.
- Review deployment logs for configuration errors.

### Frontend

- Confirm the React application loads.
- Test login and authentication.
- Verify API requests use the configured deployed backend URL rather than a local development URL.
- Confirm the dashboard retrieves data from the `/api/dashboard/` endpoint.
- Test AI Chat and relevant follow-up interactions.

### Integrations

- Test Google Calendar OAuth and API access using the configured production callback and authorized session.
- Test email delivery only when email configuration is available and an approved test recipient is being used.
- Verify business tools against their actual implementation; do not assume external services are connected when the feature uses mock or internal data.

### Security and Approval Workflow

- Confirm JWT authentication works and protected APIs reject unauthenticated requests.
- Verify approval permissions and requester-ownership restrictions.
- Confirm approval and execution outcomes are recorded correctly in audit logs.
- Keep approval-only tests separate from tests that execute real external actions.

### Recording Results

Record each check as **Passed**, **Failed**, **Blocked**, or **Not Tested**. Document any remaining issue and its next action. Do not describe the deployment as fully verified while critical checks remain unresolved.
---

# 24. Troubleshooting Procedure

When a production problem occurs, follow this sequence:

### Step 1 - Identify the Problem

Determine whether the issue affects:

* Frontend
* Backend
* Authentication
* AI agents
* Database
* Tool execution
* External integration
* Automation

### Step 2 - Check Logs

Review the backend and deployment logs.

Look for:

* Python exceptions
* Django errors
* API errors
* Authentication errors
* Integration errors
* Tool execution errors

### Step 3 - Test the API

Test the relevant endpoint independently.

For example:

```http
GET /api/hello/
```

### Step 4 - Check Authentication

Verify that the JWT access token is valid.

### Step 5 - Check Configuration

Verify relevant environment variables and external service configuration.

### Step 6 - Retest

After making the correction, repeat the affected workflow.

---

# 25. Common Administrative Issues

## Backend Does Not Start

Check:

* Python version
* `requirements.txt`
* Django configuration
* WSGI module
* Environment variables
* Render logs

---

## Frontend Cannot Reach Backend

Check:

* Backend URL
* CORS configuration
* Frontend environment configuration
* Backend availability
* Browser network errors

---

## Authentication Failure

Check:

* Username and password
* JWT access token
* JWT refresh token
* Authentication header
* Backend authentication configuration

---

## Approval Does Not Execute

Check:

* Approval status
* Action parameters
* Tool configuration
* Required fields
* Execution result
* Audit record

---

## Email Action Fails

Check:

* Recipient
* Subject
* Message
* Email service configuration
* Tool execution result

---

## Calendar Integration Fails

Check:

* OAuth credentials
* Redirect URI
* Google Cloud configuration
* Session credentials
* Calendar API access

---

# 26. Backup and Recovery

Administrators should maintain appropriate backups of production data and configuration.

Important data may include:

* Business database
* User records
* Conversation history
* Approval records
* Notification records
* Audit records
* Required configuration

Credentials and secrets should be backed up securely according to organizational security policies.

---

# 27. Recommended Maintenance

Regular maintenance should include:

* Reviewing application logs
* Reviewing audit records
* Checking pending approvals
* Checking failed tool executions
* Verifying integrations
* Checking automation results
* Updating dependencies
* Reviewing user permissions
* Reviewing production configuration
* Testing critical API endpoints

---

# 28. Administrator Checklist

## User Access

* [ ] User roles reviewed
* [ ] Permissions reviewed
* [ ] Unnecessary access removed

## AI System

* [ ] Agents available
* [ ] AI Chat functioning
* [ ] Agent routing functioning
* [ ] Tool execution functioning

## Approval System

* [ ] Pending approvals reviewed
* [ ] Approval notifications working
* [ ] Approved actions executing
* [ ] Failed executions investigated

## Notifications

* [ ] Notifications generated
* [ ] Notifications delivered to users
* [ ] Read status functioning

## Audit

* [ ] Audit records generated
* [ ] Approval history traceable
* [ ] Failed actions recorded

## Integrations

* [ ] Google Calendar tested
* [ ] Email integration tested
* [ ] WhatsApp configuration verified
* [ ] WhatsApp real Meta delivery tested when credentials are available
* [ ] Internal business tools responding correctly

## Automation

* [ ] Reminders generated
* [ ] Intelligent alerts generated
* [ ] Unexpected alerts investigated

## Deployment

* [ ] Production application available
* [ ] Backend available
* [ ] Frontend available
* [ ] Database available
* [ ] No critical deployment errors

---

# 29. Summary

The administrator is responsible for maintaining secure and reliable operation of the Vetri AI Multi-Agent platform.

The main administrative areas are:

* User access
* Roles
* Permissions
* AI agents
* Tools
* Approvals
* Notifications
* Audit logging
* Google Calendar
* Automation
* Deployment
* Security
* Troubleshooting

Regular monitoring and testing help ensure that the multi-agent business operations platform remains secure, available, and reliable.
