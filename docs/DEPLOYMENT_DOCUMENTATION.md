# Vetri AI Multi-Agent

## Deployment Documentation

**Project:** Vetri AI Multi-Agent Business Operations Assistant
**Frontend:** React + Vite
**Backend:** Django + Django REST Framework
**Authentication:** JWT
**Deployment Platform:** Render
**Source Control:** GitHub

---

# 1. Project Overview

Vetri AI Multi-Agent is a full-stack business operations assistant built using React on the frontend and Django REST Framework on the backend.

The application uses multiple specialized AI agents to handle different business operations.

The project structure is:

```text
Vetri_AI_Multi_Agent/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── myapp/
│   ├── approvals/
│   ├── notifications/
│   ├── audit_logs/
│   └── ...
│
├── frontend/
│   ├── package.json
│   ├── src/
│   └── ...
│
└── docs/
    ├── API_DOCUMENTATION.md
    ├── DEPLOYMENT_DOCUMENTATION.md
    ├── USER_GUIDE.md
    ├── ADMIN_GUIDE.md
    ├── KNOWN_ISSUES.md
    └── FUTURE_ENHANCEMENTS.md
```

---

# 2. Prerequisites

The following software is required for local development:

* Python
* Node.js
* npm
* Git
* Django
* Django REST Framework

The backend uses Python and Django, while the frontend uses React and Vite.

---

# 3. Backend Setup

Navigate to the backend directory:

```powershell
cd backend
```

Create and activate a Python virtual environment:

```powershell
python -m venv venv
```

Windows:

```powershell
venv\Scripts\activate
```

Install the backend dependencies:

```powershell
pip install -r requirements.txt
```

---

# 4. Backend Configuration

The Django backend requires the appropriate configuration for:

* Django settings
* JWT authentication
* CORS
* Google Calendar OAuth
* Email configuration
* Database configuration
* AI/LLM configuration where applicable

Sensitive credentials should not be committed to GitHub.

Environment variables or deployment platform environment settings should be used for production secrets.

---

# 5. Database Setup

Run Django migrations before starting the backend:

```powershell
python manage.py makemigrations
python manage.py migrate
```

Check the Django project for configuration errors:

```powershell
python manage.py check
```

A successful check should report:

```text
System check identified no issues
```

---

# 6. Run Backend Locally

Start the Django development server:

```powershell
python manage.py runserver
```

The backend is available locally at:

```text
http://127.0.0.1:8000/
```

The API base URL is:

```text
http://127.0.0.1:8000/api/
```

---

# 7. Frontend Setup

Open a separate terminal and navigate to the frontend:

```powershell
cd frontend
```

Install the React dependencies:

```powershell
npm install
```

Start the Vite development server:

```powershell
npm run dev
```

The frontend is normally available at:

```text
http://localhost:5173/
```

---

# 8. Frontend Configuration

The React frontend communicates with the Django backend through REST APIs.

The frontend should be configured with the correct backend API URL.

For local development:

```text
http://127.0.0.1:8000/api/
```

For production, the deployed Django backend URL should be used.

Production configuration should not contain localhost API URLs.

---

# 9. CORS Configuration

The Django backend must allow requests from the deployed React frontend.

During local development, the React development server runs on:

```text
http://localhost:5173
```

For production, the deployed frontend domain should be included in the Django CORS configuration.

After changing CORS settings, restart or redeploy the backend.

---

# 10. Render Backend Deployment

The Django backend is deployed using Render.

The backend deployment requires:

* GitHub repository
* Python environment
* Django project
* `requirements.txt`
* Gunicorn
* Correct Django WSGI module
* Production environment variables

---

# 11. Backend Build Configuration

The Render backend service should use the backend directory as its root directory when the repository contains separate frontend and backend folders.

A typical build command is:

```text
pip install -r requirements.txt && python manage.py migrate
```

The exact command should match the current Render service configuration.

---

# 12. Backend Start Command

The Django backend is served using Gunicorn.

The start command follows this structure:

```text
gunicorn <django_project>.wsgi:application
```

The deployed project should use the WSGI module belonging to the Django project.

For example:

```text
gunicorn backend.wsgi:application
```

The actual WSGI module configured in the Render service must match the backend project structure.

---

# 13. Environment Variables

Production secrets and configuration values should be stored in Render environment variables rather than committed to GitHub.

Typical variables may include:

```text
SECRET_KEY
DEBUG
ALLOWED_HOSTS
DATABASE_URL
GROQ_API_KEY
GROQ_MODEL
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
EMAILJS configuration
```

Only variables actually required by the deployed application should be configured.

Secret values must not be exposed in source code or documentation.

---

# 14. Google Calendar OAuth Configuration

The Google Calendar integration uses OAuth 2.0.

The Google Cloud project must contain the required OAuth credentials.

The production OAuth configuration must use the deployed backend callback URL.

The callback endpoint is:

```text
/api/calendar/oauth2callback/
```

The complete production callback URL should be registered in Google Cloud according to the deployed backend domain.

The OAuth redirect URI configured in Google Cloud must exactly match the callback URL used by the application.

A mismatch results in a Google OAuth `redirect_uri_mismatch` error.

---

# 15. Google Calendar Credentials

The Google Calendar OAuth client credentials are configured through environment variables rather than a credentials file.

The backend uses the following environment variables:

* `GOOGLE_CLIENT_ID`
* `GOOGLE_CLIENT_SECRET`
* `GOOGLE_REDIRECT_URI`

The backend dynamically creates the Google OAuth flow using these values. The Google Calendar integration requests read-only calendar access using the following scope:

```text
https://www.googleapis.com/auth/calendar.readonly
```

Credential values and secret keys must not be committed to GitHub.

