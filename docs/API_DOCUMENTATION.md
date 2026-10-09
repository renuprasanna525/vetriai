# Vetri AI Multi-Agent

## API Documentation

**Project:** Vetri AI Multi-Agent Business Operations Assistant
**Backend:** Django + Django REST Framework
**Frontend:** React
**Authentication:** JWT (JSON Web Token)

---

# 1. API Base URL

## Local Development

```text
http://127.0.0.1:8000/api/
```

## Production

Use the deployed backend URL followed by:

```text
/api/
```

---

# 2. Authentication

The application uses JWT authentication for protected REST API endpoints.

## Login

**Endpoint**

```http
POST /api/auth/login/
```

**Purpose**

Authenticates a user and returns access and refresh tokens.

**Request**

```json
{
    "username": "your_username",
    "password": "your_password"
}
```

**Response**

```json
{
    "refresh": "JWT_REFRESH_TOKEN",
    "access": "JWT_ACCESS_TOKEN"
}
```

The access token is used for authenticated API requests.

---

## Refresh Token

**Endpoint**

```http
POST /api/auth/refresh/
```

**Purpose**

Generates a new access token using a valid refresh token.

**Request**

```json
{
    "refresh": "JWT_REFRESH_TOKEN"
}
```

**Response**

```json
{
    "access": "NEW_ACCESS_TOKEN"
}
```

---

# 3. Authentication Header

Authenticated API requests use the following HTTP header:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

Example:

```http
Authorization: Bearer eyJhbGciOiJIUzI1Ni...
```

---

# 4. General API

## Hello API

**Endpoint**

```http
GET /api/hello/
```

**Authentication:** Not required.

**Purpose**

Basic API connectivity test.

**Example Response**

```json
{
    "status": "success",
    "message": "Hello from Vetri AI Backend",
    "project": "Vetri AI Multi-Agent"
}
```

---

# 5. AI Chat API

## Chat

**Endpoint**

```http
POST /api/chat/
```

**Authentication:** Required.

**Purpose**

Sends a user request to Vetri AI. The request is processed by the AI Orchestrator and routed to the appropriate specialized agent.

**Request**

```json
{
    "message": "Show my finance summary"
}
```

**Optional Conversation ID**

```json
{
    "message": "Show my project status",
    "conversation_id": 1
}
```

**Response**

```json
{
    "status": "success",
    "response": "...",
    "conversation_id": 1
}
```

The response also includes metadata such as the source agent, update time, and confidence information.

The AI system can route requests to specialized agents including:

* Finance Agent
* Sales Agent
* CRM Agent
* Project Agent
* Reporting Agent
* HR Agent
* Calendar Agent
* Marketing Agent
* Developer Agent
* Customer Support Agent
* QA Agent
* Operations Agent
* GitHub Agent
* Cloud Storage Agent

---

# 6. Current User API

## Get Current User

**Endpoint**

```http
GET /api/auth/me/
```

**Authentication:** Required.

**Purpose**

Returns information about the currently authenticated user.

---

# 7. Dashboard API

## Dashboard

**Endpoint**

```http
GET /api/dashboard/
```

**Authentication:** Required.

**Purpose**

Returns business dashboard information.

The dashboard can include:

* Revenue
* Sales leads
* Customers
* Follow-ups
* Orders
* Pending orders
* Employees
* Employees on leave
* Attendance
* Leave information
* Projects
* Project status
* Delayed projects
* Deadlines
* Tasks

---

# 8. User Roles API

## User Roles

**Endpoint**

```http
GET /api/user-roles/
```

**Authentication:** Required.

**Purpose**

Returns user-role information used by the application's role management system.

---

# 9. Permissions API

## Permissions

**Endpoint**

```http
GET /api/permissions/
```

**Authentication:** Required.

**Purpose**

Returns permission information provided by the permission engine.

The permission engine controls whether users are allowed to perform specific business operations.

---

# 10. Agent Registry API

## Agents

**Endpoint**

```http
GET /api/agents/
```

**Authentication:** Required.

**Purpose**

Returns the registered AI agents available in the system.

The current agent registry includes:

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

---

# 11. Conversation History API

## List Conversations

**Endpoint**

```http
GET /api/conversations/
```

**Authentication:** Required.

**Purpose**

Returns conversations belonging to the authenticated user.

---

## Create Conversation

**Endpoint**

```http
POST /api/conversations/
```

**Authentication:** Required.

**Purpose**

Creates a new conversation for the authenticated user.

---

## Conversation Details

**Endpoint**

```http
GET /api/conversations/<conversation_id>/
```

**Authentication:** Required.

**Purpose**

Returns the messages and details of a specific conversation.

**Example**

```http
GET /api/conversations/1/
```

A user can access only their own conversation records.

---

# 12. Google Calendar Integration

Vetri AI integrates with Google Calendar using OAuth 2.0.

## Calendar Login

**Endpoint**

```http
GET /api/calendar/login/
```

**Authentication:** Not enforced by the current API view.

