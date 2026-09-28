from .operations_agent import OperationsAgent
from .qa_agent import QAAgent
from .developer_agent import DeveloperAgent
from .marketing_agent import MarketingAgent
from .finance_agent import FinanceAgent
from .github_agent import GitHubAgent
from .hr_agent import HRAgent
from .sales_agent import SalesAgent
from .project_agent import ProjectAgent
from .reporting_agent import ReportingAgent
from .calendar_agent import CalendarAgent
from .customer_support_agent import CustomerSupportAgent
from .crm_agent import CRMAgent
from .cloud_storage_agent import CloudStorageAgent


class AgentRegistry:
    """
    Registry containing all available AI agents.
    """

    def __init__(self):

        self.agents = [
            CalendarAgent(),
            HRAgent(),
            SalesAgent(),
            CRMAgent(),
            ProjectAgent(),
            FinanceAgent(),
            MarketingAgent(),
            DeveloperAgent(),
            CustomerSupportAgent(),
            QAAgent(),
            OperationsAgent(),
            ReportingAgent(),
            GitHubAgent(),
            CloudStorageAgent(),
        ]

    # =========================================================
    # Get All Agents
    # =========================================================

    def get_agents(self):
        return self.agents

    # =========================================================
    # Find Single Best Agent
    # =========================================================

    def find_agent(self, request):
        """
        Return the best matching single agent.

        Specific domain priorities are checked before
        normal agent routing to avoid keyword conflicts.
        """

        print("USER REQUEST:", request)

        request_lower = request.lower().strip()

        # -----------------------------------------------------
        # HR
        # -----------------------------------------------------

        hr_keywords = [
            "reporting manager",
            "who is the reporting manager",
            "planned leave",
            "emergency leave",
            "work from home",
            "wfh",
            "hr policy",
            "leave policy",
            "employee policy",
            "hr",
            "employee",
            "employees",
            "leave",
        ]

        if any(keyword in request_lower for keyword in hr_keywords):

            for agent in self.agents:
                if agent.name == "HR Agent":
                    print("SELECTED AGENT:", agent.name)
                    return agent

        # -----------------------------------------------------
        # Finance
        # -----------------------------------------------------

        finance_keywords = [
            "finance",
            "financial",
            "expense",
            "expenses",
            "profit",
            "financial summary",
            "revenue",
        ]

        sales_context_keywords = [
            "sales",
            "sale",
            "lead",
            "leads",
            "order",
            "orders",
        ]

        has_finance_keyword = any(
            keyword in request_lower for keyword in finance_keywords
        )

        has_sales_context = any(
            keyword in request_lower for keyword in sales_context_keywords
        )

        revenue_only_finance = "revenue" in request_lower and not has_sales_context

        if has_finance_keyword or revenue_only_finance:

            for agent in self.agents:
                if agent.name == "Finance Agent":
                    print("SELECTED AGENT:", agent.name)
                    return agent

        # -----------------------------------------------------
        # Reporting
        # -----------------------------------------------------

        reporting_keywords = [
            "report",
            "reports",
            "reporting",
            "business report",
            "business reports",
            "business reporting",
            "business summary",
            "business performance",
            "overall business",
            "overall business performance",
            "overall business report",
            "bo report",
            "daily report",
            "generate report",
            "generate a report",
            "show report",
            "show me the report",
            "report summary",
            "reporting summary",
        ]

        if any(keyword in request_lower for keyword in reporting_keywords):

            for agent in self.agents:
                if agent.name == "Reporting Agent":
                    print("SELECTED AGENT:", agent.name)
                    return agent

        # -----------------------------------------------------
        # GitHub
        #
        # IMPORTANT:
        # Generic "issue" alone is NOT enough for GitHub.
        # GitHub issue questions should contain GitHub/Git/
        # repository/PR context.
        # -----------------------------------------------------

        github_context_keywords = [
            "github",
            "git",
            "repository",
            "repositories",
            "repo",
            "repos",
            "pull request",
            "pull requests",
            "pr",
            "git status",
            "repository status",
        ]

        has_github_context = any(
            keyword in request_lower for keyword in github_context_keywords
        )

        github_issue_request = (
            "issue" in request_lower or "issues" in request_lower
        ) and has_github_context

        if has_github_context or github_issue_request:

            for agent in self.agents:
                if agent.name == "GitHub Agent":
                    print("SELECTED AGENT:", agent.name)
                    return agent

        # -----------------------------------------------------
        # Customer Support
        #
        # Support issue phrases are intentionally checked before
        # entity/context routing.
        # -----------------------------------------------------

        customer_support_keywords = [
            "customer support",
            "customer service",
            "support",
            "customer issue",
            "customer issues",
            "open issue",
            "open issues",
            "resolved issue",
            "resolved issues",
            "pending issue",
            "pending issues",
            "pending request",
            "pending requests",
            "complaint",
            "complaints",
            "ticket",
            "tickets",
            "support request",
            "support requests",
            "customer problem",
            "customer problems",
            "customer complaint",
        ]

        if any(keyword in request_lower for keyword in customer_support_keywords):

            for agent in self.agents:
                if agent.name == "Customer Support Agent":
                    print("SELECTED AGENT:", agent.name)
                    return agent

        # -----------------------------------------------------
        # Cloud Storage
        # -----------------------------------------------------

        cloud_storage_keywords = [
            "cloud storage",
            "storage summary",
            "storage usage",
            "cloud files",
            "cloud documents",
            "recent files",
        ]

        if any(keyword in request_lower for keyword in cloud_storage_keywords):

            for agent in self.agents:
                if agent.name == "Cloud Storage Agent":
                    print("SELECTED AGENT:", agent.name)
                    return agent

        # -----------------------------------------------------
        # CRM
        # -----------------------------------------------------

        crm_keywords = [
            "crm",
            "crm status",
            "crm summary",
            "crm overview",
            "customer relationship",
            "customer relationships",
            "customer management",
            "customer records",
            "customer database",
        ]

        if any(keyword in request_lower for keyword in crm_keywords):

            for agent in self.agents:
                if agent.name == "CRM Agent":
                    print("SELECTED AGENT:", agent.name)
                    return agent

        # -----------------------------------------------------
        # Developer
        #
        # Explicit deployment routing is required because
        # "deployment" is otherwise not present in the old
        # DeveloperAgent.can_handle().
        # -----------------------------------------------------

        developer_keywords = [
            "developer",
            "developers",
            "development",
            "deployment",
            "deployments",
            "deploy",
            "deployed",
            "code",
            "coding",
            "programming",
            "python",
            "django",
            "react",
            "javascript",
            "bug",
            "bugs",
            "debug",
            "debugging",
            "technical",
            "software development",
            "software developer",
        ]

        if any(keyword in request_lower for keyword in developer_keywords):

            for agent in self.agents:
                if agent.name == "Developer Agent":
                    print("SELECTED AGENT:", agent.name)
                    return agent

        # -----------------------------------------------------
        # QA
        # -----------------------------------------------------

        qa_keywords = [
            "qa",
            "quality assurance",
            "testing",
            "test result",
            "test results",
            "test case",
            "test cases",
            "test execution",
            "test coverage",
            "coverage",
            "regression testing",
            "regression",
            "passed tests",
            "failed tests",
            "defect",
            "defects",
        ]

        if any(keyword in request_lower for keyword in qa_keywords):

            for agent in self.agents:
                if agent.name == "QA Agent":
                    print("SELECTED AGENT:", agent.name)
                    return agent

        # -----------------------------------------------------
        # Operations
        # -----------------------------------------------------

        operations_keywords = [
            "operations",
            "operation",
            "operational",
            "workflow",
            "workflows",
            "process",
            "processes",
            "operational performance",
            "operations summary",
            "productivity",
            "efficiency",
        ]

        if any(keyword in request_lower for keyword in operations_keywords):

            for agent in self.agents:
                if agent.name == "Operations Agent":
                    print("SELECTED AGENT:", agent.name)
                    return agent

        # -----------------------------------------------------
        # Normal Agent Routing
        # -----------------------------------------------------

        for agent in self.agents:

            print("CHECKING AGENT:", agent.name)

            if agent.can_handle(request):

                print("SELECTED AGENT:", agent.name)

                return agent

        print("NO AGENT FOUND")

        return None

    # =========================================================
    # Find All Agents
    # =========================================================

    def find_agents(self, request):
        """
        Return all agents that can technically handle
        the request.
        """

        print("USER REQUEST:", request)

        matched_agents = []

        for agent in self.agents:

            print("CHECKING AGENT:", agent.name)

            if agent.can_handle(request):

                print("MATCHED AGENT:", agent.name)

                matched_agents.append(agent)

        if not matched_agents:
            print("NO AGENTS FOUND")

        return matched_agents

    # =========================================================
    # Find Relevant Agents For Multi-Agent Requests
    # =========================================================

    def find_relevant_agents(self, request):
        """
        Identify agents that have meaningful domain-specific
        matches in the user's request.

        Focused domain requests should resolve to the relevant
        business agent instead of creating unnecessary
        multi-agent combinations.
        """

        print("========================================")
        print("FINDING RELEVANT MULTI-AGENTS")
        print("REQUEST:", request)
        print("========================================")

        request_lower = request.lower().strip()

        # =====================================================
        # Strong single-domain overrides
        # =====================================================

        # -----------------------------------------------------
        # Customer Support issue metrics
        # -----------------------------------------------------

        support_issue_terms = [
            "open issue",
            "open issues",
            "resolved issue",
            "resolved issues",
            "pending issue",
            "pending issues",
            "pending request",
            "pending requests",
        ]

        if any(term in request_lower for term in support_issue_terms):
            for agent in self.agents:
                if agent.name == "Customer Support Agent":
                    print(
                        "SUPPORT ISSUE PRIORITY:",
                        agent.name,
                    )
                    return [agent]

        # -----------------------------------------------------
        # Customer Support issue questions
        # -----------------------------------------------------
        support_issue_questions = [
            "how many issues are open",
            "how many issues are resolved",
            "issues are open",
            "issues are resolved",
        ]

        if any(term in request_lower for term in support_issue_questions):
            for agent in self.agents:
                if agent.name == "Customer Support Agent":
                    print(
                        "SUPPORT ISSUE QUESTION PRIORITY:",
                        agent.name,
                    )
                    return [agent]

        # -----------------------------------------------------
        # Explicit GitHub issue request
        # -----------------------------------------------------

        github_context = [
            "github",
            "git",
            "repository",
            "repositories",
            "repo",
            "repos",
            "pull request",
            "pull requests",
            "git status",
            "repository status",
        ]

        has_github_context = any(term in request_lower for term in github_context)

        if has_github_context and (
            "issue" in request_lower or "issues" in request_lower
        ):
            for agent in self.agents:
                if agent.name == "GitHub Agent":
                    print(
                        "GITHUB ISSUE PRIORITY:",
                        agent.name,
                    )
                    return [agent]

        # -----------------------------------------------------
        # Developer deployment request
        # -----------------------------------------------------

        developer_focus_terms = [
            "deployment",
            "deployments",
            "deploy",
            "deployed",
        ]

        if any(term in request_lower for term in developer_focus_terms):
            for agent in self.agents:
                if agent.name == "Developer Agent":
                    print(
                        "DEVELOPER DEPLOYMENT PRIORITY:",
                        agent.name,
                    )
                    return [agent]

        # =====================================================
        # Customer Follow-up Priority
        # =====================================================

        has_customer_reference = (
            "customer" in request_lower or "customers" in request_lower
        )

        has_followup_reference = (
            "follow-up" in request_lower
            or "follow up" in request_lower
            or "followups" in request_lower
        )

        if has_customer_reference and has_followup_reference:
            for agent in self.agents:
                if agent.name == "CRM Agent":
                    print(
                        "CUSTOMER FOLLOW-UP PRIORITY:",
                        agent.name,
                    )
                    return [agent]

        # =====================================================
        # Sales
        # =====================================================

        sales_keywords = [
            "sales",
            "sale",
            "lead",
            "leads",
            "follow-up",
            "follow up",
            "followups",
            "order",
            "orders",
            "sales policy",
            "sales sop",
            "sales process",
        ]

        sales_score = sum(1 for keyword in sales_keywords if keyword in request_lower)

        # =====================================================
        # Finance
        # =====================================================

        finance_keywords = [
            "finance",
            "financial",
            "expense",
            "expenses",
            "profit",
            "financial summary",
        ]

        finance_score = sum(
            1 for keyword in finance_keywords if keyword in request_lower
        )

        if "revenue" in request_lower and sales_score == 0 and finance_score == 0:
            finance_score = 1

        # =====================================================
        # Reporting
        # =====================================================

        reporting_keywords = [
            "report",
            "reports",
            "reporting",
            "business report",
            "business reports",
            "business reporting",
            "business summary",
            "business performance",
            "overall business",
            "overall business performance",
            "overall business report",
            "bo report",
            "daily report",
            "generate report",
            "generate a report",
            "show report",
            "show me the report",
            "report summary",
            "reporting summary",
        ]

        reporting_score = sum(
            1 for keyword in reporting_keywords if keyword in request_lower
        )

        # Reporting is a complete business-level request.
        # Do not add GitHub merely because the report contains
        # GitHub-related wording.
        if reporting_score > 0:
            for agent in self.agents:
                if agent.name == "Reporting Agent":
                    print(
                        "REPORTING PRIORITY:",
                        agent.name,
                    )
                    return [agent]

        # =====================================================
        # Project
        # =====================================================

        project_keywords = [
            "project",
            "projects",
            "delayed",
            "delay",
            "deadline",
            "deadlines",
            "task",
            "tasks",
            "milestone",
            "milestones",
            "project status",
            "project policy",
            "project sop",
            "project process",
        ]

        project_score = sum(
            1 for keyword in project_keywords if keyword in request_lower
        )

        # =====================================================
        # GitHub
        # =====================================================

        github_keywords = [
            "github",
            "git",
            "repository",
            "repositories",
            "repo",
            "repos",
            "pull request",
            "pull requests",
            "git status",
            "repository status",
        ]

        github_score = sum(1 for keyword in github_keywords if keyword in request_lower)

        # =====================================================
        # Marketing
        # =====================================================

        marketing_keywords = [
            "marketing",
            "campaign",
            "campaigns",
            "advertising",
            "advertisement",
            "promotion",
            "promotions",
            "marketing performance",
            "marketing summary",
            "conversion",
            "conversions",
            "clicks",
            "impressions",
        ]

        marketing_score = sum(
            1 for keyword in marketing_keywords if keyword in request_lower
        )

        # =====================================================
        # Customer Support
        # =====================================================

        customer_support_keywords = [
            "customer support",
            "customer service",
            "support",
            "customer issue",
            "customer issues",
            "complaint",
            "complaints",
            "ticket",
            "tickets",
            "support request",
            "support requests",
            "customer problem",
            "customer problems",
            "customer complaint",
        ]

        customer_support_score = sum(
            1 for keyword in customer_support_keywords if keyword in request_lower
        )

        # =====================================================
        # Calendar
        # =====================================================

        calendar_keywords = [
            "calendar",
            "event",
            "events",
            "meeting",
            "meetings",
            "schedule",
            "scheduled",
            "appointment",
            "appointments",
        ]

        calendar_score = sum(
            1 for keyword in calendar_keywords if keyword in request_lower
        )

        # =====================================================
        # CRM
        # =====================================================

        crm_keywords = [
            "crm",
            "crm status",
            "crm summary",
            "crm overview",
            "customer relationship",
            "customer relationships",
            "customer management",
            "customer records",
            "customer database",
            "customer information",
        ]

        crm_score = sum(1 for keyword in crm_keywords if keyword in request_lower)

        # =====================================================
        # Developer
        # =====================================================

        developer_keywords = [
            "developer",
            "developers",
            "development",
            "deployment",
            "deployments",
            "deploy",
            "deployed",
            "bug",
            "bugs",
            "coding",
            "programming",
            "python",
            "django",
            "react",
            "javascript",
            "debug",
            "debugging",
            "technical",
        ]

        developer_score = sum(
            1 for keyword in developer_keywords if keyword in request_lower
        )

        # =====================================================
        # QA
        # =====================================================

        qa_keywords = [
            "qa",
            "quality assurance",
            "testing",
            "test result",
            "test results",
            "test case",
            "test cases",
            "test execution",
            "test coverage",
            "coverage",
            "regression testing",
            "regression",
            "passed tests",
            "failed tests",
            "defect",
            "defects",
        ]

        qa_score = sum(1 for keyword in qa_keywords if keyword in request_lower)

        # =====================================================
        # Operations
        # =====================================================

        # -----------------------------------------------------
        # Operations pending task priority
        # -----------------------------------------------------

        operations_pending_task_questions = [
            "how many tasks are pending",
            "how many pending tasks",
            "tasks are pending",
            "pending tasks",
        ]
        
        if any(term in request_lower for term in operations_pending_task_questions):
            for agent in self.agents:
                if agent.name == "Operations Agent":
                    print(
                        "OPERATIONS PENDING TASK PRIORITY:",
                        agent.name,
                    )
                    return [agent]

        operations_keywords = [
            "operations",
            "operation",
            "operational",
            "workflow",
            "workflows",
            "process",
            "processes",
            "operational performance",
            "operations summary",
            "productivity",
            "efficiency",
            "pending task",
            "pending tasks",
        ]

        operations_score = sum(
            1 for keyword in operations_keywords if keyword in request_lower
        )

        # =====================================================
        # Score Map
        # =====================================================

        scores = {
            "Sales Agent": sales_score,
            "CRM Agent": crm_score,
            "Finance Agent": finance_score,
            "Reporting Agent": reporting_score,
            "Project Agent": project_score,
            "GitHub Agent": github_score,
            "Marketing Agent": marketing_score,
            "Customer Support Agent": customer_support_score,
            "Calendar Agent": calendar_score,
            "Developer Agent": developer_score,
            "QA Agent": qa_score,
            "Operations Agent": operations_score,
        }

        # =====================================================
        # Strong Matches
        # =====================================================

        matches = []

        for agent in self.agents:

            score = scores.get(agent.name, 0)

            if score > 0:

                print(
                    "RELEVANT AGENT:",
                    agent.name,
                    "SCORE:",
                    score,
                )

                matches.append((agent, score))

        # =====================================================
        # Remaining Agents
        # =====================================================

        explicitly_scored = set(scores.keys())

        for agent in self.agents:

            if agent.name in explicitly_scored:
                continue

            if agent.can_handle(request):

                print(
                    "RELEVANT AGENT:",
                    agent.name,
                    "SCORE:",
                    1,
                )

                matches.append((agent, 1))

        # =====================================================
        # Sort
        # =====================================================

        matches.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        selected_agents = [agent for agent, score in matches]

        print(
            "FINAL RELEVANT AGENTS:",
            [agent.name for agent in selected_agents],
        )

        return selected_agents
