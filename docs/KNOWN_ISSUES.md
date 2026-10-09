# Vetri AI Multi-Agent

## Known Issues

**Project:** Vetri AI Multi-Agent Business Operations Assistant

---

# 1. Introduction

This document records the current known limitations, configuration dependencies, operational considerations, and areas requiring additional validation in the Vetri AI Multi-Agent application.

The application is functional across its major business workflows. The items documented below should not be interpreted as failures of the overall platform unless specifically stated.

Some items are configuration-dependent, while others represent areas for continued production hardening and testing.

---

# 2. Google Calendar OAuth Configuration

Google Calendar integration depends on correct OAuth 2.0 configuration.

The configured redirect URI in Google Cloud must exactly match the callback URL used by the deployed backend.

**Callback endpoint:**

```text
/api/calendar/oauth2callback/
```

The production OAuth redirect URI must be registered using the deployed backend domain.

An incorrect redirect URI, OAuth configuration, or credential configuration may prevent Google Calendar authorization from completing successfully.

---

# 3. Google OAuth Testing Mode

When the Google OAuth application is configured in testing mode, only configured test users may be able to authorize the application.

An account that is not configured as an allowed test user may receive an access-denied or authorization-related error.

This is an OAuth configuration limitation rather than an application failure.

---

# 4. Google Calendar Credential Availability

Calendar operations depend on valid Google Calendar OAuth credentials being available to the application.

If credentials are missing, expired, invalid, or unavailable in the current application session, Calendar retrieval may fail.

The application should report the failure through the appropriate error-handling path rather than assuming that Calendar data is always available.

Production verification should confirm that the deployed environment has the required Google Calendar configuration.

---

# 5. Email Parameter Validation

Email actions require valid execution parameters, including a recipient.

For example, attempting to execute an email action without a recipient may result in an error similar to:

```json
{
    "status": "error",
    "message": "Recipient is required."
}
```

This is expected validation behavior.

The approval and audit mechanisms can record the execution result so that failed operations can be investigated.

---

# 6. Audit Log Access Control

Audit logs contain operational information and may contain sensitive business activity.

The audit-log API and related views should continue to be reviewed as part of security hardening to ensure that only appropriately authorized users can access audit records.

**Endpoint:**

```text
GET /api/audit-logs/
```

The final production security review should confirm authentication and authorization behavior for audit-log access.

---

# 7. Calendar Endpoint Security Review

The Google Calendar login, OAuth callback, and Calendar test endpoints require careful security review because OAuth flows have different authentication requirements from normal authenticated API requests.

The relevant endpoints include:

```text
GET /api/calendar/login/
GET /api/calendar/oauth2callback/
GET /api/calendar/test/
```

The OAuth callback must remain accessible to complete the OAuth flow, while sensitive Calendar operations should remain appropriately protected.

Final production verification should confirm that the OAuth flow works without exposing unauthorized Calendar data or operations.

---

# 8. LLM Provider Dependency

Vetri AI currently uses a Groq-based LLM integration.

AI-generated responses depend on:

* Valid Groq API credentials
* Provider availability
* API quota and limits
* Network connectivity
* Model availability
* Request timeout behavior

If the external LLM provider is unavailable or the configured quota is exhausted, AI-generated responses may be degraded or unavailable.

The application includes fallback and error-handling behavior where supported, but external LLM availability remains an operational dependency.

---

# 9. RAG and Knowledge Retrieval Limitations

Knowledge retrieval depends on the quality and availability of the configured knowledge-base data.

Possible limitations include:

* Missing knowledge documents
* Incomplete business information
* Poorly matched retrieval results
* Ambiguous user questions
* Insufficient source information
* Retrieval relevance limitations

Future improvements may further increase retrieval accuracy, ranking quality, and source grounding.

---

# 10. Multi-Agent Routing and Context Limitations

The AI Orchestrator supports specialized agent routing, contextual follow-ups, multi-agent workflows, and shared request context.

However, highly ambiguous requests may still require clarification.

For example:

```text
Show my summary
```

provides less context than:

```text
Show my sales summary
```

The system can request clarification when the intended business domain or reference cannot be determined reliably.

Users should provide sufficient context when asking complex or ambiguous business questions.

---

# 11. Tool Execution Failures

An agent may correctly identify a tool or business action while the actual tool execution fails.

Possible causes include:

* Missing parameters
* Invalid business data
* Permission restrictions
* Authentication problems
* Configuration errors
* External service failures
* Network failures
* Tool-specific validation errors

Tool execution results should be reviewed when an operation fails.

The Tool Registry, permission checks, approval workflow, and error handling are intended to reduce unauthorized or invalid operations.

---

# 12. Automation Data Dependency

Automated reminders and intelligent alerts depend on available business data and matching conditions.

If no records satisfy the configured conditions, the automation endpoint may legitimately return zero results.

For example:

```json
{
    "status": "success",
    "total_reminders": 0,
    "message": "0 new automated reminders generated."
}
```

A zero-result response does not necessarily indicate an application failure.

The same principle applies to intelligent alerts.

---

# 13. External Service Dependency

Some platform functionality depends on external services.

Possible causes of external-service failures include:

* Service downtime
* Invalid credentials
* Expired OAuth credentials
* Network problems
* API quota limits
* Permission restrictions
* Incorrect configuration
* Third-party API changes

External-service failures should be investigated through application logs and the corresponding service configuration.

The application should not assume that an external provider is always available.