For production deployment, the Google Calendar OAuth credentials and redirect URI must be securely configured through the deployment environment.

After successful Google authentication, the user's OAuth credentials are stored in the Django session and used by the backend to access the Google Calendar API.

After deployment, the Calendar login flow should be tested by:

1. Opening the Calendar login endpoint.
2. Completing Google authentication.
3. Returning to the application.
4. Testing the Calendar API connection.
5. Confirming that the user's calendar information is accessible.

---

# 16. Frontend Deployment

The React frontend can be deployed separately from the Django backend.

The frontend build process is:

```powershell
npm install
npm run build
```

The production build is generated by Vite.

The deployed frontend must communicate with the deployed Django API rather than:

```text
http://127.0.0.1:8000/
```

or:

```text
http://localhost:8000/
```

---

# 17. GitHub Deployment Workflow

The project source code is maintained using Git.

After making changes:

```powershell
git status
```

Review the modified files.

Stage the required files:

```powershell
git add .
```

Commit the changes:

```powershell
git commit -m "Update project documentation"
```

Push to the main branch:

```powershell
git push origin main
```

---

# 18. Render Automatic Deployment

When the Render service is connected to the GitHub repository, pushing changes to the configured branch can trigger a new deployment.

Typical workflow:

```text
Local Changes
     ↓
Git Add
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
Production Application
```

Documentation-only changes normally do not change application behavior, but the repository can still trigger a deployment depending on the Render service configuration.

---

# 19. Production Verification

After deployment, verify the backend.

Check the deployed API endpoint:

```text
/api/hello/
```

Verify:

* Backend is running.
* Frontend loads successfully.
* Login works.
* JWT authentication works.
* AI Chat works.
* Dashboard loads.
* Agents are accessible.
* Conversations work.
* Approval workflow works.
* Notifications work.
* Google Calendar integration works.
* Automation endpoints respond correctly.

---

# 20. Deployment Testing Checklist

## Backend

* [ ] Django deployment successful
* [ ] Gunicorn starts successfully
* [ ] Migrations completed
* [ ] No Django configuration errors
* [ ] Production environment variables configured
* [ ] CORS configured correctly
* [ ] API is reachable

## Frontend

* [ ] React build succeeds
* [ ] Production frontend loads
* [ ] Backend API URL is correct
* [ ] Login works
* [ ] AI Chat works
* [ ] Dashboard works

## Authentication

* [ ] Login endpoint works
* [ ] Access token generated
* [ ] Refresh token works
* [ ] Protected endpoints reject unauthenticated requests

## AI and Agents

* [ ] AI Chat works
* [ ] Finance Agent works
* [ ] Project Agent works
* [ ] Reporting Agent works
* [ ] Calendar Agent works
* [ ] Other registered agents are available

## Integrations

* [ ] Google Calendar OAuth works
* [ ] Calendar API connection works
* [ ] Email integration works
* [ ] Required business tools work

## Approval Workflow

* [ ] Approval request created
* [ ] Pending notification generated
* [ ] Approval can be approved
* [ ] Approved action executes
* [ ] Execution notification generated
* [ ] Audit record created

## Automation

* [ ] Reminder generation works
* [ ] Intelligent alert generation works

---

# 21. Common Deployment Issues

## Build Failure

Check:

* `requirements.txt`
* Python version
* Missing dependencies
* Incorrect Render root directory
* Incorrect build command

---

## Gunicorn Error

Verify that the start command points to the correct Django WSGI module:

```text
gunicorn <django_project>.wsgi:application
```

The module name must match the actual Django project directory.

---

## CORS Error

If the frontend cannot communicate with the backend:

1. Verify the frontend production URL.
2. Check Django CORS configuration.
3. Confirm the backend allows the production frontend origin.
4. Redeploy the backend after configuration changes.

---

## Database Error

Check:

* Database configuration
* Database URL
* Credentials
* Migrations
* Database availability

Run:

```powershell
python manage.py migrate
```

---

## Google OAuth Error

For errors such as:

```text
redirect_uri_mismatch
```

verify that the redirect URI configured in Google Cloud exactly matches the callback URL used by the deployed application.

---

# 22. Security Recommendations

Production deployments should follow these practices:

* Do not commit passwords.
* Do not commit API keys.
* Do not commit OAuth secrets.
* Do not expose private credentials in frontend code.
* Set `DEBUG=False` in production.
* Configure appropriate `ALLOWED_HOSTS`.
* Configure production CORS correctly.
* Use HTTPS in production.
* Use secure environment variables.
* Keep dependencies updated.
* Restrict sensitive actions through the approval workflow.
* Maintain audit logging for important operations.

---

# 23. Deployment Architecture

The deployed system follows this architecture:

```text
User
  ↓
React Frontend
  ↓
Production Web Server
  ↓
Django REST API
  ↓
Authentication / Permission Engine
  ↓
AI Orchestrator
  ↓
Agent Registry
  ↓
Specialized Agents
  ↓
Tools / Integrations
  ↓
Database / External Services
```

For sensitive operations:

```text
User
  ↓
AI Agent
  ↓
Sensitive Tool Action
  ↓
Approval Workflow
  ↓
Notification
  ↓
User Approval
  ↓
Tool Execution
  ↓
Audit Log
```

---

# 24. Final Deployment Status

The Vetri AI Multi-Agent application has been deployed and the major application functionality has been tested.

The deployed system includes:

* React frontend
* Django backend
* JWT authentication
* Multi-agent AI architecture
* Role and permission management
* RAG/knowledge functionality
* Approval workflow
* Notifications
* Audit logging
* Google Calendar integration
* Automation reminders
* Intelligent alerts
* Business operation tools

Deployment documentation should be updated whenever the production infrastructure, environment configuration, deployment commands, or external integrations change.
