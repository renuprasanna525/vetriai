# Vetri AI Multi-Agent

## User Guide

**Project:** Vetri AI Multi-Agent Business Operations Assistant

**Frontend:** React

**Backend:** Django REST Framework

**Authentication:** JWT

---

# 1. Introduction

Vetri AI Multi-Agent is an AI-powered business operations assistant that provides a centralized AI Chat interface for accessing business information and performing supported business operations.

The platform uses specialized business agents, an AI Orchestrator, permissions, tools, approvals, notifications, automation, knowledge retrieval, and audit logging to process business requests.

The platform supports business capabilities including:

* Finance
* Sales
* Projects
* HR
* Reporting
* Calendar
* Marketing
* Developer operations
* QA
* Operations
* GitHub-related business information
* Notifications
* Approvals
* Automation
* Intelligent alerts
* Business briefings
* Knowledge retrieval

The exact operations available to a user depend on the user's role and permissions.

---

# 2. Getting Started

To use Vetri AI Multi-Agent:

1. Open the deployed application.
2. Log in with your username and password.
3. After successful authentication, the application opens the authenticated interface.
4. Use the available navigation options to access supported features.
5. Use AI Chat to ask business questions or request supported operations.
6. Review notifications when approvals or important business alerts are generated.

---

# 3. Login

The Login page is used to authenticate users.

Enter:

* Username
* Password

Then select **Login**.

After successful authentication, the application uses JWT-based authentication for protected API requests.

Users should keep their credentials and authentication tokens private.

If login fails, verify the username and password and retry.

---

# 4. Dashboard

The Dashboard provides an overview of available business information.

Depending on the user's role and available business data, the application may display information such as:

* Revenue
* Expenses
* Profit
* Sales leads
* Customers
* Follow-ups
* Orders
* Pending orders
* Employees
* Leave information
* Attendance information
* Projects
* Project status
* Delayed projects
* Tasks
* Deadlines
* Business risks
* Other supported business indicators

The Dashboard provides a quick overview, while AI Chat can be used for more detailed business questions.

---

# 5. AI Chat

AI Chat is the primary interface for interacting with Vetri AI.

Users can enter natural-language business questions or requests.

Example:

```text
Show my finance summary
```

The request is sent to the Django backend and processed by the AI Orchestrator.

The Orchestrator evaluates the request, checks the applicable permissions, identifies the appropriate agent or agents, retrieves the required business information, and returns a response.

Depending on the request, the system may also use tools, knowledge retrieval, approval workflows, or multiple specialized agents.

---

# 6. Contextual Conversations

Vetri AI supports conversation context and contextual follow-up questions.

For example:

```text
Show my sales summary
```

followed by:

```text
How many of those are pending?
```

The system can use the previous conversation context to understand what the user is referring to.

If the reference is ambiguous, the system may ask a clarification question.

For example, if both pending follow-ups and pending orders are possible references, the application may ask which one the user means.

Users can then provide a clarification such as:

```text
The orders.
```

The system can continue processing the request using the clarified context.

---

# 7. New Chat and Conversation History

Authenticated users can manage separate conversations.

Supported conversation functionality includes:

* Creating a new conversation
* Continuing an existing conversation
* Viewing previous messages
* Maintaining conversation context
* Using contextual follow-up questions
* Keeping separate conversation histories

Conversation records are associated with the authenticated user.

Users should only be able to access their own authorized conversation records.

Starting a new conversation can be used when the user wants to begin a different business topic without relying on the previous conversation context.

---

# 8. Example AI Chat Requests

Users can ask questions such as:

### Finance

```text
Show my finance summary
```

### Sales

```text
How many new sales leads do we have?
```

### Projects

```text
Show delayed projects
```

### HR

```text
Who is currently on leave?
```

### Reporting

```text
Show the latest business report
```

### Calendar

```text
Show my calendar events
```

### Multiple Business Areas

```text
Show my sales leads and finance summary
```

### Contextual Follow-up

```text
Tell me about the pending follow-ups.
```

followed by:

```text
Which customer has been waiting the longest?
```

The system uses the conversation context and available business information to process related questions.

---

# 9. Specialized AI Agents

Vetri AI uses specialized agents for different business domains.

Current registered business agents include:

* Calendar Agent
* HR Agent
* Sales Agent
* Project Agent
* Finance Agent
* Marketing Agent
* Developer Agent
* QA Agent
* Operations Agent
* Reporting Agent
* GitHub Agent

The AI Orchestrator determines which agent or agents should handle a request.

A request may be processed by a single agent or may require collaboration between multiple agents.

---

# 10. User Roles

Vetri AI uses role-based access control.

A user's role determines which business operations and information the user may access.

Example roles include:

* Admin
* Manager
* HR
* Sales
* Employee

The exact permissions available to each role are controlled by the application's permission configuration.

Users should only receive access to operations permitted for their role.

---

# 11. Permissions

The Permission Engine controls access to restricted business operations.

Before performing a protected operation, the system can verify whether the authenticated user has the required permission.