---

# 14. Internal Business Data and Mock Integrations

Several business capabilities use internal or mock business data rather than requiring live third-party systems.

This includes capabilities such as:

* CRM-related business data
* Project-management data
* GitHub-related business information
* Cloud-storage-related capabilities
* Other internal business operations

These implementations are intentional for the current project architecture.

Live external APIs should only be introduced where there is a clear future business requirement.

Therefore, the absence of a live third-party API for these capabilities should not be treated as an application defect.

---

# 15. WhatsApp Delivery Dependency

The WhatsApp application-side functionality and reliability handling are implemented, but real Meta WhatsApp Cloud API delivery depends on Meta configuration.

Required production configuration includes values such as:

```text
WHATSAPP_API_URL
WHATSAPP_ACCESS_TOKEN
WHATSAPP_PHONE_NUMBER_ID
```

If valid Meta credentials and configuration are unavailable, real WhatsApp message delivery cannot be completed.

This is an external configuration dependency rather than a limitation of the internal WhatsApp workflow implementation.

---

# 16. Production Frontend Configuration

The frontend previously contained a hard-coded local backend API URL.

The local source code has been corrected to use the centralized API configuration, and the production environment configuration contains the deployed backend URL.

The production build has also been verified to contain the Render backend URL.

However, the corrected frontend has not yet been deployed at the time of this documentation audit.

Therefore, final production verification remains pending.

The expected production API base is:

```text
https://vetri-ai-backend-i3pw.onrender.com/api
```

The deployed application must be re-tested after the corrected frontend is pushed and deployed.

---

# 17. Deployment Configuration Dependency

Production operation depends on correct configuration of:

* Environment variables
* Allowed hosts
* CORS
* Database configuration
* Gunicorn
* LLM credentials
* OAuth credentials
* Email configuration
* WhatsApp configuration where applicable
* Other required service configuration

A configuration problem can cause functionality to work locally but fail after deployment.

Production configuration should therefore be validated after every significant deployment change.

---

# 18. Database Dependency

The Django application depends on a correctly configured and available database.

Database connectivity, migration, or configuration problems may affect:

* User data
* Conversations
* Notifications
* Approvals
* Audit records
* Business information
* Application state

Database migrations should be applied after model changes where required.

The production database configuration must be verified separately from the local SQLite development environment.

---

# 19. Browser and Network Dependency

The React frontend requires network access to communicate with the Django backend.

API requests may fail when:

* The backend is unavailable
* The frontend API URL is incorrect
* CORS is incorrectly configured
* The user's network is unavailable
* A required external service cannot be reached

Browser developer tools and backend logs should be checked when diagnosing frontend-to-backend communication problems.

---

# 20. Security Hardening and Regression Testing

The platform has authentication, permissions, approval workflows, and audit logging, but security validation remains an ongoing requirement.

Additional production hardening should include:

* Unauthorized-access testing
* Role and permission regression testing
* Object-level authorization testing
* API endpoint protection review
* Audit-log access review
* CORS review
* Secret-management review
* Rate-limiting review
* Input-validation testing
* Integration failure testing
* Security regression testing

Security testing should be repeated after significant permission, API, or deployment changes.

---

# 21. Testing Limitations

Major application workflows have been tested across multiple areas, including:

* Authentication
* AI Chat
* Contextual conversation handling
* Specialized agents
* Multi-agent workflows
* Permission enforcement
* Approval workflow
* Notifications
* Audit logging
* Reporting
* Automation
* Google Calendar workflows
* Email functionality
* Management workflows
* Daily business briefing

Additional testing remains valuable for:

* Production-only configuration
* Security edge cases
* External service failures
* LLM failure conditions
* RAG evaluation
* High-load scenarios
* Browser/device compatibility
* Long-running automation
* Advanced failure recovery

Testing status should be updated as new regression testing is completed.

---

# 22. Production Verification Status

Some production-related documentation cannot be considered final until the corrected frontend configuration has been deployed.

The remaining production verification should confirm:

* Frontend uses the deployed backend URL
* Authentication works in production
* `/api/auth/me/` succeeds with a valid production session
* AI Chat works in production
* Conversations work in production
* Calendar OAuth and retrieval work in production
* Required environment variables are available
* Database connectivity is stable
* CORS and allowed hosts are correct
* No localhost API URL remains in the deployed frontend
* Critical workflows operate correctly after deployment

This verification should be completed before declaring the final deployment documentation complete.

---

# 23. Known Issue Tracking

This document should be reviewed whenever:

* A new limitation is discovered
* An integration changes
* A deployment issue is identified
* A security concern is discovered
* A configuration dependency changes
* A previously known issue is resolved

Resolved issues should be removed from this document or moved to an appropriate project change log.

Known issues should describe actual current limitations and should not contain already-resolved development problems.

---

# 24. Summary

Vetri AI Multi-Agent is functional across its major business workflows and provides a foundation for AI-assisted business operations.

The primary current considerations are:

* Google Calendar OAuth configuration and credential availability
* LLM provider availability and quota
* RAG data and retrieval quality
* Tool execution failure conditions
* External service availability
* WhatsApp Meta configuration for real delivery
* Production frontend deployment verification
* Database and deployment configuration
* Security hardening and regression testing

These considerations should be monitored during deployment, production validation, testing, and future development.

They do not prevent the core platform from functioning, but they should be addressed or verified before considering the production deployment fully finalized.