**Purpose**

Starts the Google Calendar OAuth authentication flow.

---

## OAuth Callback

**Endpoint**

```http
GET /api/calendar/oauth2callback/
```

**Authentication:** Not enforced by the current API view.

**Purpose**

Receives the callback from Google after successful OAuth authentication and stores the calendar credentials in the user's session.

---

## Calendar Test

**Endpoint**

```http
GET /api/calendar/test/
```

**Authentication:** Not enforced by the current API view.

**Purpose**

Tests the Google Calendar API connection using the credentials stored in the session.

A successful response confirms that the Google Calendar integration is working.

---

# 13. Approval Workflow API

Sensitive actions require approval before execution.

Current sensitive actions include:

* Sending emails
* Sending bulk messages
* Approving leave
* Financial changes
* Deployment
* Data deletion

All approval endpoints require authentication.

---

## List Approvals

**Endpoint**

```http
GET /api/approvals/
```

**Authentication:** Required.

**Purpose**

Returns approval actions.

Optional status filter:

```http
GET /api/approvals/?status=pending
```

---

## Create Approval Preview

**Endpoint**

```http
POST /api/approvals/preview/
```

**Authentication:** Required.

**Purpose**

Creates an approval request for a sensitive action.

**Request**

```json
{
    "agent_name": "Sales Agent",
    "tool_name": "email_tool",
    "action": "send_email",
    "parameters": {
        "subject": "Test Email",
        "message": "Hello",
        "recipient": "example@example.com"
    }
}
```

The parameters object must be provided as a dictionary.

---

## Get Approval Details

**Endpoint**

```http
GET /api/approvals/<action_id>/
```

**Authentication:** Required.

**Example**

```http
GET /api/approvals/1/
```

**Purpose**

Returns details of a specific approval action.

---

## Approve Action

**Endpoint**

```http
POST /api/approvals/<action_id>/approve/
```

**Authentication:** Required.

**Purpose**

Approves a pending action and allows the associated tool to execute.

**Example**

```http
POST /api/approvals/1/approve/
```

---

## Edit Approval

**Endpoint**

```http
PUT /api/approvals/<action_id>/edit/
```

**Authentication:** Required.

**Purpose**

Updates the parameters of a pending approval request.

**Example Request**

```json
{
    "parameters": {
        "subject": "Updated Subject",
        "message": "Updated message",
        "recipient": "example@example.com"
    }
}
```

---

## Cancel Approval

**Endpoint**

```http
POST /api/approvals/<action_id>/cancel/
```

**Authentication:** Required.

**Purpose**

Cancels a pending approval request.

---

# 14. Notifications API

Notifications are generated for important business and approval events.

All notification endpoints require authentication.

Notifications are restricted to the authenticated user's own records.

## List Notifications

**Endpoint**

```http
GET /api/notifications/
```

**Authentication:** Required.

**Purpose**

Returns notifications belonging to the authenticated user.

Notifications can include:

* Approval required
* Action approved and executed
* Project risks
* High-priority leads
* Overdue payments
* Customer issues
* Deadlines
* Intelligent alerts

---

## Notification Details

**Endpoint**

```http
GET /api/notifications/<id>/
```

**Authentication:** Required.

**Example**

```http
GET /api/notifications/1/
```

**Purpose**

Returns a specific notification belonging to the authenticated user.

---

## Mark Notification as Read

**Endpoint**

```http
PUT /api/notifications/<id>/read/
```

**Authentication:** Required.

**Purpose**

Marks a notification as read.

**Example**

```http
PUT /api/notifications/1/read/
```

---

# 15. Audit Logs API

## List Audit Logs

**Endpoint**

```http
GET /api/audit-logs/
```

**Authentication:** Required.

**Authorization:** Requires the `view_audit_logs` permission.

**Purpose**

Returns audit records generated by important system actions.

Audit records contain:

* User
* Agent
* Request
* Data accessed
* Tool
* Action
* Approval status
* Result
* Timestamp

**Example Response**

```json
{
    "id": 3,
    "user": "renu",
    "agent": "Sales Agent",
    "request": "send_email",
    "data_accessed": "",
    "tool": "email_tool",
    "action": "send_email",
    "approval": "Approved - Executed",
    "result": "Execution result",
    "timestamp": "2026-09-06T12:14:39Z"
}
```

Audit logging provides traceability for important requests, approval actions, tool execution, and results.

---

# 16. Automation APIs

Vetri AI provides automation endpoints for generating reminders and intelligent business alerts.

Both automation endpoints require authentication.

## Generate Reminders

**Endpoint**

```http
POST /api/automation/reminders/
```

**Authentication:** Required.

**Purpose**

Generates automated reminders based on available business information.

**Example Response**

```json
{
    "status": "success",
    "total_reminders": 0,
    "message": "0 new automated reminders generated."
}
```

---

## Generate Intelligent Alerts

**Endpoint**

```http
POST /api/automation/alerts/
```

**Authentication:** Required.

**Purpose**