Permissions may control access to areas such as:

* Finance
* Sales
* HR
* Projects
* Business data
* Calendar operations
* Sensitive actions
* Tools
* Administrative functionality

If a user does not have permission for a requested operation, the application should deny the operation rather than executing it.

---

# 12. Google Calendar

Vetri AI supports Google Calendar integration using OAuth 2.0.

## Connecting Google Calendar

The general authorization flow is:

```text
Open Calendar Login
        ↓
Google Authentication
        ↓
Grant Requested Calendar Permission
        ↓
OAuth Callback
        ↓
Calendar Credentials Available
        ↓
Supported Calendar Operations
```

The production OAuth configuration must use the correct deployed backend callback URL.

The callback endpoint is:

```text
/api/calendar/oauth2callback/
```

Google OAuth configuration must be valid before Calendar operations can be used successfully.

---

# 13. Notifications

The Notifications functionality provides users with important system and business messages.

Notifications may be generated for:

* Approval requests
* Approved actions
* Executed actions
* Project risks
* Important sales conditions
* Overdue payments
* Customer issues
* Deadlines
* Intelligent business alerts
* Other supported business events

Notifications are associated with the authenticated user.

Users should regularly review notifications, particularly when sensitive actions require approval.

---

# 14. Approval Workflow

Some operations are considered sensitive and may require approval before execution.

Depending on the configured workflow, sensitive operations may include actions such as:

* Sending emails
* Sending bulk communications
* Approving leave
* Financial changes
* Deployment-related operations
* Data deletion or other high-risk actions

The general workflow is:

```text
User Request
     ↓
AI Orchestrator
     ↓
Specialized Agent
     ↓
Sensitive Action
     ↓
Approval Required
     ↓
Notification
     ↓
User Reviews Request
     ↓
Approve / Edit / Cancel
     ↓
Permission / Validation Checks
     ↓
Tool Execution
     ↓
Execution Result
     ↓
Notification / Audit Record
```

The exact approval behavior depends on the operation and configured permissions.

---

# 15. Reviewing an Approval

When an approval request is generated:

1. Open the relevant notification or approval area.
2. Identify the pending approval.
3. Review the requested action.
4. Check the parameters carefully.
5. Verify recipients or other sensitive information.
6. Choose the appropriate action.

Supported approval actions may include:

* Approve
* Edit
* Cancel

Do not approve a request if its parameters are incorrect or unexpected.

---

# 16. Approval Example

A sensitive email operation may generate an approval request containing information similar to:

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

The exact fields displayed may depend on the operation.

The action should not be executed until the required approval and validation steps are completed.

---

# 17. Audit Logging

Important system operations are recorded through audit logging.

Audit records may include information such as:

* User
* Agent
* Request
* Data accessed
* Tool
* Action
* Approval status
* Result
* Timestamp

Audit logging provides traceability for important business operations, tool execution, and approval workflows.

Access to audit information should follow the application's security and authorization rules.

---

# 18. Automation

Vetri AI provides automation functionality for generating automated reminders and intelligent alerts.

## Automated Reminders

Reminders can be generated from available business information.

Examples include:

* Upcoming deadlines
* Pending follow-ups
* Pending business tasks
* Other time-sensitive activities

A successful automation run may generate multiple reminders, depending on the available business data and matching conditions.

A successful run that produces zero reminders is not necessarily an error.

## Intelligent Alerts

Intelligent alerts identify important business conditions.

Examples include:

* Project risks
* Approaching deadlines
* Important sales conditions
* Overdue payments
* Customer issues
* Other business risks

Alert generation depends on the available business information and configured rules.

---

# 19. Reporting and Business Briefings

Vetri AI provides reporting capabilities for summarizing business information.

The Reporting functionality can combine information from supported business areas and present a consolidated business view.

The platform also supports management-oriented priority and attention information and daily business briefing capabilities.

Users can use AI Chat to request supported reports, summaries, or business status information.

Example:

```text
Give me the latest business report.
```

---

# 20. WhatsApp

The application includes WhatsApp-related functionality and reliability handling.

Real Meta WhatsApp Cloud API message delivery depends on valid Meta configuration and credentials.

Production delivery requires the appropriate Meta configuration, including values such as:

```text
WHATSAPP_API_URL
WHATSAPP_ACCESS_TOKEN
WHATSAPP_PHONE_NUMBER_ID
```

If these values are not configured, real external WhatsApp delivery cannot be completed.

---

# 21. How to Use AI Chat Effectively

For better results, users should provide clear and specific requests.

### General request

```text
Show my current project status
```

### More specific request

```text
Show delayed projects and upcoming deadlines
```

### Business-domain request

```text
Show my new sales leads
```

### Multiple-agent request

```text
Show my sales leads and finance summary
```

### Contextual follow-up

```text
How many of those are pending?
```

If a request is ambiguous, Vetri AI may ask the user to clarify the intended reference.

Clear requests help the AI Orchestrator select the appropriate business functionality.

---

# 22. Sensitive Actions

