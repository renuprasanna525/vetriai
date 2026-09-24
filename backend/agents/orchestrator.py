from .registry import AgentRegistry
from permissions.permission_engine import PermissionEngine
from audit_logs.utils import create_audit_log
from knowledge_base.llm_service import LLMService


class AIOrchestrator:
    """
    Central coordinator for the Vetri AI Multi-Agent system.

    Responsibilities:
    - Understand user requests
    - Select one or multiple agents
    - Check permissions
    - Execute authorized agents
    - Combine results from multiple agents
    - Generate natural conversational responses
    - Maintain conversation context
    - Maintain entity/item-level context
    - Support management/business overview queries
    - Support contextual follow-up questions
    - Record audit logs
    """

    def __init__(self):
        self.registry = AgentRegistry()
        self.permission_engine = PermissionEngine()
        self.llm_service = LLMService()

    # =========================================================
    # AGENT INFORMATION
    # =========================================================

    def get_available_agents(self):
        return [
            {
                "name": agent.name,
                "description": agent.description,
            }
            for agent in self.registry.get_agents()
        ]

    def understand_intent(self, request):
        agent = self.registry.find_agent(request)

        if agent:
            return {
                "intent": agent.name,
                "agent": agent,
            }

        return {
            "intent": "unknown",
            "agent": None,
        }

    # =========================================================
    # QUERY DETECTION
    # =========================================================

    def is_management_query(self, request):
        management_keywords = [
            "business priorities",
            "business priority",
            "important business",
            "important priorities",
            "important priority",
            "management priorities",
            "management priority",
            "business overview",
            "management overview",
            "business summary",
            "management summary",
            "complete business",
            "complete business update",
            "overall business",
            "overall business status",
            "overall company",
            "company overview",
            "company summary",
            "operational overview",
            "operational summary",
            "what is important",
            "what's important",
            "what needs attention",
            "what should i focus on",
            "what should we focus on",
            "priorities for tomorrow",
            "important for tomorrow",
            "complete operational",
            "entire operation",
            "entire operations",
            "all operations",
        ]

        request_lower = request.lower()

        return any(keyword in request_lower for keyword in management_keywords)

    def is_knowledge_question(self, request):
        knowledge_keywords = [
            "policy",
            "how can",
            "how do",
            "how many days",
            "who approves",
            "work from home",
            "wfh",
            "planned leave",
            "emergency leave",
            "reporting manager",
        ]

        request_lower = request.lower()

        return any(keyword in request_lower for keyword in knowledge_keywords)

    def is_follow_up_question(
        self,
        request,
        conversation_history=None,
    ):
        """
        Detect questions that depend on previous conversation context.

        In addition to normal follow-up phrases, this method
        recognizes entity-reference phrases such as:

         - it
         - its
         - their
         - that
         - this
         - that project
         - this project
         - that one
         - this one
         - for it
         - for that
         - for this
         - about it
         - about that
         - about this

        These are treated as follow-ups only when an entity
        exists in the previous conversation.
        """

        follow_up_keywords = [
            "which area",
            "which one",
            "which department",
            "which project",
            "which part",
            "what about",
            "tell me more",
            "tell me more about",
            "more details",
            "more detail",
            "more about",
            "why is that",
            "why is this",
            "why",
            "what should i focus",
            "what should we focus",
            "what should i do",
            "what should we do",
            "what next",
            "what should happen next",
            "what needs attention",
            "anything else",
            "is there anything",
            "how does that affect",
            "how is that",
            "explain that",
            "explain this",
            "show more",
            "give more details",
            "give me more",
            "for it",
            "for that",
            "for this",
            "about it",
            "about that",
            "about this",
            "its",
            "their",
            "the same",
            "same project",
            "same task",
        ]

        request_lower = request.lower().strip()

        # -----------------------------------------------------
        # No conversation means there cannot be a follow-up
        # -----------------------------------------------------

        if not conversation_history:
            return False

        # -----------------------------------------------------
        # Direct follow-up phrase detection
        # -----------------------------------------------------

        if any(keyword in request_lower for keyword in follow_up_keywords):
            return True

        # -----------------------------------------------------
        # Entity-reference follow-up detection
        # -----------------------------------------------------

        entity_context = self.get_entity_context_from_conversation(
            request=request,
            conversation_history=conversation_history,
        )

        if entity_context:

            reference_phrases = [
                "it",
                "its",
                "their",
                "that",
                "this",
                "that one",
                "this one",
                "that project",
                "this project",
                "that customer",
                "this customer",
                "that employee",
                "this employee",
                "that task",
                "this task",
            ]

        # Exact short reference questions
        if request_lower in reference_phrases:
            return True

        words = request_lower.split()

        # -------------------------------------------------
        # Pronoun-based references
        # -------------------------------------------------

        if "it" in words:
            return True

        if "its" in words:
            return True

        if "their" in words:
            return True

        # -------------------------------------------------
        # That / this references
        # -------------------------------------------------

        if "that" in words or "this" in words:

            reference_patterns = [
                "that project",
                "this project",
                "that one",
                "this one",
                "that customer",
                "this customer",
                "that employee",
                "this employee",
                "that task",
                "this task",
            ]

            if any(phrase in request_lower for phrase in reference_patterns):
                return True

            return False

    # =========================================================
    # CONVERSATION CONTEXT
    # =========================================================

    def get_recent_conversation_context(
        self,
        conversation_history,
        limit=8,
    ):
        if not conversation_history:
            return []

        return conversation_history[-limit:]

    def format_conversation_context(
        self,
        conversation_history,
    ):
        recent_messages = self.get_recent_conversation_context(conversation_history)

        if not recent_messages:
            return ""

        context_lines = []

        for message in recent_messages:
            sender = message.get(
                "sender",
                "user",
            )

            content = message.get(
                "content",
                "",
            )

            if not content:
                continue

            label = "Assistant" if sender == "assistant" else "User"

            context_lines.append(f"{label}: {content}")

        return "\n".join(context_lines)

    def get_last_assistant_message(
        self,
        conversation_history,
    ):
        if not conversation_history:
            return ""

        for message in reversed(conversation_history):
            if message.get("sender") == "assistant":
                return message.get(
                    "content",
                    "",
                )

        return ""

    def get_previous_user_message(
        self,
        conversation_history,
    ):
        if not conversation_history:
            return ""

        found_current_user = False

        for message in reversed(conversation_history):
            if message.get("sender") == "user":

                if not found_current_user:
                    found_current_user = True
                    continue

                return message.get(
                    "content",
                    "",
                )

        return ""

    # =========================================================
    # NATURAL RESPONSE GENERATION
    # =========================================================

    def generate_natural_response(
        self,
        request,
        results,
        conversation_history=None,
        fallback_response="",
    ):
        """
        Convert verified agent results into a natural,
        conversational AI response.
        """

        conversation_history = conversation_history or []

        successful_results = [
            result for result in results if result.get("status") == "success"
        ]

        denied_results = [
            result for result in results if result.get("status") == "denied"
        ]

        error_results = [
            result for result in results if result.get("status") == "error"
        ]

        if not successful_results:

            if fallback_response:
                return fallback_response

            if denied_results:
                return (
                    "I found the relevant business information, "
                    "but your current role does not have "
                    "permission to access the requested area."
                )

            if error_results:
                return (
                    "I could not retrieve the relevant business "
                    "information at the moment."
                )

            return "I could not find enough information to answer " "your question."

        conversation_context = self.format_conversation_context(conversation_history)

        natural_results = []

        for result in results:
            natural_results.append(
                {
                    "agent": result.get(
                        "agent",
                        "Business Agent",
                    ),
                    "status": result.get(
                        "status",
                        "success",
                    ),
                    "message": result.get(
                        "message",
                        "",
                    ),
                    "data": result.get(
                        "data",
                        {},
                    ),
                }
            )

        try:
            response = self.llm_service.generate_chat_response(
                question=request,
                agent_results=natural_results,
                conversation_context=conversation_context,
            )

            if response and response.strip():
                return response.strip()

        except Exception as error:
            print(
                "NATURAL RESPONSE LLM ERROR:",
                str(error),
            )

        return fallback_response

    # =========================================================
    # AGENT CONTEXT DETECTION
    # =========================================================

    def get_agents_from_conversation(
        self,
        conversation_history,
    ):
        """
        Detect the business agents involved in the previous
        conversation.

        Priority:

        1. Previous USER message
        2. No previous assistant fallback for explicit entity
        3. Previous assistant only when necessary

        This prevents generic assistant responses from
        contaminating the next request with unrelated agents.
        """

        if not conversation_history:
            return []

        available_agents = self.registry.get_agents()

        previous_user = self.get_previous_user_message(conversation_history)

        previous_assistant = self.get_last_assistant_message(conversation_history)

        print(
            "CONTEXT PREVIOUS USER:",
            previous_user,
        )

        print(
            "CONTEXT PREVIOUS ASSISTANT:",
            previous_assistant,
        )

        agent_keywords = {
            "Finance Agent": [
                "finance",
                "financial",
                "revenue",
                "expense",
                "expenses",
                "profit",
                "loss",
                "payment",
                "payments",
                "budget",
                "financial status",
            ],
            "Sales Agent": [
                "sales",
                "sale",
                "lead",
                "leads",
                "follow-up",
                "follow up",
                "followups",
                "customer",
                "customers",
                "order",
                "orders",
            ],
            "Project Agent": [
                "project",
                "projects",
                "project status",
                "deadline",
                "deadlines",
                "delayed project",
                "delayed projects",
                "delay",
                "delays",
                "project risk",
                "project risks",
            ],
            "HR Agent": [
                "hr",
                "human resources",
                "employee",
                "employees",
                "leave",
                "leaves",
                "attendance",
                "staff",
            ],
            "Calendar Agent": [
                "calendar",
                "meeting",
                "meetings",
                "event",
                "events",
                "schedule",
                "scheduled",
                "appointment",
            ],
            "Marketing Agent": [
                "marketing",
                "campaign",
                "campaigns",
                "marketing leads",
            ],
            "Developer Agent": [
                "developer",
                "development",
                "bug",
                "bugs",
                "deployment",
                "deployments",
                "technical",
                "code",
                "coding",
            ],
            "Customer Support Agent": [
                "support",
                "customer support",
                "support issue",
                "support issues",
                "open issue",
                "open issues",
                "resolved issue",
                "resolved issues",
            ],
            "Operations Agent": [
                "operations",
                "operation",
                "workflow",
                "workflows",
                "process",
                "processes",
                "efficiency",
                "operational",
            ],
            "QA Agent": [
                "qa",
                "quality assurance",
                "test case",
                "test cases",
                "testing",
                "passed",
                "failed",
                "coverage",
            ],
            "CRM Agent": [
                "crm",
                "customer relationship",
                "customer relationships",
            ],
            "Project Management Agent": [
                "project management",
                "task",
                "tasks",
                "milestone",
                "milestones",
                "schedule",
                "schedules",
            ],
            "Cloud Storage Agent": [
                "cloud storage",
                "storage",
                "files",
                "documents",
                "cloud files",
            ],
            "GitHub Agent": [
                "github",
                "repository",
                "repositories",
                "repo",
                "repos",
                "pull request",
                "pull requests",
            ],
        }

        def detect_agents_from_text(text):
            if not text:
                return []

            text_lower = text.lower()

            detected_agents = []

            for agent in available_agents:

                agent_name = agent.name

                if agent_name.lower() in text_lower:
                    detected_agents.append(agent)
                    continue

                keywords = agent_keywords.get(
                    agent_name,
                    [],
                )

                if any(keyword.lower() in text_lower for keyword in keywords):
                    detected_agents.append(agent)

            unique_agents = []
            seen_names = set()

            for agent in detected_agents:
                if agent.name not in seen_names:
                    unique_agents.append(agent)
                    seen_names.add(agent.name)

            return unique_agents

        # -----------------------------------------------------
        # Previous USER is authoritative
        # -----------------------------------------------------

        user_agents = detect_agents_from_text(previous_user)

        if user_agents:
            print("CONTEXT SOURCE: PREVIOUS USER MESSAGE")

            print(
                "PREVIOUS USER CONTEXT AGENTS:",
                [agent.name for agent in user_agents],
            )

            return user_agents

        # -----------------------------------------------------
        # Previous assistant is only a limited fallback.
        #
        # IMPORTANT:
        # We do NOT use assistant context when the previous
        # user message is simply an entity-reference question.
        # Entity routing is handled separately.
        # -----------------------------------------------------

        if previous_assistant:
            assistant_agents = detect_agents_from_text(previous_assistant)

            if assistant_agents:
                print("CONTEXT SOURCE: PREVIOUS ASSISTANT MESSAGE")

                print(
                    "PREVIOUS ASSISTANT CONTEXT AGENTS:",
                    [agent.name for agent in assistant_agents],
                )

                return assistant_agents

        print("CONTEXT SOURCE: NONE")
        print("CONTEXT AGENTS DETECTED: []")

        return []

    # =========================================================
    # ENTITY / ITEM CONTEXT
    # =========================================================

    def get_entity_context_from_conversation(
        self,
        request,
        conversation_history,
    ):
        """
        Detect specific business entities/items.

        Priority:

        1. Current user request
        2. Previous user message
        3. Previous assistant response

        Examples:

        Tell me more about Vetri E-Commerce
            -> Vetri E-Commerce

        Why is that project delayed?
            -> Vetri E-Commerce

        What tasks are pending for it?
            -> Vetri E-Commerce

        What about AI Dashboard?
            -> AI Dashboard
        """

        known_entities = [
            "Vetri E-Commerce",
            "AI Dashboard",
            "CRM System",
            "HR Management System",
            "ABC Technologies",
            "XYZ Solutions",
            "Global Systems",
            "Payment Integration",
            "Dashboard UI",
            "Customer Module",
            "Priya",
            "Divya",
        ]

        def detect_entities_from_text(text):
            if not text:
                return []

            text_lower = text.lower()

            detected_entities = []

            for entity in known_entities:
                if entity.lower() in text_lower:
                    detected_entities.append(entity)

            return detected_entities

        # -----------------------------------------------------
        # 1. Current user request
        # -----------------------------------------------------

        current_entities = detect_entities_from_text(request)

        if current_entities:
            print("ENTITY CONTEXT SOURCE: CURRENT USER REQUEST")

            print(
                "CURRENT USER ENTITIES:",
                current_entities,
            )

            return current_entities

        # -----------------------------------------------------
        # 2. Previous user message
        # -----------------------------------------------------

        previous_user = self.get_previous_user_message(conversation_history)

        previous_user_entities = detect_entities_from_text(previous_user)

        if previous_user_entities:
            print("ENTITY CONTEXT SOURCE: PREVIOUS USER MESSAGE")

            print(
                "PREVIOUS USER ENTITIES:",
                previous_user_entities,
            )

            return previous_user_entities

        # -----------------------------------------------------
        # 3. Previous assistant message
        #
        # Only used if the user did not identify an entity.
        # -----------------------------------------------------

        previous_assistant = self.get_last_assistant_message(conversation_history)

        previous_assistant_entities = detect_entities_from_text(previous_assistant)

        if previous_assistant_entities:
            print("ENTITY CONTEXT SOURCE: PREVIOUS ASSISTANT MESSAGE")

            print(
                "PREVIOUS ASSISTANT ENTITIES:",
                previous_assistant_entities,
            )

            return previous_assistant_entities

        print("ENTITY CONTEXT SOURCE: NONE")
        print("ENTITY CONTEXT ENTITIES: []")

        return []

    # =========================================================
    # ENTITY -> AGENT MAPPING
    # =========================================================

    def get_agents_from_entities(
        self,
        entity_context,
    ):
        """
        Determine the correct business agent from a known entity.

        This is important when the current request contains
        an entity but does not contain an agent keyword.

        Example:

            "What about AI Dashboard?"

        The word "project" may not appear, but AI Dashboard
        clearly belongs to Project Agent.
        """

        if not entity_context:
            return []

        entity_agent_mapping = {
            "Vetri E-Commerce": "Project Agent",
            "AI Dashboard": "Project Agent",
            "CRM System": "Project Agent",
            "HR Management System": "Project Agent",
            "Payment Integration": "Project Agent",
            "Dashboard UI": "Project Agent",
            "Customer Module": "Project Agent",
            "ABC Technologies": "Sales Agent",
            "XYZ Solutions": "Sales Agent",
            "Global Systems": "Sales Agent",
            "Priya": "HR Agent",
            "Divya": "HR Agent",
        }

        agent_names = []

        for entity in entity_context:
            agent_name = entity_agent_mapping.get(entity)

            if agent_name and agent_name not in agent_names:
                agent_names.append(agent_name)

        selected_agents = []

        for agent in self.registry.get_agents():
            if agent.name in agent_names:
                selected_agents.append(agent)

        if selected_agents:
            print(
                "ENTITY-BASED AGENTS:",
                [agent.name for agent in selected_agents],
            )

        return selected_agents

    # =========================================================
    # DIRECT REQUEST AGENT DETECTION
    # =========================================================

    def get_agents_from_request(
        self,
        request,
    ):
        """
        Detect agents directly mentioned in the current question.
        """

        return self.registry.find_relevant_agents(request)

    # =========================================================
    # PERMISSION HELPER
    # =========================================================

    def check_agent_permission(
        self,
        user,
        agent_name,
    ):
        try:
            return self.permission_engine.can_access(
                user,
                agent_name,
            )

        except TypeError:

            try:
                return self.permission_engine.can_access(
                    user=user,
                    agent=agent_name,
                )

            except Exception:
                return True

        except Exception:
            return True

    # =========================================================
    # AGENT EXECUTION HELPER
    # =========================================================

    def execute_agent(
        self,
        agent,
        agent_request,
        user,
        credentials=None,
    ):
        agent_name = agent.name

        allowed = self.check_agent_permission(
            user=user,
            agent_name=agent_name,
        )

        if not allowed:
            return {
                "agent": agent_name,
                "status": "denied",
                "message": (
                    f"You do not have permission to access "
                    f"{agent_name} information."
                ),
            }

        try:

            if agent_name == "Calendar Agent":

                agent_result = agent.process(
                    agent_request,
                    user=user,
                    credentials=credentials,
                )

            else:

                agent_result = agent.process(
                    agent_request,
                    user=user,
                )

            if isinstance(agent_result, dict):
                result = agent_result.copy()

            else:
                result = {
                    "status": "success",
                    "message": str(agent_result),
                }

            result["agent"] = agent_name

            return result

        except Exception as error:

            print(
                f"{agent_name} ERROR:",
                str(error),
            )

            return {
                "agent": agent_name,
                "status": "error",
                "message": (f"{agent_name} could not process " f"the request."),
                "error": str(error),
            }

    # =========================================================
    # CONTEXTUAL AGENT REQUEST
    # =========================================================

    def get_contextual_agent_request(
        self,
        request,
        agent_name,
        previous_assistant="",
        previous_user="",
        entity_context=None,
        attention_question=False,
    ):
        """
        Convert vague follow-ups into meaningful requests.

        Entity context is included when a specific business
        item/project/customer/employee is known.
        """

        entity_context = entity_context or []

        # -----------------------------------------------------
        # Attention questions
        # -----------------------------------------------------

        if attention_question:

            attention_requests = {
                "HR Agent": (
                    "Give current HR status and identify "
                    "important employee or leave items "
                    "that may need attention."
                ),
                "Project Agent": (
                    "Give current project status and identify "
                    "delayed projects, upcoming deadlines, "
                    "and project risks that may need attention."
                ),
                "Sales Agent": (
                    "Give current sales status and identify "
                    "pending follow-ups, important leads, "
                    "and sales items requiring attention."
                ),
                "Finance Agent": (
                    "Give current finance status and identify "
                    "important financial items requiring review."
                ),
                "Calendar Agent": (
                    "Give upcoming important meetings and "
                    "calendar items that may require attention."
                ),
            }

            base_request = attention_requests.get(
                agent_name,
                request,
            )

        else:

            detail_requests = {
                "HR Agent": (
                    "Give more detailed information about the "
                    "current HR and employee status discussed "
                    "in the previous conversation. Include "
                    "important leave information and relevant "
                    "employee items."
                ),
                "Project Agent": (
                    "Give more detailed information about the "
                    "current project status discussed in the "
                    "previous conversation. Include project "
                    "names, statuses, delayed projects, delay "
                    "duration, deadlines, risks, pending tasks, "
                    "and completed tasks when available."
                ),
                "Sales Agent": (
                    "Give more detailed information about the "
                    "current sales status discussed in the "
                    "previous conversation. Include total "
                    "leads, new leads, pending follow-ups, "
                    "orders, and other available sales details."
                ),
                "Finance Agent": (
                    "Give more detailed information about the "
                    "current finance status discussed in the "
                    "previous conversation. Include revenue, "
                    "expenses, net profit, and other available "
                    "financial details."
                ),
                "Calendar Agent": (
                    "Give more detailed information about the "
                    "important calendar events and meetings "
                    "related to the previous conversation."
                ),
                "Marketing Agent": (
                    "Give more detailed information about the "
                    "current marketing status discussed in the "
                    "previous conversation. Include campaigns, "
                    "active campaigns, leads, conversions, and "
                    "other available marketing details."
                ),
                "Developer Agent": (
                    "Give more detailed information about the "
                    "current developer and technical work status. "
                    "Include projects, bugs, tasks, deployments, "
                    "and other available details."
                ),
                "Customer Support Agent": (
                    "Give more detailed information about the "
                    "current customer support status. Include "
                    "customers, open issues, pending issues, "
                    "resolved issues, and other available details."
                ),
                "Operations Agent": (
                    "Give more detailed information about the "
                    "current operations status. Include workflows, "
                    "processes, pending tasks, efficiency, and "
                    "other available operational details."
                ),
                "QA Agent": (
                    "Give more detailed information about the "
                    "current QA status. Include test cases, "
                    "passed and failed cases, coverage, and "
                    "other available quality information."
                ),
                "CRM Agent": (
                    "Give more detailed information about the "
                    "current CRM status and available customer "
                    "relationship information."
                ),
                "Project Management Agent": (
                    "Give more detailed information about the "
                    "current project management status, including "
                    "tasks, schedules, risks, and project progress."
                ),
                "Cloud Storage Agent": (
                    "Give more detailed information about the "
                    "current cloud storage status and available "
                    "storage-related information."
                ),
                "GitHub Agent": (
                    "Give more detailed information about the "
                    "current GitHub status, including repositories, "
                    "issues, pull requests, and other available "
                    "development information."
                ),
            }

            base_request = detail_requests.get(
                agent_name,
                (
                    "Provide more detailed information about "
                    "the business area discussed in the previous "
                    "conversation."
                ),
            )

        # -----------------------------------------------------
        # Project task / item-specific requests
        # -----------------------------------------------------

        request_lower = request.lower()

        if agent_name == "Project Agent":
            if any(
                keyword in request_lower
                for keyword in [
                    "pending task",
                    "pending tasks",
                    "what tasks",
                    "which tasks",
                    "task status",
                    "status of",
                    "payment integration",
                    "dashboard ui",
                    "customer module",
                ]
            ):
                base_request = (
                    "Retrieve the project-level and task-level information "
                    "needed to answer the current question. Include the "
                    "specific project or task requested, its current status, "
                    "progress, pending/in-progress/completed state, delay "
                    "information, and related project details when available. "
                    "For task questions, return the actual task names and "
                    "their statuses from the available project records. "
                    "Do not replace task-level information with only a "
                    "high-level project summary. Do not invent information."
                )

        # -----------------------------------------------------
        # Entity-specific context
        # -----------------------------------------------------

        if entity_context:

            entity_names = ", ".join(entity_context)

            if len(entity_context) == 1:

                entity_name = entity_context[0]

                if agent_name == "Project Agent":

                    base_request += (
                        "\n\nSPECIFIC PROJECT CONTEXT:\n"
                        f"The user is specifically asking about "
                        f"the project '{entity_name}'.\n\n"
                        f"Focus only on '{entity_name}' unless "
                        "the user explicitly asks about another "
                        "project.\n"
                        "Include its current status, progress, "
                        "delay information, related tasks, risks, "
                        "and other available project details.\n"
                        "If the reason for a delay is not available "
                        "in the data, clearly state that the reason "
                        "is not available.\n"
                        "Do not invent project information."
                    )

                elif agent_name == "Sales Agent":

                    base_request += (
                        "\n\nSPECIFIC SALES ENTITY CONTEXT:\n"
                        f"The user is specifically asking about "
                        f"'{entity_name}'.\n\n"
                        f"Focus on '{entity_name}' and provide "
                        "available lead, follow-up, order, or "
                        "customer information.\n"
                        "Do not invent information."
                    )

                elif agent_name == "HR Agent":

                    base_request += (
                        "\n\nSPECIFIC EMPLOYEE CONTEXT:\n"
                        f"The user is specifically asking about "
                        f"'{entity_name}'.\n\n"
                        "Provide available employee or leave "
                        "information for this person.\n"
                        "Do not invent information."
                    )

                else:

                    base_request += (
                        "\n\nSPECIFIC ENTITY CONTEXT:\n"
                        f"The user is specifically asking about "
                        f"'{entity_name}'.\n\n"
                        "Focus on this entity when the available "
                        "agent data supports it.\n"
                        "Do not switch to unrelated entities.\n"
                        "Do not invent information."
                    )

            else:

                base_request += (
                    "\n\nSPECIFIC ENTITY CONTEXT:\n"
                    f"The user is discussing: {entity_names}.\n\n"
                    "Focus on these entities when the available "
                    "data supports them.\n"
                    "Do not switch to unrelated entities.\n"
                    "Do not invent information."
                )

            base_request += (
                "\n\nENTITY REFERENCE RULE:\n"
                "If the current question contains phrases such "
                "as 'it', 'that', 'this', 'that project', "
                "'this project', 'that one', 'this one', "
                "'for it', 'for that', or 'for this', resolve "
                "the reference using the identified entity "
                "from the conversation."
            )

        # -----------------------------------------------------
        # Previous conversation
        # -----------------------------------------------------

        if previous_user or previous_assistant:

            base_request += (
                "\n\nPREVIOUS CONVERSATION CONTEXT:\n"
                f"Previous user message: {previous_user}\n"
                f"Previous assistant message: "
                f"{previous_assistant}\n"
            )

        # -----------------------------------------------------
        # Current question
        # -----------------------------------------------------

        base_request += "\n\nCURRENT USER QUESTION:\n" f"{request}\n"

        return base_request

    # =========================================================
    # MANAGEMENT AGENT SELECTION
    # =========================================================

    def get_management_agents(
        self,
        request,
    ):
        requested_agents = self.registry.find_relevant_agents(request)

        if requested_agents:

            print(
                "TARGETED MANAGEMENT AGENTS:",
                [agent.name for agent in requested_agents],
            )

            return requested_agents

        broad_management_names = [
            "HR Agent",
            "Project Agent",
            "Sales Agent",
            "Finance Agent",
            "Calendar Agent",
        ]

        management_agents = [
            agent
            for agent in self.registry.get_agents()
            if agent.name in broad_management_names
        ]

        print(
            "BROAD MANAGEMENT AGENTS:",
            [agent.name for agent in management_agents],
        )

        return management_agents

    # =========================================================
    # MANAGEMENT QUERY
    # =========================================================

    def process_management_query(
        self,
        request,
        user,
        role,
        credentials=None,
        conversation_history=None,
    ):
        conversation_history = conversation_history or []

        selected_agents = self.get_management_agents(request)

        agent_requests = {
            "HR Agent": (
                "Give the current HR and employee status, "
                "including important leave information."
            ),
            "Project Agent": (
                "Give the current project status, upcoming "
                "deadlines, and delayed projects."
            ),
            "Sales Agent": (
                "Give the current sales summary, including "
                "total leads, new leads, follow-ups, and orders."
            ),
            "Finance Agent": (
                "Give the current finance summary, including "
                "revenue, expenses, and net profit."
            ),
            "Calendar Agent": (
                "Give the important meetings and events " "scheduled for tomorrow."
            ),
        }

        results = []

        for agent in selected_agents:

            agent_name = agent.name

            agent_request = agent_requests.get(
                agent_name,
                request,
            )

            print(
                f"{agent_name} REQUEST:",
                agent_request,
            )

            result = self.execute_agent(
                agent=agent,
                agent_request=agent_request,
                user=user,
                credentials=credentials,
            )

            results.append(result)

        fallback_response = self.build_combined_response(
            request=request,
            results=results,
            conversation_history=conversation_history,
            management=True,
        )

        response_message = self.generate_natural_response(
            request=request,
            results=results,
            conversation_history=conversation_history,
            fallback_response=fallback_response,
        )

        try:
            create_audit_log(
                user=user,
                action="multi_agent_management_query",
                details={
                    "request": request,
                    "agents": [agent.name for agent in selected_agents],
                },
            )
        except Exception:
            pass

        return {
            "status": "success",
            "intent": "multi_agent_management",
            "agent": "Multi-Agent Orchestrator",
            "response": response_message,
            "data": {
                "agent_results": results,
                "conversation_context_used": bool(conversation_history),
            },
        }

    # =========================================================
    # MULTI-AGENT QUERY
    # =========================================================

    def process_multi_agent_query(
        self,
        request,
        user,
        role,
        credentials=None,
        conversation_history=None,
    ):
        conversation_history = conversation_history or []

        selected_agents = self.registry.find_relevant_agents(request)

        results = []

        for agent in selected_agents:

            result = self.execute_agent(
                agent=agent,
                agent_request=request,
                user=user,
                credentials=credentials,
            )

            results.append(result)

        fallback_response = self.build_combined_response(
            request=request,
            results=results,
            conversation_history=conversation_history,
            management=False,
        )

        response_message = self.generate_natural_response(
            request=request,
            results=results,
            conversation_history=conversation_history,
            fallback_response=fallback_response,
        )

        try:
            create_audit_log(
                user=user,
                action="multi_agent_query",
                details={
                    "request": request,
                    "agents": [agent.name for agent in selected_agents],
                },
            )
        except Exception:
            pass

        return {
            "status": "success",
            "intent": "multi_agent",
            "agent": "Multi-Agent Orchestrator",
            "response": response_message,
            "data": {
                "agent_results": results,
                "conversation_context_used": bool(conversation_history),
            },
        }

    # =========================================================
    # FOLLOW-UP QUERY
    # =========================================================

    def process_follow_up_query(
        self,
        request,
        user,
        role,
        credentials=None,
        conversation_history=None,
    ):
        conversation_history = conversation_history or []

        print(
            "FOLLOW-UP REQUEST:",
            request,
        )

        previous_assistant = self.get_last_assistant_message(conversation_history)

        previous_user = self.get_previous_user_message(conversation_history)

        print(
            "PREVIOUS USER MESSAGE:",
            previous_user,
        )

        print(
            "PREVIOUS ASSISTANT MESSAGE:",
            previous_assistant,
        )

        # -----------------------------------------------------
        # 1. Entity context FIRST
        # -----------------------------------------------------

        entity_context = self.get_entity_context_from_conversation(
            request=request,
            conversation_history=conversation_history,
        )

        print(
            "ENTITY CONTEXT:",
            entity_context,
        )

        # -----------------------------------------------------
        # 2. Current request agents
        # -----------------------------------------------------

        current_agents = self.get_agents_from_request(request)

        print(
            "AGENTS FROM CURRENT REQUEST:",
            [agent.name for agent in current_agents],
        )

        # -----------------------------------------------------
        # 3. Explicit entity gets priority
        #
        # Example:
        # "What about AI Dashboard?"
        #
        # Entity -> Project Agent
        #
        # Do NOT inherit Sales/Finance from old assistant text.
        # -----------------------------------------------------

        entity_agents = self.get_agents_from_entities(entity_context)

        if entity_agents:

            if current_agents:

                # Keep only agents relevant to the entity
                entity_agent_names = {agent.name for agent in entity_agents}

                filtered_agents = [
                    agent
                    for agent in current_agents
                    if agent.name in entity_agent_names
                ]

                if filtered_agents:
                    current_agents = filtered_agents

                else:
                    current_agents = entity_agents

            else:

                current_agents = entity_agents

            print(
                "ENTITY-PRIORITY AGENTS:",
                [agent.name for agent in current_agents],
            )

        # -----------------------------------------------------
        # 4. Previous USER agent context
        # -----------------------------------------------------

        if not current_agents:

            current_agents = self.get_agents_from_conversation(conversation_history)

        print(
            "AGENTS AFTER CONVERSATION CONTEXT:",
            [agent.name for agent in current_agents],
        )

        # -----------------------------------------------------
        # 5. Attention question detection
        # -----------------------------------------------------

        attention_keywords = [
            "which area",
            "which one",
            "needs attention",
            "most attention",
            "what should i focus",
            "what should we focus",
            "what should i do",
            "what should we do",
            "what next",
            "priorities",
            "priority",
        ]

        request_lower = request.lower()

        is_attention_question = any(
            keyword in request_lower for keyword in attention_keywords
        )

        # -----------------------------------------------------
        # 6. Management attention questions
        # -----------------------------------------------------

        if is_attention_question:

            management_names = [
                "HR Agent",
                "Project Agent",
                "Sales Agent",
                "Finance Agent",
                "Calendar Agent",
            ]

            management_agents = [
                agent
                for agent in self.registry.get_agents()
                if agent.name in management_names
            ]

            if management_agents:
                current_agents = management_agents

        # -----------------------------------------------------
        # 7. No agent found
        # -----------------------------------------------------

        if not current_agents:

            if previous_assistant:

                return {
                    "status": "success",
                    "intent": "contextual_follow_up",
                    "agent": "Conversation Context",
                    "response": (
                        "I can continue from our previous "
                        "conversation, but I could not identify "
                        "the specific business area you want "
                        "to explore. You can mention Sales, "
                        "Finance, Projects, HR, Marketing, "
                        "Operations, QA, Customer Support, "
                        "Developer, GitHub, CRM, or Calendar."
                    ),
                    "data": {
                        "conversation_context_used": True,
                        "previous_user_message": previous_user,
                        "entity_context": entity_context,
                    },
                }

            return {
                "status": "error",
                "intent": "contextual_follow_up",
                "agent": "Conversation Context",
                "response": (
                    "I need a little more information to "
                    "understand the follow-up question."
                ),
            }

        # -----------------------------------------------------
        # 8. Execute contextual agents
        # -----------------------------------------------------

        results = []

        for agent in current_agents:

            agent_name = agent.name

            agent_request = self.get_contextual_agent_request(
                request=request,
                agent_name=agent_name,
                previous_assistant=previous_assistant,
                previous_user=previous_user,
                entity_context=entity_context,
                attention_question=is_attention_question,
            )

            print(
                "CONTEXTUAL AGENT:",
                agent_name,
            )

            print(
                "CONTEXTUAL ENTITY:",
                entity_context,
            )

            print(
                "CONTEXTUAL AGENT REQUEST:",
                agent_request,
            )

            result = self.execute_agent(
                agent=agent,
                agent_request=agent_request,
                user=user,
                credentials=credentials,
            )

            results.append(result)

        # -----------------------------------------------------
        # 9. Fallback response
        # -----------------------------------------------------

        fallback_response = self.build_follow_up_response(
            request=request,
            results=results,
            previous_assistant=previous_assistant,
            attention_question=is_attention_question,
        )

        # -----------------------------------------------------
        # 10. Natural response
        # -----------------------------------------------------

        response_message = self.generate_natural_response(
            request=request,
            results=results,
            conversation_history=conversation_history,
            fallback_response=fallback_response,
        )

        # -----------------------------------------------------
        # 11. Audit log
        # -----------------------------------------------------

        try:
            create_audit_log(
                user=user,
                action="contextual_follow_up_query",
                details={
                    "request": request,
                    "previous_user_message": previous_user,
                    "agents": [agent.name for agent in current_agents],
                    "entity_context": entity_context,
                },
            )
        except Exception:
            pass

        return {
            "status": "success",
            "intent": "contextual_follow_up",
            "agent": "Multi-Agent Orchestrator",
            "response": response_message,
            "data": {
                "agent_results": results,
                "conversation_context_used": True,
                "entity_context": entity_context,
            },
        }

    # =========================================================
    # FOLLOW-UP RESPONSE FALLBACK
    # =========================================================

    def build_follow_up_response(
        self,
        request,
        results,
        previous_assistant="",
        attention_question=False,
    ):
        """
        Build a natural fallback response when the LLM
        is unavailable.
        """

        successful_results = [
            result for result in results if result.get("status") == "success"
        ]

        denied_results = [
            result for result in results if result.get("status") == "denied"
        ]

        error_results = [
            result for result in results if result.get("status") == "error"
        ]

        # -----------------------------------------------------
        # No successful results
        # -----------------------------------------------------

        if not successful_results:

            if denied_results:
                return (
                    "I found the relevant business information, "
                    "but your current role does not have permission "
                    "to access the requested area."
                )

            if error_results:
                return (
                    "I could not retrieve the relevant business "
                    "information at the moment."
                )

            return (
                "I could not retrieve enough information to "
                "answer your follow-up question."
            )

        # -----------------------------------------------------
        # Attention / priority questions
        # -----------------------------------------------------

        if attention_question:

            attention_items = []

            for result in successful_results:

                agent_name = result.get(
                    "agent",
                    "Business Agent",
                )

                message = result.get(
                    "message",
                    "",
                )

                data = result.get(
                    "data",
                    {},
                )

                combined_text = (
                    f"{message} " f"{self.format_data_for_response(data)}"
                ).lower()

                signals = []

                if any(
                    keyword in combined_text
                    for keyword in [
                        "delayed",
                        "delay",
                        "overdue",
                        "risk",
                        "deadline",
                    ]
                ):
                    signals.append("deadlines, delays, or risks")

                if any(
                    keyword in combined_text
                    for keyword in [
                        "pending follow-up",
                        "pending followups",
                        "follow-up",
                        "follow up",
                        "followups",
                    ]
                ):
                    signals.append("pending sales follow-ups")

                if any(
                    keyword in combined_text
                    for keyword in [
                        "overdue payment",
                        "expense",
                        "financial issue",
                        "financial",
                        "finance",
                        "profit",
                        "revenue",
                    ]
                ):
                    signals.append("financial items")

                if any(
                    keyword in combined_text
                    for keyword in [
                        "open issue",
                        "pending issue",
                        "customer issue",
                        "unresolved",
                    ]
                ):
                    signals.append("open or unresolved issues")

                if signals:
                    attention_items.append(f"{agent_name}: " + ", ".join(signals))

            response_parts = [
                (
                    "Based on the current information, "
                    "these are the areas showing items "
                    "that may need attention:"
                )
            ]

            if attention_items:

                for item in attention_items:
                    response_parts.append(f"- {item}")

            else:

                response_parts.append(
                    "I do not see a clearly identified "
                    "attention item in the available data."
                )

            response_parts.append(
                "You can ask me to drill down into "
                "any of these areas and I can provide "
                "more details."
            )

            if denied_results:
                response_parts.append(
                    "Some areas were excluded because " "of your current permissions."
                )

            return "\n".join(response_parts)

        # -----------------------------------------------------
        # Single-agent conversational fallback
        # -----------------------------------------------------

        if len(successful_results) == 1:

            result = successful_results[0]

            agent_name = result.get(
                "agent",
                "Business Agent",
            )

            message = result.get(
                "message",
                "",
            ).strip()

            data = result.get(
                "data",
                {},
            )

            # Project Agent fallback
            if agent_name == "Project Agent" and message:

                natural_message = message

                natural_message = natural_message.replace(
                    "is currently Delayed",
                    "is currently delayed",
                )

                natural_message = natural_message.replace(
                    "is currently Active",
                    "is currently active",
                )

                natural_message = natural_message.replace(
                    "is currently Completed",
                    "is currently completed",
                )

                if "delayed" in natural_message.lower():

                    natural_message += (
                        " The project is still in progress, "
                        "and the available project data does not "
                        "currently provide a specific reason "
                        "for the delay."
                    )

                return natural_message

            # Other single-agent responses
            if message:
                return message

            if data:
                return self.format_data_for_response(data)

        # -----------------------------------------------------
        # Multi-agent conversational fallback
        # -----------------------------------------------------

        response_parts = [
            "Here is the latest information based " "on our conversation:"
        ]

        for result in successful_results:

            agent_name = result.get(
                "agent",
                "Business Agent",
            )

            message = result.get(
                "message",
                "",
            )

            data = result.get(
                "data",
                {},
            )

            if not message and not data:
                continue

            section = f"### {agent_name}\n"

            if message:
                section += message.strip()

            elif data:
                section += self.format_data_for_response(data)

            response_parts.append(section)

        if denied_results:
            response_parts.append(
                "Some requested information was not "
                "included because your current role "
                "does not have permission to access it."
            )

        if error_results:
            response_parts.append(
                "Some business areas could not be " "refreshed at this time."
            )

        response_parts.append(
            "You can continue the conversation by "
            "asking about any specific area, metric, "
            "project, or issue."
        )

        return "\n\n".join(response_parts)

    # =========================================================
    # COMBINED RESPONSE FALLBACK
    # =========================================================

    def build_combined_response(
        self,
        request,
        results,
        conversation_history=None,
        management=False,
    ):
        conversation_history = conversation_history or []

        successful_results = [
            result for result in results if result.get("status") == "success"
        ]

        denied_results = [
            result for result in results if result.get("status") == "denied"
        ]

        error_results = [
            result for result in results if result.get("status") == "error"
        ]

        if not successful_results:

            if denied_results:
                return (
                    "I found the requested business areas, "
                    "but your current role does not have "
                    "permission to access the available "
                    "information."
                )

            return (
                "I could not retrieve the requested "
                "business information at the moment."
            )

        if management:

            response_parts = [
                (
                    "Here is the combined business overview "
                    "based on the available information."
                )
            ]

        else:

            response_parts = [
                (
                    "I checked the relevant business areas "
                    "and combined the available information "
                    "below."
                )
            ]

        for result in successful_results:

            agent_name = result.get(
                "agent",
                "Business Agent",
            )

            message = result.get(
                "message",
                "",
            )

            data = result.get(
                "data",
                {},
            )

            if not message and not data:
                continue

            section = f"### {agent_name}\n"

            if message:
                section += message.strip()

            elif data:
                section += self.format_data_for_response(data)

            response_parts.append(section)

        if denied_results:
            response_parts.append(
                "Some information was not included "
                "because your current role does not "
                "have permission to access those areas."
            )

        if error_results:
            response_parts.append(
                "A few business areas could not be " "refreshed at this time."
            )

        response_parts.append(
            "You can ask a follow-up question about "
            "any of these areas and I can continue "
            "from this conversation."
        )

        return "\n\n".join(response_parts)

    # =========================================================
    # DATA FORMATTER
    # =========================================================

    def format_data_for_response(
        self,
        data,
    ):
        if not data:
            return ""

        if isinstance(data, str):
            return data

        if isinstance(data, list):

            lines = []

            for item in data:

                if isinstance(item, dict):

                    values = []

                    for key, value in item.items():
                        values.append(f"{key}: {value}")

                    lines.append("- " + ", ".join(values))

                else:
                    lines.append(f"- {item}")

            return "\n".join(lines)

        if isinstance(data, dict):

            lines = []

            for key, value in data.items():

                if key == "agent_results":
                    continue

                readable_key = key.replace(
                    "_",
                    " ",
                ).title()

                if isinstance(
                    value,
                    (dict, list),
                ):

                    lines.append(f"{readable_key}:")

                    nested = self.format_data_for_response(value)

                    if nested:
                        lines.append(nested)

                else:

                    lines.append(f"{readable_key}: {value}")

            return "\n".join(lines)

        return str(data)

    # =========================================================
    # MAIN REQUEST PROCESSOR
    # =========================================================

    def process_request(
        self,
        request,
        user,
        role,
        credentials=None,
        conversation_history=None,
    ):
        """
        Main entry point for every AI chat request.

        Routing order:

        1. Contextual follow-up
        2. Management / business overview
        3. Multi-agent request
        4. Single-agent request
        """

        conversation_history = conversation_history or []

        print("=" * 60)

        print("AI ORCHESTRATOR REQUEST")

        print(
            "REQUEST:",
            request,
        )

        print(
            "CONVERSATION HISTORY COUNT:",
            len(conversation_history),
        )

        print(
            "FOLLOW-UP DETECTED:",
            self.is_follow_up_question(
                request,
                conversation_history,
            ),
        )

        print("=" * 60)

        # =====================================================
        # 1. CONTEXTUAL FOLLOW-UP
        # =====================================================

        if conversation_history and self.is_follow_up_question(
            request,
            conversation_history,
        ):

            print("ROUTING: CONTEXTUAL FOLLOW-UP")

            return self.process_follow_up_query(
                request=request,
                user=user,
                role=role,
                credentials=credentials,
                conversation_history=conversation_history,
            )

        # =====================================================
        # 2. MANAGEMENT QUERY
        # =====================================================

        if self.is_management_query(request):

            print("ROUTING: MANAGEMENT QUERY")

            return self.process_management_query(
                request=request,
                user=user,
                role=role,
                credentials=credentials,
                conversation_history=conversation_history,
            )

        # =====================================================
        # 3. AGENT SELECTION
        # =====================================================
        # Known entities must take priority over generic keyword
        # matching. This prevents requests such as
        # "What is the status of Payment Integration?" from
        # being incorrectly routed to HR because of a keyword
        # score elsewhere in the registry.

        entity_context = self.get_entity_context_from_conversation(
            request=request,
            conversation_history=conversation_history,
        )

        entity_agents = self.get_agents_from_entities(entity_context)

        if entity_agents:
            selected_agents = entity_agents
            print(
                "ENTITY-PRIORITY AGENTS:",
                [agent.name for agent in selected_agents],
            )
        else:
            selected_agents = self.registry.find_relevant_agents(request)

        print(
            "RELEVANT AGENTS:",
            [agent.name for agent in selected_agents],
        )

        if len(selected_agents) >= 2:

            print("ROUTING: MULTI-AGENT")

            return self.process_multi_agent_query(
                request=request,
                user=user,
                role=role,
                credentials=credentials,
                conversation_history=conversation_history,
            )

        # =====================================================
        # 4. SINGLE AGENT QUERY
        # =====================================================

        if len(selected_agents) == 1:
            agent = selected_agents[0]
            intent_result = {
                "intent": agent.name,
                "agent": agent,
            }
        else:
            intent_result = self.understand_intent(request)
            agent = intent_result["agent"]

        print(
            "SINGLE AGENT:",
            agent.name if agent else None,
        )

        if agent is None:

            if conversation_history:

                response_message = (
                    "I understand that you are "
                    "continuing our conversation, "
                    "but I could not identify the "
                    "business area needed for this "
                    "request. Could you provide a "
                    "little more detail about what "
                    "you would like me to check?"
                )

            else:

                response_message = (
                    "I could not identify the business "
                    "area needed for this request. "
                    "You can ask me about areas such "
                    "as Sales, Finance, Projects, HR, "
                    "Marketing, Operations, QA, "
                    "Customer Support, Developer, "
                    "GitHub, CRM, or Calendar."
                )

            try:

                create_audit_log(
                    user=user,
                    action="unknown_query",
                    details={
                        "request": request,
                    },
                )

            except Exception:
                pass

            return {
                "status": "success",
                "intent": "unknown",
                "agent": "Vetri AI",
                "response": response_message,
                "data": {
                    "conversation_context_used": bool(conversation_history),
                },
            }

        # =====================================================
        # 5. PERMISSION CHECK
        # =====================================================

        agent_name = agent.name

        allowed = self.check_agent_permission(
            user=user,
            agent_name=agent_name,
        )

        if not allowed:

            response_message = (
                f"You do not have permission to " f"access {agent_name} information."
            )

            try:

                create_audit_log(
                    user=user,
                    action="permission_denied",
                    details={
                        "request": request,
                        "agent": agent_name,
                    },
                )

            except Exception:
                pass

            return {
                "status": "error",
                "intent": agent_name,
                "agent": agent_name,
                "response": response_message,
            }

        # =====================================================
        # 6. EXECUTE SINGLE AGENT
        # =====================================================

        result = self.execute_agent(
            agent=agent,
            agent_request=request,
            user=user,
            credentials=credentials,
        )

        if result.get("status") == "error":

            try:

                create_audit_log(
                    user=user,
                    action="agent_error",
                    details={
                        "request": request,
                        "agent": agent_name,
                        "error": result.get(
                            "error",
                            "",
                        ),
                    },
                )

            except Exception:
                pass

            return {
                "status": "error",
                "intent": agent_name,
                "agent": agent_name,
                "response": result.get(
                    "message",
                    (
                        f"{agent_name} could not "
                        "process your request at "
                        "the moment."
                    ),
                ),
            }

        # =====================================================
        # 7. AUDIT LOG
        # =====================================================

        try:

            create_audit_log(
                user=user,
                action="agent_query",
                details={
                    "request": request,
                    "agent": agent_name,
                },
            )

        except Exception:
            pass

        # =====================================================
        # 8. NATURAL RESPONSE
        # =====================================================

        fallback_response = result.get(
            "message",
            result.get(
                "response",
                "Request processed successfully.",
            ),
        )

        natural_response = self.generate_natural_response(
            request=request,
            results=[result],
            conversation_history=conversation_history,
            fallback_response=fallback_response,
        )

        # =====================================================
        # 9. RETURN
        # =====================================================

        return {
            "status": result.get(
                "status",
                "success",
            ),
            "intent": agent_name,
            "agent": agent_name,
            "response": natural_response,
            "data": result.get(
                "data",
                {},
            ),
        }