Generates intelligent business alerts based on business conditions such as:

* Risks
* Deadlines
* Sales leads
* Payments
* Customer issues
* Other important business conditions

**Example Response**

```json
{
    "status": "success",
    "total_alerts": 0,
    "message": "0 new intelligent alerts generated."
}
```
---

# 17. API Endpoint Summary

| Feature                | Method | Authentication | Endpoint                        |
| ---------------------- | ------ | -------------- | ------------------------------- |
| Login                  | POST   | No             | `/api/auth/login/`              |
| Refresh Token          | POST   | No             | `/api/auth/refresh/`            |
| Hello                  | GET    | No             | `/api/hello/`                   |
| AI Chat                | POST   | Yes            | `/api/chat/`                    |
| Current User           | GET    | Yes            | `/api/auth/me/`                 |
| Dashboard              | GET    | Yes            | `/api/dashboard/`               |
| User Roles             | GET    | Yes            | `/api/user-roles/`              |
| Permissions            | GET    | Yes            | `/api/permissions/`             |
| Agents                 | GET    | Yes            | `/api/agents/`                  |
| List Conversations     | GET    | Yes            | `/api/conversations/`           |
| Create Conversation    | POST   | Yes            | `/api/conversations/`           |
| Conversation Details   | GET    | Yes            | `/api/conversations/<id>/`      |
| Calendar Login         | GET    | No*            | `/api/calendar/login/`          |
| Calendar Callback      | GET    | No*            | `/api/calendar/oauth2callback/` |
| Calendar Test          | GET    | No*            | `/api/calendar/test/`           |
| Approvals              | GET    | Yes            | `/api/approvals/`               |
| Approval Preview       | POST   | Yes            | `/api/approvals/preview/`       |
| Approval Details       | GET    | Yes            | `/api/approvals/<id>/`          |
| Approve Action         | POST   | Yes            | `/api/approvals/<id>/approve/`  |
| Edit Approval          | PUT    | Yes            | `/api/approvals/<id>/edit/`     |
| Cancel Approval        | POST   | Yes            | `/api/approvals/<id>/cancel/`   |
| Notifications          | GET    | Yes            | `/api/notifications/`           |
| Notification Details   | GET    | Yes            | `/api/notifications/<id>/`      |
| Mark Notification Read | PUT    | Yes            | `/api/notifications/<id>/read/` |
| Audit Logs             | GET    | Yes            | `/api/audit-logs/`              |
| Generate Reminders     | POST   | Yes            | `/api/automation/reminders/`    |
| Generate Alerts        | POST   | Yes            | `/api/automation/alerts/`       |

`*` Authentication is not currently enforced by the corresponding Calendar view.

---

# 18. Security

The application uses JWT authentication for protected API operations.

Security mechanisms include:

* JWT-based authentication
* Role-based access control
* Permission Engine
* User-specific conversation access
* User-specific notification access
* Approval workflow for sensitive actions
* Audit logging
* OAuth authentication for Google Calendar

Sensitive actions are protected by the approval workflow before execution.

Important system actions are recorded through the audit logging system.

---

# 19. AI Agent Architecture

The AI system follows a multi-agent architecture.

A typical request follows:

```text
User
  ↓
React AI Chat
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
  ↓
User
```

For sensitive actions:

```text
User Request
     ↓
AI Orchestrator
     ↓
Agent
     ↓
Tool
     ↓
Approval Required
     ↓
Notification
     ↓
User Approval
     ↓
Tool Execution
     ↓
Notification
     ↓
Audit Log
```

This architecture separates AI routing, business agents, tools, approvals, notifications, and audit tracking.

---

# 20. Error Handling

API errors generally return an appropriate HTTP status code and JSON response containing status and message information.

Example:

```json
{
    "status": "error",
    "message": "Recipient is required."
}
```

Clients should handle:

* Authentication failures
* Missing required parameters
* Validation errors
* Unauthorized access
* Integration failures
* Tool execution errors
* Invalid conversation IDs
* Invalid approval actions

Errors generated during tool execution are recorded as part of the approval and audit workflow where applicable.

---

# 21. Testing

The API and major project functionality have been tested for:

* Authentication
* JWT login
* AI Chat
* Finance Agent
* Project Agent
* Reporting Agent
* Calendar Agent
* Google Calendar OAuth
* Approval workflow
* Approval notifications
* Approval execution notifications
* Audit logging
* Automation reminders
* Intelligent alerts

Approval workflow testing verified the creation of pending approvals, approval execution, notifications, and audit records.

Additional integration-failure and AI evaluation testing remain part of the final testing phase.

---

# 22. Conclusion

Vetri AI Multi-Agent exposes Django REST APIs that connect the React frontend with:

* Authentication
* AI agents
* Business operations
* Role and permission management
* Conversation management
* Approval workflows
* Notifications
* Audit logging
* Google Calendar
* Automation services

The API architecture supports the multi-agent business operations assistant and provides a foundation for future integrations and enhancements.