Users should carefully review sensitive actions before approving them.

Before approval, verify:

* Agent name
* Tool name
* Action
* Parameters
* Recipient information where applicable
* Expected result

Do not approve an action if:

* The recipient is incorrect.
* The requested operation is unexpected.
* The parameters are incorrect.
* The operation appears unauthorized.

When in doubt, cancel the approval and contact an administrator.

---

# 23. Error Messages

The application may display an error when:

* Required information is missing.
* Authentication fails.
* A resource does not exist.
* The user does not have permission.
* An external service is unavailable.
* An OAuth configuration is incorrect.
* A tool cannot execute an action.
* An LLM provider is unavailable.
* A network or deployment configuration problem occurs.

Example:

```json
{
    "status": "error",
    "message": "Recipient is required."
}
```

Users should correct the missing information and retry where appropriate.

For configuration or external-service errors, an administrator may need to review the application logs and environment configuration.

---

# 24. Logout

Users should log out when they have finished using the application, especially when using a shared or public computer.

Do not leave an authenticated session unattended on a shared device.

---

# 25. User Security Guidelines

Users should:

* Keep usernames and passwords private.
* Never share JWT tokens or authentication credentials.
* Never share LLM, OAuth, email, or other service credentials.
* Review sensitive approval requests carefully.
* Verify recipients before approving communication actions.
* Avoid approving unknown or unexpected operations.
* Log out from shared devices.
* Report unexpected system behavior to an administrator.
* Avoid entering sensitive credentials into AI Chat.

---

# 26. Typical User Workflow

A normal information-request workflow is:

```text
Login
  ↓
Dashboard
  ↓
AI Chat
  ↓
User Business Request
  ↓
AI Orchestrator
  ↓
Permission Check
  ↓
Specialized Agent
  ↓
Business Data / Knowledge / Tool
  ↓
AI Response
```

For a contextual follow-up:

```text
Previous Conversation
  ↓
New User Question
  ↓
Context Resolution
  ↓
Agent / Business Operation
  ↓
Response
```

For a sensitive operation:

```text
Login
  ↓
AI Chat
  ↓
Sensitive Request
  ↓
Permission Check
  ↓
Approval Request
  ↓
Notification
  ↓
User Review
  ↓
Approve / Edit / Cancel
  ↓
Validation
  ↓
Tool Execution
  ↓
Result
  ↓
Notification / Audit Record
```

---

# 27. Best Practices

For effective use of Vetri AI:

1. Use clear natural-language requests.
2. Specify the business area when necessary.
3. Provide enough context for follow-up questions.
4. Review AI responses before making important business decisions.
5. Carefully review approval requests.
6. Verify sensitive action parameters.
7. Monitor notifications regularly.
8. Use conversation history when continuing a related task.
9. Start a new conversation when beginning an unrelated topic.
10. Contact an administrator when an unexpected error occurs.
11. Never share passwords, JWT tokens, API keys, or OAuth credentials through AI Chat.

---

# 28. Troubleshooting Quick Reference

| Problem                         | Recommended action                                                |
| ------------------------------- | ----------------------------------------------------------------- |
| Login fails                     | Verify username/password and check authentication availability    |
| AI response unavailable         | Check LLM/provider configuration and service availability         |
| Permission denied               | Confirm that the user's role has the required permission          |
| Calendar unavailable            | Check Google OAuth configuration and credentials                  |
| Email action fails              | Check required parameters, especially recipient information       |
| Approval not executing          | Review approval status and required permissions                   |
| Automation returns zero results | Verify whether matching business conditions exist                 |
| Frontend cannot reach backend   | Check production API URL, CORS, network, and backend availability |
| External integration fails      | Check credentials, configuration, service availability, and logs  |
| Unexpected AI routing           | Provide a more specific business request or clarify the question  |

---

# 29. Important Configuration Notes

The following configuration areas may affect application functionality:

* JWT authentication configuration
* Django environment configuration
* Database configuration
* CORS and allowed hosts
* Groq API configuration
* Google Calendar OAuth configuration
* Email configuration
* WhatsApp/Meta configuration where applicable
* Production frontend API configuration

Users should contact an administrator rather than modifying production configuration themselves.

---

# 30. Summary

Vetri AI Multi-Agent provides a centralized interface for interacting with multiple business functions through AI-assisted workflows.

Users can:

* Log in securely
* View business information
* Ask questions through AI Chat
* Use contextual conversations
* Access specialized agents
* Manage conversation history
* Review notifications
* Approve sensitive actions
* Use Google Calendar integration
* Use supported email functionality
* Receive automated reminders
* Receive intelligent business alerts
* Access business reports and briefings
* Benefit from permission-controlled business operations
* Use supported knowledge and retrieval capabilities

The platform combines AI agents, an orchestration layer, business tools, permissions, approvals, notifications, automation, knowledge retrieval, and audit logging to support business operations through a centralized interface.

Users should follow the security guidelines in this guide and contact an administrator when configuration, authentication, integration, or unexpected system errors occur.
