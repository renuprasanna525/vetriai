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

Sensitive actions require approval before execution.

Current sensitive actions include:

* `send_email`
* `send_bulk_message`
* `approve_leave`
* `financial_change`
* `deploy`
* `delete_data`

The workflow is:

```text
Sensitive Request
      ↓
Approval Created
      ↓
Pending Notification
      ↓
User Review
      ↓
Approve / Edit / Cancel
      ↓
Tool Execution
      ↓
Execution Notification
      ↓
Audit Log
```

Administrators should monitor pending approval requests and investigate unexpected or failed executions.

---

# 9. Approval API

The approval system provides the following operations.

### List Approvals

```http
GET /api/approvals/
```

### Filter Approvals

```http
GET /api/approvals/?status=pending
```

### Create Approval Preview

```http
POST /api/approvals/preview/
```

### View Approval

```http
GET /api/approvals/<action_id>/
```

### Approve Action

```http
POST /api/approvals/<action_id>/approve/
```

### Edit Approval

```http
PUT /api/approvals/<action_id>/edit/
```

### Cancel Approval

```http
POST /api/approvals/<action_id>/cancel/
```

All approval endpoints require authentication.

---

# 10. Approval Failure Handling

A sensitive action may be approved successfully but still fail during tool execution.

For example, an email action may fail when required recipient information is missing.

Example:

```json
{
    "status": "error",
    "message": "Recipient is required."
}
```

Administrators should review the approval result and audit record when an execution fails.

The approval system records execution results so that failures can be investigated.

---

# 11. Notification Management

Notifications provide information about important application events.

Notifications can include:

Notifications may be delivered through supported notification channels, including in-app notifications, email, and WhatsApp when configured.

* Approval requests
* Approved actions
* Executed actions
* Project risks
* High-priority leads
* Overdue payments
* Customer issues
* Deadlines
* Intelligent alerts

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

A typical approval workflow may produce records such as:

```text
Required - Pending
        ↓
Approved
        ↓
Approved - Executed
```

Administrators should review unusual or unexpected records.

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
     ↓
Google OAuth Login
     ↓
User Authorization
     ↓
OAuth Callback
     ↓
Credentials Stored in Session
     ↓
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

The WhatsApp notification service is implemented using the Meta WhatsApp Cloud API.

The following production environment variables are required for real WhatsApp delivery:

* WHATSAPP_API_URL
* WHATSAPP_ACCESS_TOKEN
* WHATSAPP_PHONE_NUMBER_ID

The WhatsApp service includes configuration validation and delivery error handling.

Real Meta WhatsApp message delivery remains pending until valid Meta WhatsApp Cloud API credentials are configured.

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
     ↓
Git Commit
     ↓
Git Push
     ↓
GitHub
     ↓
Render Build
     ↓
Render Deployment
     ↓
Production Verification
```

After deployment, administrators should verify that the application is working correctly.

---

# 23. Deployment Verification

After a new deployment, verify:

### Backend

* Django service is running.
* Gunicorn starts successfully.
* Database migrations are successful.
* API endpoints are reachable.
* No configuration errors are present.

### Frontend

* React application loads.
* Login works.
* API requests reach the backend.
* Dashboard loads and retrieves data from the /api/dashboard/ endpoint.
* AI Chat works.

### Integrations

* Google Calendar works.
* Email functionality works.
* Business tools respond correctly.

### Security

* JWT authentication works.
* Protected APIs require authentication.
* Approval workflow works.
* Audit records are generated.

---

# 24. Troubleshooting Procedure

When a production problem occurs, follow this sequence:

### Step 1 — Identify the Problem

Determine whether the issue affects:

* Frontend
* Backend
* Authentication
* AI agents
* Database
* Tool execution
* External integration
* Automation

### Step 2 — Check Logs

Review the backend and deployment logs.

Look for:

* Python exceptions
* Django errors
* API errors
* Authentication errors
* Integration errors
* Tool execution errors

### Step 3 — Test the API

Test the relevant endpoint independently.

For example:

```http
GET /api/hello/
```

### Step 4 — Check Authentication

Verify that the JWT access token is valid.

### Step 5 — Check Configuration

Verify relevant environment variables and external service configuration.

### Step 6 — Retest

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
