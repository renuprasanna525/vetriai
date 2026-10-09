from .registry import AgentRegistry
from permissions.permission_engine import PermissionEngine
from audit_logs.utils import create_audit_log
from audit_logs.models import AuditLog
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
            # Management attention questions
            "which areas need attention",
            "which area needs attention",
            "which areas need the most attention",
            "which area needs the most attention",
            "which areas need attention first",
            "which area needs attention first",
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

    def is_confirmation_reply(self, request):
        """Detect short replies that confirm a previous offer."""
        normalized = request.lower().strip().rstrip("!.,?")

        confirmations = {
            "yes",
            "yes please",
            "yes, please",
            "yeah",
            "yep",
            "sure",
            "okay",
            "ok",
            "please do",
            "go ahead",
            "show me",
            "show it",
            "continue",
            "proceed",
            "tell me more",
        }

        return normalized in confirmations

    def is_rejection_reply(self, request):
        """Detect short replies that reject a previous offer."""
        normalized = request.lower().strip().rstrip("!.,?")

        rejections = {
            "no",
            "no thanks",
            "no, thanks",
            "not now",
            "no need",
            "that's okay",
            "that is okay",
            "don't",
            "do not",
            "cancel",
        }

        return normalized in rejections

    def is_ambiguous_pending_reference(
        self,
        request,
        conversation_history=None,
    ):
        """
        Detect questions such as:

            "How many of those are pending?"
            "How many of these are pending?"

        when the previous sales conversation contains more than
        one possible pending category, such as pending follow-ups
        and pending orders.

        The system should ask the user to clarify instead of guessing.
        """

        conversation_history = conversation_history or []

        request_lower = request.lower().strip()

        ambiguous_phrases = [
            "how many are pending",
            "how many of those are pending",
            "how many of these are pending",
            "which of those are pending",
            "which of these are pending",
            "which are pending",
        ]

        if not any(phrase in request_lower for phrase in ambiguous_phrases):
            return False

        previous_user = self.get_previous_user_message(
            conversation_history,
            current_request=request,
        )

        previous_assistant = self.get_last_assistant_message(conversation_history)

        combined_context = (f"{previous_user} {previous_assistant}").lower()

        has_followups = any(
            phrase in combined_context
            for phrase in [
                "follow-up",
                "follow up",
                "followups",
                "pending follow",
            ]
        )

        has_orders = any(
            phrase in combined_context
            for phrase in [
                "order",
                "orders",
                "pending order",
                "pending orders",
            ]
        )
        print("AMBIGUOUS PENDING DEBUG:")
        print("REQUEST:", request)
        print("REQUEST LOWER:", request_lower)
        print("PREVIOUS USER:", previous_user)
        print("HAS FOLLOWUPS:", has_followups)
        print("HAS ORDERS:", has_orders)
        print("COMBINED CONTEXT:", combined_context)

        return has_followups and has_orders

    def is_follow_up_question(
        self,
        request,
        conversation_history=None,
    ):
        """
        Detect questions that depend on previous conversation context.
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
            "first one",
            "second one",
            "third one",
            "first order",
            "second order",
            "third order",
            "waiting the longest",
            "waited the longest",
            "longest waiting",
            "longest-waiting",
            "longest pending",
            "most days pending",
            "how many of those",
            "how many of these",
            "how many are pending",
            "what needs my attention",
            "what needs my attention first",
            "what needs attention first",
            "what needs attention most",
            "what should i attend to first",
            "what should i prioritize",
            "what should i prioritize first",
            "what is most urgent",
            "what is urgent",
            "which needs attention",
            "which needs attention first",
            "what needs to be handled first",
            "what should be handled first",
        ]

        request_lower = request.lower().strip()

        if not conversation_history:
            return False

        # -----------------------------------------------------
        # Normalize punctuation for reference detection
        # -----------------------------------------------------
        normalized_request = (
            request_lower.replace("?", " ")
            .replace("!", " ")
            .replace(",", " ")
            .replace(".", " ")
            .replace(":", " ")
            .replace(";", " ")
        )

        normalized_request = " ".join(normalized_request.split())

        # Direct follow-up phrase detection.
        if any(keyword in request_lower for keyword in follow_up_keywords):
            return True

        # Entity-reference follow-up detection.
        entity_context = self.get_entity_context_from_conversation(
            request=request,
            conversation_history=conversation_history,
        )
        # TEMPORARY DEBUG
        print("FOLLOW-UP DEBUG REQUEST:", repr(request))
        print("FOLLOW-UP DEBUG NORMALIZED:", repr(normalized_request))
        print("FOLLOW-UP DEBUG ENTITIES:", entity_context)
        print("FOLLOW-UP DEBUG WORDS:", normalized_request.split())

        if not entity_context:
            return False

        reference_phrases = [
            "it",
            "its",
            "their",
            "that",
            "this",
            "those",
            "these",
            "them",
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

        # Exact reference question
        if normalized_request in reference_phrases:
            return True
        # -----------------------------------------------------
        # Reference words
        # -----------------------------------------------------
        words = normalized_request.split()

        if any(
            word in words for word in ["it", "its", "their", "those", "these", "them"]
        ):
            return True

        # -----------------------------------------------------
        # Explicit reference patterns
        # -----------------------------------------------------

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

        if ("that" in words or "this" in words) and any(
            phrase in request_lower for phrase in reference_patterns
        ):
            return True
        print("FOLLOW-UP DEBUG RESULT: No follow-up condition matched")
        return False

    # ADD THE NEW HELPER HERE
    def is_clarification_reply(self, request, conversation_history):
        """
        Detect short replies that answer the assistant's
        previous clarification question.
        """
        if not conversation_history:
            return False

        previous_assistant = self.get_last_assistant_message(conversation_history)

        if not previous_assistant:
            return False

        assistant_text = previous_assistant.lower()
        request_text = request.lower().strip().rstrip(".!?")
        # The previous assistant must have asked for clarification.
        clarification_phrases = [
            "do you mean",
            "which one do you mean",
            "which do you mean",
            "are you referring to",
        ]

        if not any(phrase in assistant_text for phrase in clarification_phrases):
            return False

        # Recognize the options in the pending sales clarification.
        clarification_options = {
            "orders": [
                "orders",
                "order",
            ],
            "follow_ups": [
                "follow-ups",
                "follow ups",
                "followup",
                "followups",
            ],
        }

        return any(
            request_text == option
            or request_text == f"the {option}"
            or request_text == f"those {option}"
            for options in clarification_options.values()
            for option in options
        )

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

    def assistant_offered_details(self, conversation_history):
        """Check whether the latest assistant message offered an action."""
        message = self.get_last_assistant_message(conversation_history).lower()

        offer_phrases = [
            "would you like to see",
            "would you like me to show",
            "would you like more details",
            "do you want to see",
            "shall i show",
            "i can show you",
            "i can provide more details",
            "would you like me to retrieve",
        ]

        return any(phrase in message for phrase in offer_phrases)

    def get_previous_user_message(
        self,
        conversation_history,
        current_request=None,
    ):
        """
        Get the previous user message from conversation history.

        Supports both history formats:

        1. History includes the current user message.
        2. History contains only messages from before the current request.

        If current_request is supplied and the latest user message
        matches it, that message is skipped.
        """

        if not conversation_history:
            return ""

        current_request_normalized = ""

        if current_request:
            current_request_normalized = str(current_request).strip().lower()

        for message in reversed(conversation_history):

            if message.get("sender") != "user":
                continue

            content = message.get(
                "content",
                "",
            )

            if not content:
                continue

            content_normalized = str(content).strip().lower()

            # If the current request is already inside history,
            # skip it and continue looking for the previous user message.
            if (
                current_request_normalized
                and content_normalized == current_request_normalized
            ):
                continue

            return content

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

        The specialized agents remain responsible for
        retrieving business information.

        The LLM is responsible only for:
        - understanding the conversation context
        - organizing verified information
        - explaining results naturally
        - producing a ChatGPT-style response

        If the LLM is unavailable, the application
        fallback response is returned.
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
        unsupported_results = [
            result for result in results if result.get("status") == "unsupported"
        ]

        # =====================================================
        # NO SUCCESSFUL RESULTS
        # =====================================================

        if not successful_results:
            if unsupported_results:
                unsupported_context = []

                for result in unsupported_results:
                    message = result.get("message", "").strip()

                    if message:
                        unsupported_context.append(message)
                if unsupported_context:
                    fallback_response = " ".join(unsupported_context)

                else:
                    fallback_response = (
                        "The requested information or action "
                        "is not currently supported."
                    )
                try:
                    response = self.llm_service.generate_chat_response(
                        question=request,
                        agent_results=[
                            {
                                "agent": result.get(
                                    "agent",
                                    "Business Agent",
                                ),
                                "status": "unsupported",
                                "message": result.get(
                                    "message",
                                    "",
                                ),
                                "data": {},
                            }
                            for result in unsupported_results
                        ],
                        conversation_context=self.format_conversation_context(
                            conversation_history
                        ),
                    )
                    if response and response.strip():
                        return response.strip()
                except Exception as error:
                    print(
                        "UNSUPPORTED RESPONSE LLM ERROR:",
                        str(error),
                    )

                return (
                    f"{fallback_response} "
                    "I can still help you with the business "
                    "areas and information currently available "
                    "in Vetri AI. Please feel free to ask me "
                    "another question."
                )
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

        # =====================================================
        # CONVERSATION CONTEXT
        # =====================================================

        conversation_context = self.format_conversation_context(conversation_history)

        # =====================================================
        # PREPARE VERIFIED AGENT RESULTS
        # =====================================================
        #
        # Only the useful business result fields are sent
        # to the LLM.
        #
        # Internal implementation details are not required.
        # =====================================================

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
        print("NATURAL RESULTS SENT TO GROQ:", natural_results)

        # =====================================================
        # CALL LLM FOR ALL SUCCESSFUL RESPONSES
        # =====================================================
        #
        # Previously:
        #
        #   single agent -> direct message
        #   multiple agents -> LLM
        #
        # Now:
        #
        #   single agent -> LLM
        #   multiple agents -> LLM
        #   follow-up -> LLM
        #   management -> LLM
        #
        # This creates one consistent conversational layer.
        # =====================================================

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

        # =====================================================
        # LLM UNAVAILABLE
        # =====================================================
        #
        # The application still returns the verified
        # fallback response.
        # =====================================================
        if fallback_response:
            return fallback_response

        # =====================================================
        # FINAL SAFE FALLBACK
        # =====================================================

        if len(successful_results) == 1:

            result = successful_results[0]

            message = result.get(
                "message",
                "",
            ).strip()

            data = result.get(
                "data",
                {},
            )

            if message:
                return message

            if data:
                return self.format_data_for_response(data)

        # =====================================================
        # MULTI-AGENT FALLBACK
        # =====================================================

        return self.build_combined_response(
            request=request,
            results=results,
            conversation_history=conversation_history,
            management=False,
        )

    # =========================================================
    # AGENT CONTEXT DETECTION
    # =========================================================

    def get_agents_from_conversation(
        self,
        conversation_history,
        current_request=None,
    ):
        """
        Identify the most recent explicit business topic
        from earlier user messages.

        Priority:
        1. Most recent earlier user message with an agent topic
        2. Previous assistant message as a limited fallback
        """

        if not conversation_history:
            return []

        available_agents = self.registry.get_agents()

        current_request_normalized = (
            str(current_request).strip().lower() if current_request else ""
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
                "opportunity",
                "opportunities",
                "conversion",
                "conversions",
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

            text_lower = str(text).lower()
            detected_agents = []

            for agent in available_agents:
                agent_name = agent.name

                if agent_name.lower() in text_lower:
                    detected_agents.append(agent)
                    continue

                keywords = agent_keywords.get(agent_name, [])

                if any(keyword in text_lower for keyword in keywords):
                    detected_agents.append(agent)

            # Remove duplicates while preserving order.
            unique_agents = []
            seen_names = set()

            for agent in detected_agents:
                if agent.name not in seen_names:
                    unique_agents.append(agent)
                    seen_names.add(agent.name)

            return unique_agents

        # -----------------------------------------------------
        # 1. Search earlier USER messages, newest first.
        # Skip the current request if it is already in history.
        # Continue past generic follow-ups such as:
        # "Tell me more about them."
        # -----------------------------------------------------

        for message in reversed(conversation_history):

            if message.get("sender") != "user":
                continue

            content = message.get("content", "")

            if not content:
                continue

            content_normalized = str(content).strip().lower()

            if (
                current_request_normalized
                and content_normalized == current_request_normalized
            ):
                continue

            user_agents = detect_agents_from_text(content)

            if user_agents:
                print("CONTEXT SOURCE: EARLIER EXPLICIT USER TOPIC")
                print(
                    "TOPIC USER MESSAGE:",
                    content,
                )
                print(
                    "CONTEXT AGENTS:",
                    [agent.name for agent in user_agents],
                )

                return user_agents

        # -----------------------------------------------------
        # 2. Limited fallback to the previous assistant message
        # only if no earlier user message identified a topic.
        # -----------------------------------------------------

        previous_assistant = self.get_last_assistant_message(conversation_history)

        if previous_assistant:
            assistant_agents = detect_agents_from_text(previous_assistant)

            if assistant_agents:
                print("CONTEXT SOURCE: PREVIOUS ASSISTANT MESSAGE")
                print(
                    "PREVIOUS ASSISTANT CONTEXT AGENTS:",
                    [agent.name for agent in assistant_agents],
                )

                return assistant_agents

        # -----------------------------------------------------
        # 3. No matching context
        # -----------------------------------------------------

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
        """
        # TEMPORARY DEBUG PRINTS — ADD HERE
        print("========== ENTITY CONTEXT INPUT DEBUG ==========")
        print("CURRENT REQUEST:", repr(request))
        print("HISTORY COUNT:", len(conversation_history or []))
        print("HISTORY:", repr(conversation_history))
        print("================================================")

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

            # Normalize regular spaces, non-breaking spaces,
            # narrow non-breaking spaces, and repeated whitespace.
            text_lower = str(text).replace("\u00a0", " ").replace("\u202f", " ")
            text_lower = " ".join(text_lower.casefold().split())

            detected_entities = []

            for entity in known_entities:
                normalized_entity = entity.replace("\u00a0", " ").replace("\u202f", " ")
                normalized_entity = " ".join(normalized_entity.casefold().split())

                if normalized_entity in text_lower:
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

        previous_user = self.get_previous_user_message(
            conversation_history,
            current_request=request,
        )

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
        print(
            "DEBUG PREVIOUS ASSISTANT TEXT:",
            repr(previous_assistant),
        )

        previous_assistant_entities = detect_entities_from_text(previous_assistant)
        print(
            "DEBUG PREVIOUS ASSISTANT ENTITIES:",
            previous_assistant_entities,
        )

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
        Route order-ID queries directly to the Sales Agent.
        """

        request_lower = str(request).lower()

        # Direct order-ID detection
        if "ord-" in request_lower:

            sales_agent = next(
                (
                    agent
                    for agent in self.registry.get_agents()
                    if agent.name.lower() == "sales agent"
                ),
                None,
            )

            if sales_agent:
                print("DIRECT ORDER ID DETECTED: Sales Agent")

                return [sales_agent]

        # Existing registry-based detection
        return self.registry.find_relevant_agents(request)

    # =========================================================
    # PERMISSION HELPER
    # =========================================================
    def check_agent_permission(
        self,
        user,
        agent_name,
        agent=None,
        agent_request=None,
    ):
        """
        Check whether the user's role is allowed to access
        the permission required for this specific request.
        """

        # Get the user's role from UserProfile
        role = None

        try:
            if hasattr(user, "profile"):
                role = user.profile.role
        except Exception:
            role = None

        # Superuser should always use the application admin role
        if getattr(user, "is_superuser", False):
            role = "admin"

        if not role:
            return False

        # Default agent -> permission mapping.
        # Used when an agent does not provide request-specific
        # permission logic.
        agent_permissions = {
            "Finance Agent": "view_finance",
            "Sales Agent": "view_sales",
            "Project Agent": "view_projects",
            "Reporting Agent": "view_reports",
            "HR Agent": "view_employees",
            "Marketing Agent": "view_marketing",
            "Developer Agent": "view_developer",
            "QA Agent": "view_qa",
            "Operations Agent": "view_operations",
            "Customer Support Agent": "view_customer_support",
            "GitHub Agent": "view_github",
            "Cloud Storage Agent": "view_cloud_storage",
            "CRM Agent": "view_crm",
            "Calendar Agent": "view_calendar",
        }

        # Unknown agents are denied instead of being allowed
        # accidentally.
        permission = agent_permissions.get(agent_name)

        if not permission:
            return False

        # Use request-specific permission logic when available.
        if (
            agent is not None
            and agent_request
            and callable(getattr(agent, "get_required_permission", None))
        ):
            try:
                required_permission = agent.get_required_permission(
                    agent_request, user=user
                )
                print("AGENT REQUIRED PERMISSION:", required_permission)

                if required_permission:
                    permission = required_permission

            except Exception:
                pass
        print("\n========== PERMISSION DEBUG ==========")
        print("AGENT:", agent_name)
        print("ROLE:", role)
        print("REQUEST:", repr(agent_request))
        print("FINAL PERMISSION:", permission)

        result = self.permission_engine.check_permission(
            role,
            permission,
        )

        print("PERMISSION RESULT:", result)
        print("======================================\n")

        return result.get("allowed", False)

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
            agent=agent,
            agent_request=agent_request,
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
    # STRUCTURED AGENT-TO-AGENT COLLABORATION
    # =========================================================

    def request_agent_collaboration(
        self,
        requesting_agent,
        target_agent_name,
        collaboration_request,
        user,
        credentials=None,
    ):
        """
        Allow one agent to request structured information
        from another agent through the existing orchestrator.

        The target agent is executed through execute_agent()
        so the normal permission checks remain active.
        """

        requesting_agent_name = (
            requesting_agent.name
            if hasattr(requesting_agent, "name")
            else str(requesting_agent)
        )

        print("=" * 60)
        print("AGENT COLLABORATION REQUEST")
        print("REQUESTING AGENT:", requesting_agent_name)
        print("TARGET AGENT:", target_agent_name)
        print("COLLABORATION REQUEST:", collaboration_request)
        print("=" * 60)

        target_agent = None

        for agent in self.registry.get_agents():

            if agent.name == target_agent_name:
                target_agent = agent
                break

        if target_agent is None:

            print(
                "COLLABORATION TARGET NOT FOUND:",
                target_agent_name,
            )

            return {
                "type": "agent_collaboration",
                "requesting_agent": requesting_agent_name,
                "target_agent": target_agent_name,
                "status": "error",
                "message": (
                    f"{target_agent_name} is not available " "for collaboration."
                ),
                "data": {},
            }

        result = self.execute_agent(
            agent=target_agent,
            agent_request=collaboration_request,
            user=user,
            credentials=credentials,
        )

        collaboration_result = {
            "type": "agent_collaboration",
            "requesting_agent": requesting_agent_name,
            "target_agent": target_agent_name,
            "status": result.get(
                "status",
                "success",
            ),
            "data": result.get(
                "data",
                {},
            ),
            "message": result.get(
                "message",
                "",
            ),
        }

        print(
            "AGENT COLLABORATION RESULT:",
            collaboration_result,
        )

        try:

            create_audit_log(
                user=user,
                action="agent_collaboration",
                details={
                    "requesting_agent": requesting_agent_name,
                    "target_agent": target_agent_name,
                    "request": collaboration_request,
                    "status": collaboration_result["status"],
                },
            )

        except Exception:
            pass

        return collaboration_result

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
                    "Give current sales information and identify "
                    "the specific sales item that may need attention "
                    "based on the previous conversation. Focus on "
                    "the same sales topic discussed previously. "
                    "If the previous conversation was specifically "
                    "about new leads, focus only on those new leads. "
                    "Use only information returned by the CRM. "
                    "If individual lead details are unavailable, "
                    "clearly state that a specific lead cannot be "
                    "identified. Do not switch to orders, follow-ups, "
                    "customers, or a general sales summary unless "
                    "the user explicitly asks for them. "
                    "Do not invent information."
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
                    "Continue the same HR topic from the previous conversation. "
                    "If the previous conversation was about an employee's salary, "
                    "retrieve the salary for the employee identified in the current "
                    "request. If the previous conversation was about attendance, "
                    "retrieve attendance information for the employee identified "
                    "in the current request. If it was about leave, retrieve the "
                    "relevant leave information. If it was about employee details, "
                    "retrieve the relevant employee information. Preserve the "
                    "previous HR topic when the current request only changes the "
                    "employee or refers to another employee. Use only available "
                    "HR data and do not invent information."
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
        # Sales-specific contextual follow-up requests
        # -----------------------------------------------------

        if agent_name == "Sales Agent":

            # Extract the actual current question when the request
            # already contains the contextual prompt.
            current_question = request

            if "CURRENT USER QUESTION:" in request:
                current_question = request.rsplit("CURRENT USER QUESTION:", 1)[
                    1
                ].strip()

            current_question_lower = current_question.lower()
            previous_user_lower = previous_user.lower()
            # Preserve the previous explicit sales topic for
            # contextual attention questions.
            if attention_question:
                if any(
                    keyword in previous_user_lower
                    for keyword in ["new lead", "new leads"]
                ):
                    base_request = (
                        "The previous conversation was specifically about "
                        "new sales leads. Retrieve current new-lead information "
                        "from the CRM and focus only on those new leads. "
                        "Identify a specific lead needing attention only if "
                        "individual records and relevant priority details are "
                        "available. If they are unavailable, state that clearly. "
                        "Do not switch to follow-ups, orders, customers, or a "
                        "general sales summary. Do not invent information."
                    )
                elif any(
                    keyword in previous_user_lower
                    for keyword in ["follow-up", "follow up", "followups"]
                ):
                    base_request = (
                        "The previous conversation was specifically about "
                        "pending sales follow-ups. Retrieve current pending "
                        "follow-up information from the CRM. Include available "
                        "customer names and pending durations, and identify "
                        "the longest-pending follow-up when the data supports "
                        "that comparison. Do not switch to leads, orders, "
                        "customers, or a general sales summary. Do not invent "
                        "information."
                    )
                elif any(
                    keyword in previous_user_lower for keyword in ["order", "orders"]
                ):
                    base_request = (
                        "The previous conversation was specifically about "
                        "sales orders. Retrieve current order information from "
                        "the CRM and identify any order requiring attention "
                        "only when the available order details support it. "
                        "Do not switch to leads, follow-ups, customers, or a "
                        "general sales summary. Do not invent information."
                    )
                elif any(
                    keyword in previous_user_lower
                    for keyword in ["customer", "customers"]
                ):
                    base_request = (
                        "The previous conversation was specifically about "
                        "sales customers. Retrieve current customer information "
                        "from the CRM and identify any customer requiring "
                        "attention only when the available data supports it. "
                        "Do not switch to leads, follow-ups, orders, or a "
                        "general sales summary. Do not invent information."
                    )

            # Detect vague follow-ups from the current question only.
            is_vague_detail_followup = any(
                phrase in current_question_lower
                for phrase in [
                    "tell me more",
                    "more details",
                    "more information",
                    "explain more",
                    "describe them",
                    "who are they",
                    "which ones",
                ]
            )

            if is_vague_detail_followup:
                # An explicit topic in the current question takes priority
                # over the previous conversation topic.
                if any(
                    keyword in current_question_lower
                    for keyword in [
                        "follow-up",
                        "follow up",
                        "followups",
                    ]
                ):
                    base_request = (
                        "Retrieve more information specifically about "
                        "the pending sales follow-ups requested by the user. "
                        "Include the customers requiring follow-up and "
                        "how long each has been pending, when available. "
                        "Do not switch to leads, orders, customers, or a "
                        "general sales summary. Do not invent information."
                    )

                # Preserve the specific topic from the previous question.
                elif any(
                    keyword in previous_user_lower
                    for keyword in ["new lead", "new leads"]
                ):
                    base_request = (
                        "Retrieve more information specifically about "
                        "the new leads discussed in the previous question. "
                        "Include the available new-lead count and any "
                        "individual lead details returned by the CRM. "
                        "If individual names or details are unavailable, "
                        "state that clearly. Do not replace this request "
                        "with a general sales summary. Do not invent information."
                    )

                elif any(
                    keyword in previous_user_lower for keyword in ["lead", "leads"]
                ):
                    base_request = (
                        "Retrieve more information specifically about "
                        "the leads discussed in the previous question. "
                        "Include the available total and new-lead counts "
                        "and any individual lead details returned by the CRM. "
                        "State clearly if individual details are unavailable. "
                        "Do not invent information."
                    )

                elif any(
                    keyword in previous_user_lower
                    for keyword in [
                        "follow-up",
                        "follow up",
                        "followups",
                    ]
                ):
                    base_request = (
                        "Retrieve more information specifically about "
                        "the pending sales follow-ups discussed previously. "
                        "Include the customers requiring follow-up and "
                        "how long each has been pending, when available. "
                        "Do not invent information."
                    )

                elif any(
                    keyword in previous_user_lower for keyword in ["order", "orders"]
                ):
                    base_request = (
                        "Retrieve more information specifically about "
                        "the orders discussed previously. Include available "
                        "order counts, statuses, customer names, and amounts. "
                        "Do not invent information."
                    )

                elif any(
                    keyword in previous_user_lower
                    for keyword in ["customer", "customers"]
                ):
                    base_request = (
                        "Retrieve more information specifically about "
                        "the customers discussed previously. Include "
                        "available customer names and status information. "
                        "Do not invent information."
                    )

            else:
                # An explicit topic in the current question takes priority.

                # Comparative questions about pending follow-ups
                if any(
                    phrase in current_question_lower
                    for phrase in [
                        "waiting the longest",
                        "waited the longest",
                        "longest waiting",
                        "longest-waiting",
                        "longest pending",
                        "most days pending",
                    ]
                ):
                    base_request = (
                        "Retrieve the current pending sales follow-up records "
                        "needed to answer the user's comparative question. "
                        "Include each available customer name and the exact "
                        "number of days their follow-up has been pending. "
                        "Compare the waiting durations and identify the "
                        "customer with the greatest number of pending days. "
                        "Use only durations present in the retrieved data. "
                        "If the durations are unavailable or cannot be "
                        "compared, clearly state that. Do not invent "
                        "customer names or waiting durations."
                    )

                # Ordinal order references such as "first one", "second one"
                elif any(
                    phrase in current_question_lower
                    for phrase in [
                        "first one",
                        "second one",
                        "third one",
                        "first order",
                        "second order",
                        "third order",
                    ]
                ):
                    base_request = (
                        "Resolve the user's ordinal reference using the order list "
                        "from the previous conversation. The user is referring to "
                        "an order by its position in the previously discussed order "
                        "list.\n\n"
                        "Use the same order ordering that was previously shown to "
                        "the user. For example, 'first one' means the first order "
                        "in that previous list and 'second one' means the second "
                        "order in that previous list.\n\n"
                        "Return the actual matching order record and use its available "
                        "order ID, customer, amount, and status to answer the current "
                        "question. If the requested position cannot be resolved, "
                        "clearly state that the order could not be identified. "
                        "Do not invent information."
                    )

                # Existing order condition
                elif any(
                    keyword in current_question_lower
                    for keyword in [
                        "pending order",
                        "pending orders",
                        "order",
                        "orders",
                    ]
                ):
                    base_request = (
                        "Retrieve the current order information needed "
                        "to answer the user's question. Include the "
                        "total number of orders and the number of "
                        "pending orders. If available, include relevant "
                        "order details and statuses. Focus specifically "
                        "on orders rather than returning the complete "
                        "sales summary. Do not invent information."
                    )

                elif any(
                    keyword in current_question_lower
                    for keyword in [
                        "new lead",
                        "new leads",
                        "lead",
                        "leads",
                    ]
                ):
                    base_request = (
                        "Retrieve the current sales lead information "
                        "needed to answer the user's question. Include "
                        "the total number of leads and new leads, along "
                        "with other available lead details when relevant. "
                        "Focus specifically on leads rather than returning "
                        "the complete sales summary. Do not invent information."
                    )

                elif any(
                    keyword in current_question_lower
                    for keyword in ["customer", "customers"]
                ):
                    base_request = (
                        "Retrieve the current customer information "
                        "needed to answer the user's question. Include "
                        "the available customer names and relevant "
                        "customer status information. Focus specifically "
                        "on customers rather than returning the complete "
                        "sales summary. Do not invent information."
                    )

                elif any(
                    keyword in current_question_lower
                    for keyword in [
                        "sales",
                        "sale",
                        "sales status",
                        "sales summary",
                        "sales overview",
                        "current sales",
                    ]
                ):
                    base_request = (
                        "Give the current sales summary discussed in "
                        "the conversation. Include total leads, new "
                        "leads, pending follow-ups, customers, orders, "
                        "and other available sales details."
                    )

        # -----------------------------------------------------
        # HR-specific contextual follow-up requests
        # -----------------------------------------------------
        if agent_name == "HR Agent":

            current_question_lower = request.lower()
            previous_user_lower = previous_user.lower()
            # -------------------------------------------------
            # Pending leave requests
            # -------------------------------------------------
            if any(
                phrase in previous_user_lower
                for phrase in [
                    "pending leave",
                    "pending leave request",
                    "pending leave requests",
                    "leave request",
                    "leave requests",
                ]
            ):
                base_request = (
                    "Retrieve information specifically about the leave requests "
                    "discussed in the previous conversation.\n\n"
                    "The previous topic was leave requests. Preserve that topic "
                    "for this follow-up and do not replace it with a general "
                    "employee-on-leave summary.\n\n"
                    "If pending leave-request records are available, return "
                    "their current status and relevant employee information. "
                    "If pending leave-request data is unavailable, clearly "
                    "state that the pending leave-request information is not "
                    "available.\n\n"
                    "Do not switch to attendance, employee salary, general "
                    "employee information, or current employees on leave "
                    "unless the user explicitly asks for them.\n"
                    "Do not invent information."
                )
            # -------------------------------------------------
            # Employee-specific leave/status
            # -------------------------------------------------
            elif entity_context and any(
                phrase in previous_user_lower
                for phrase in [
                    "leave",
                    "on leave",
                ]
            ):
                entity_name = entity_context[0]
                base_request = (
                    f"Retrieve the leave information specifically for "
                    f"the employee '{entity_name}'.\n\n"
                    f"The previous conversation was about '{entity_name}' "
                    "and their leave.\n\n"
                    "For the current follow-up, preserve this employee and "
                    "leave context. If the user asks for the status, provide "
                    "the available leave status for this employee.\n\n"
                    "Do not switch to the general employee list or unrelated "
                    "HR information.\n"
                    "Use only information available from the HR data.\n"
                    "Do not invent information."
                )
            # -------------------------------------------------
            # Attendance follow-up
            # -------------------------------------------------

            elif any(
                phrase in previous_user_lower
                for phrase in [
                    "attendance",
                    "absent",
                    "present",
                ]
            ):
                base_request = (
                    "Retrieve more detailed information about the attendance "
                    "topic discussed in the previous conversation.\n\n"
                    "Preserve the attendance context and provide the available "
                    "attendance information.\n"
                    "Do not switch to leave information or general employee "
                    "information unless explicitly requested.\n"
                    "Do not invent information."
                )
            # -------------------------------------------------
            # General employee information
            # -------------------------------------------------
            elif any(
                phrase in previous_user_lower
                for phrase in [
                    "employee",
                    "employees",
                    "staff",
                    "team member",
                    "team members",
                ]
            ):
                base_request = (
                    "Retrieve more detailed information about the employee "
                    "information discussed in the previous conversation.\n\n"
                    "Preserve the employee-information context and provide "
                    "available employee details.\n"
                    "Do not switch to unrelated HR topics.\n"
                    "Do not invent information."
                )

        # -----------------------------------------------------
        # Project task / item-specific requests
        # -----------------------------------------------------
        request_lower = request.lower()

        # -------------------------------------------------
        # Explicit employee-owned project request
        # -------------------------------------------------

        is_own_project_request = False

        if agent_name == "Project Agent":
            is_own_project_request = any(
                phrase in request_lower
                for phrase in [
                    "my projects",
                    "my project",
                    "projects assigned to me",
                    "projects assigned for me",
                    "projects assigned to",
                    "projects for me",
                    "projects i'm working on",
                    "projects i am working on",
                    "which projects am i working on",
                    "what projects am i working on",
                    "currently working on",
                    "currently assigned",
                ]
            )
        if is_own_project_request:
            # The current question explicitly asks for the
            # employee's own projects. Do not let an entity
            # from the previous task conversation override it.
            entity_context = []

            base_request = (
                "Retrieve only the projects currently assigned to "
                "the authenticated employee.\n\n"
                "The user is asking which projects they are currently "
                "working on. Return the employee's own assigned projects "
                "from the available project records.\n\n"
                "Include project names and their current status when "
                "available. If related tasks are available, include them "
                "only when they belong to the employee's assigned projects.\n\n"
                "Do not return general company-wide project information. "
                "Do not return unrelated delayed projects. "
                "Do not use projects from other employees. "
                "Do not invent project assignments."
            )
        elif any(
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
                        "Preserve the HR topic from the previous conversation "
                        "when answering this employee-specific follow-up. "
                        "If the previous topic was salary, provide the salary "
                        "for this employee. If the previous topic was attendance, "
                        "provide attendance information for this employee. "
                        "If the previous topic was leave, provide leave information "
                        "for this employee. If the previous topic was general "
                        "employee information, provide the relevant employee details.\n"
                        "Do not switch to an unrelated HR topic.\n"
                        "Use only available HR data.\n"
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

        selected_agents = self.get_agents_from_request(request)

        results = []

        # =====================================================
        # STRUCTURED AGENT-TO-AGENT COLLABORATION
        # =====================================================

        project_agent = None
        sales_agent = None

        for agent in selected_agents:

            if agent.name == "Project Agent":
                project_agent = agent

            elif agent.name == "Sales Agent":
                sales_agent = agent
        if project_agent and sales_agent:

            print("=" * 60)
            print("STRUCTURED COLLABORATION: PROJECT -> SALES")
            print("=" * 60)

            # First execute the primary Project Agent.
            project_result = self.execute_agent(
                agent=project_agent,
                agent_request=request,
                user=user,
                credentials=credentials,
            )
            # Project Agent requests relevant sales/customer
            # information from Sales Agent.
            collaboration_result = self.request_agent_collaboration(
                requesting_agent=project_agent,
                target_agent_name="Sales Agent",
                collaboration_request=(
                    "Provide the sales and customer information "
                    "needed to evaluate the possible business impact "
                    "of the projects mentioned in the user's request. "
                    "Include relevant customers, pending orders, "
                    "and pending follow-ups when available. "
                    "Do not invent relationships between projects "
                    "and customers or orders."
                ),
                user=user,
                credentials=credentials,
            )
            # Keep the collaboration attached to the Project Agent
            # result for structured agent-to-agent tracking.
            project_result["collaboration"] = collaboration_result

            results.append(project_result)
            # Also expose the Sales collaboration as a separate
            # result so the final natural-response layer can use it.
            if collaboration_result.get("status") == "success":
                results.append(
                    {
                        "agent": "Sales Agent",
                        "status": "success",
                        "message": collaboration_result.get(
                            "message",
                            "Sales information retrieved through Project Agent collaboration.",
                        ),
                        "data": collaboration_result.get(
                            "data",
                            {},
                        ),
                    }
                )

            # Execute the other selected agents normally.
            # Project Agent has already been executed above.
            # Sales Agent contributed through structured collaboration.
            for agent in selected_agents:
                if agent.name in ["Project Agent", "Sales Agent"]:
                    continue
                result = self.execute_agent(
                    agent=agent,
                    agent_request=request,
                    user=user,
                    credentials=credentials,
                )
                results.append(result)
        else:

            # Existing behavior for all other multi-agent requests.
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

        previous_user = self.get_previous_user_message(
            conversation_history,
            current_request=request,
        )

        print(
            "PREVIOUS USER MESSAGE:",
            previous_user,
        )

        print(
            "PREVIOUS ASSISTANT MESSAGE:",
            previous_assistant,
        )

        # -----------------------------------------------------
        # Ambiguous "those/these" pending reference
        # -----------------------------------------------------
        if self.is_ambiguous_pending_reference(
            request=request,
            conversation_history=conversation_history,
        ):
            return {
                "status": "success",
                "intent": "contextual_follow_up",
                "agent": "Conversation Context",
                "response": (
                    "Do you mean the 3 pending sales follow-ups "
                    "or the 2 pending orders?"
                ),
                "data": {
                    "conversation_context_used": True,
                    "clarification_required": True,
                },
            }

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
        # 3. Follow-up routing priority
        # -----------------------------------------------------
        # Priority:
        #
        # 1. Explicit agent/topic in CURRENT request
        # 2. Entity context when current request is ambiguous
        # 3. Previous conversation context
        #
        # Example:
        #
        # "Tell me about Vetri E-Commerce."
        # "What about sales?"
        #
        # Current request = Sales
        # Previous entity = Vetri E-Commerce
        #
        # Sales must win because the current request explicitly
        # identifies the Sales area.
        # -----------------------------------------------------
        entity_agents = self.get_agents_from_entities(entity_context)

        print(
            "ENTITY-BASED AGENTS:",
            [agent.name for agent in entity_agents],
        )

        # -----------------------------------------------------
        # Current request wins
        # -----------------------------------------------------
        if current_agents:
            print(
                "FOLLOW-UP ROUTING PRIORITY: CURRENT REQUEST",
            )

            print(
                "SELECTED FOLLOW-UP AGENTS:",
                [agent.name for agent in current_agents],
            )

        # -----------------------------------------------------
        # If current request is ambiguous, use entity context
        # -----------------------------------------------------
        elif entity_agents:
            current_agents = entity_agents
            print("FOLLOW-UP ROUTING PRIORITY: ENTITY CONTEXT")
            print(
                "ENTITY-BASED AGENTS:",
                [agent.name for agent in current_agents],
            )
        # -----------------------------------------------------
        # Otherwise use previous conversation context
        # -----------------------------------------------------
        else:

            current_agents = self.get_agents_from_conversation(
                conversation_history,
                current_request=request,
            )
            print("FOLLOW-UP ROUTING PRIORITY: CONVERSATION CONTEXT")

            print(
                "CONVERSATION AGENTS:",
                [agent.name for agent in current_agents],
            )

        # -----------------------------------------------------
        # 4. Attention question detection
        # -----------------------------------------------------

        attention_keywords = [
            "which area",
            "which one",
            "needs attention",
            "what needs my attention",
            "what needs my attention first",
            "what needs attention first",
            "what needs attention most",
            "most attention",
            "what should i focus",
            "what should we focus",
            "what should i do",
            "what should we do",
            "what should i attend to first",
            "what should i prioritize",
            "what should i prioritize first",
            "what is most urgent",
            "what is urgent",
            "which needs attention",
            "which needs attention first",
            "what needs to be handled first",
            "what should be handled first",
            "what next",
            "priorities",
            "priority",
        ]

        request_lower = request.lower()

        is_attention_question = any(
            keyword in request_lower for keyword in attention_keywords
        )

        # -----------------------------------------------------
        # 5. Attention question handling
        # -----------------------------------------------------
        #
        # Preserve the existing conversation context.
        # Only use multiple management agents when there is
        # no specific business context.
        #
        # Example:
        # How many new leads are there?
        # Tell me more about them.
        # Which one needs attention?
        #
        # This must remain in the Sales context.
        # -----------------------------------------------------

        if is_attention_question:

            if current_agents:

                print("ATTENTION ROUTING: PRESERVING EXISTING CONTEXT")

                print(
                    "ATTENTION CONTEXT AGENTS:",
                    [agent.name for agent in current_agents],
                )

            else:

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

                    print("ATTENTION ROUTING: MANAGEMENT OVERVIEW")

                    print(
                        "MANAGEMENT ATTENTION AGENTS:",
                        [agent.name for agent in current_agents],
                    )

        # -----------------------------------------------------
        # 6. No agent found
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
        # 7. Execute contextual agents
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

            # Handle a reply to the previous clarification question.
            if self.is_clarification_reply(
                request,
                conversation_history,
            ):
                request_lower = request.lower()
                if "order" in request_lower:
                    agent_request = (
                        "The user clarified that they are asking about "
                        "orders from the previous sales summary. "
                        "Retrieve the actual order records and identify "
                        "which orders are pending. Include the order ID, "
                        "customer, amount, and status where available. "
                        "Use the available business data and do not "
                        "invent missing details."
                    )
                elif (
                    "follow-up" in request_lower
                    or "follow up" in request_lower
                    or "followup" in request_lower
                ):
                    agent_request = (
                        "The user clarified that they are asking about "
                        "pending sales follow-ups from the previous "
                        "sales summary. Retrieve the actual pending "
                        "follow-up records and include the customer "
                        "and pending duration where available. "
                        "Do not invent missing details."
                    )

            # Handle a short confirmation such as "yes"
            if self.is_confirmation_reply(request) and self.assistant_offered_details(
                conversation_history
            ):
                agent_request += (
                    "\n\nThe user has confirmed the previous "
                    "assistant's offer to provide more details.\n\n"
                    f"Previous user request: {previous_user}\n\n"
                    f"Previous assistant offer: "
                    f"{previous_assistant}\n\n"
                    "Retrieve the actual detailed business "
                    "information needed to fulfill the previous "
                    "user request. Focus on the same business "
                    "topic and return the available records, "
                    "names, statuses, counts, and other relevant "
                    "details. Do not return only a general summary. "
                    "Do not invent missing information."
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

            print(
                "EXECUTE AGENT RESULT:",
                result,
            )

            results.append(result)

        # -----------------------------------------------------
        # 8. Handle permission-denied results
        # -----------------------------------------------------

        permission_denied_results = [
            result
            for result in results
            if isinstance(result, dict)
            and (
                result.get("status") == "denied"
                or result.get("status") == "permission_denied"
                or result.get("permission_denied") is True
            )
        ]

        if permission_denied_results:

            denied_result = permission_denied_results[0]

            response_message = denied_result.get(
                "message",
                "You do not have permission to access the requested information.",
            )

            print(
                "PERMISSION DENIED:",
                denied_result,
            )

        else:

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
            # 10. Natural conversational response
            # -----------------------------------------------------
            #
            # The follow-up has already been routed to the
            # correct agent(s). The verified results are now
            # passed through the same natural-language layer
            # used by normal and multi-agent requests.
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

        # Handle short rejection replies without calling an agent.
        if (
            conversation_history
            and self.is_rejection_reply(request)
            and self.assistant_offered_details(conversation_history)
        ):
            return {
                "status": "success",
                "intent": "conversation",
                "agent": "Vetri AI",
                "response": (
                    "No problem. Let me know if you would "
                    "like to explore those details later."
                ),
                "data": {
                    "conversation_context_used": True,
                },
            }

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

        # =====================================================
        # CHECK FOR A REAL PREVIOUS CONVERSATION TURN
        # =====================================================
        has_previous_conversation = any(
            message.get("content", "").strip() != request.strip()
            for message in conversation_history
        )

        print(
            "HAS PREVIOUS CONVERSATION:",
            has_previous_conversation,
        )
        follow_up_detected = False

        if has_previous_conversation:
            follow_up_detected = self.is_follow_up_question(
                request,
                conversation_history,
            )
        print(
            "FOLLOW-UP DETECTED:",
            follow_up_detected,
        )

        print("=" * 60)

        # =====================================================
        # 1. CONTEXTUAL FOLLOW-UP
        # =====================================================

        if has_previous_conversation:
            is_follow_up = self.is_follow_up_question(
                request,
                conversation_history,
            )
            is_confirmation = self.is_confirmation_reply(
                request
            ) and self.assistant_offered_details(conversation_history)
            is_clarification = self.is_clarification_reply(
                request,
                conversation_history,
            )
            if is_follow_up or is_confirmation or is_clarification:
                print("ROUTING: CONTEXTUAL FOLLOW-UP")

                if is_clarification:
                    print("CLARIFICATION REPLY DETECTED:", request)

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

        permission_engine = PermissionEngine()

        # =====================================================
        # ADMIN-ONLY AUDIT LOG REQUEST
        # =====================================================

        if any(
            keyword in request.lower()
            for keyword in [
                "audit log",
                "audit logs",
                "auditlog",
                "auditlogs",
                "audit information",
                "audit across users",
                "audit information across users",
            ]
        ):

            if not permission_engine.has_permission(
                role,
                "view_audit_logs",
            ):
                return {
                    "status": "error",
                    "intent": "Audit Logs",
                    "agent": "Audit Logs",
                    "response": "You do not have permission to view audit logs.",
                }
            # -------------------------------------------------
            # Retrieve existing audit records
            # -------------------------------------------------
            audit_logs = AuditLog.objects.all().order_by("-timestamp")

            audit_data = []
            for log in audit_logs:

                audit_data.append(
                    {
                        "id": log.id,
                        "user": log.user,
                        "agent": log.agent,
                        "request": log.request,
                        "data_accessed": log.data_accessed,
                        "tool": log.tool,
                        "action": log.action,
                        "approval": log.approval,
                        "result": log.result,
                        "timestamp": log.timestamp.isoformat(),
                    }
                )
            # -------------------------------------------------
            # Fallback response
            # -------------------------------------------------
            fallback_response = (
                f"I found {len(audit_data)} audit log records."
                if audit_data
                else "There are currently no audit log records."
            )
            # -------------------------------------------------
            # Natural response
            # -------------------------------------------------
            natural_response = self.generate_natural_response(
                request=request,
                results=[
                    {
                        "status": "success",
                        "agent": "Audit Logs",
                        "message": fallback_response,
                        "data": {
                            "total_logs": len(audit_data),
                            "audit_logs": audit_data,
                        },
                    }
                ],
                conversation_history=conversation_history,
                fallback_response=fallback_response,
            )
            # -------------------------------------------------
            # Record that the audit logs were accessed
            # -------------------------------------------------

            try:

                create_audit_log(
                    user=user,
                    action="audit_logs_viewed",
                    details={
                        "request": request,
                        "records_returned": len(audit_data),
                    },
                )

            except Exception:
                pass

            return {
                "status": "success",
                "intent": "Audit Logs",
                "agent": "Audit Logs",
                "response": natural_response,
                "data": {
                    "total_logs": len(audit_data),
                    "audit_logs": audit_data,
                },
            }
        # =====================================================
        # ADMIN-ONLY SENSITIVE INFORMATION REQUEST
        # =====================================================

        if any(
            keyword in request.lower()
            for keyword in [
                "sensitive admin information",
                "sensitive information",
                "admin information",
                "protected admin information",
            ]
        ):

            if not permission_engine.has_permission(
                role,
                "view_audit_logs",
            ):
                return {
                    "status": "error",
                    "intent": "Sensitive Admin Information",
                    "agent": "Admin Security",
                    "response": "You do not have permission to access sensitive admin information.",
                }

            fallback_response = (
                "As an administrator, you are authorized to access protected "
                "business information including audit logs, employee information, "
                "employee salary information, finance, sales, project, HR, "
                "GitHub, Cloud Storage, and other configured business data."
            )

            natural_response = self.generate_natural_response(
                request=request,
                results=[
                    {
                        "status": "success",
                        "agent": "Admin Security",
                        "message": fallback_response,
                        "data": {
                            "role": role,
                            "authorized": True,
                            "protected_permissions": [
                                "view_audit_logs",
                                "view_employees",
                                "view_employee_salary",
                                "view_finance",
                                "view_sales",
                                "view_projects",
                                "view_github",
                                "view_cloud_storage",
                            ],
                        },
                    }
                ],
                conversation_history=conversation_history,
                fallback_response=fallback_response,
            )

            return {
                "status": "success",
                "intent": "Sensitive Admin Information",
                "agent": "Admin Security",
                "response": natural_response,
                "data": {
                    "role": role,
                    "authorized": True,
                },
            }

        # =====================================================
        # 3. AGENT SELECTION
        # =====================================================
        #
        # Priority:
        #
        # 1. Explicit agent/topic in CURRENT user request
        # 2. Explicit entity in CURRENT user request
        # 3. Previous conversation/entity context only when
        #    the current request is ambiguous
        #
        # This prevents a previous project such as
        # "Vetri E-Commerce" from overriding a new request
        # such as "Show me the sales information."
        # -----------------------------------------------------
        # 3A. Detect agents directly from CURRENT request
        # -----------------------------------------------------

        current_request_agents = self.get_agents_from_request(request)
        print(
            "CURRENT REQUEST AGENTS:",
            [agent.name for agent in current_request_agents],
        )

        # -----------------------------------------------------
        # 3B. Detect entities from current/conversation context
        # -----------------------------------------------------

        entity_context = self.get_entity_context_from_conversation(
            request=request,
            conversation_history=conversation_history,
        )

        print(
            "ENTITY CONTEXT:",
            entity_context,
        )

        entity_agents = self.get_agents_from_entities(entity_context)

        # -----------------------------------------------------
        # 3C. Current request always wins when it explicitly
        # identifies a business area.
        # -----------------------------------------------------

        if current_request_agents:

            selected_agents = current_request_agents

            print(
                "ROUTING PRIORITY: CURRENT REQUEST",
            )

            print(
                "CURRENT REQUEST AGENTS:",
                [agent.name for agent in selected_agents],
            )

        # -----------------------------------------------------
        # 3D. If current request has no direct agent keyword,
        # use entity-based routing.
        #
        # Example:
        # "What about AI Dashboard?"
        # -> Project Agent
        # -----------------------------------------------------

        elif entity_agents:

            selected_agents = entity_agents

            print(
                "ROUTING PRIORITY: ENTITY CONTEXT",
            )

            print(
                "ENTITY-BASED AGENTS:",
                [agent.name for agent in selected_agents],
            )

        # -----------------------------------------------------
        # 3E. Final fallback to registry relevance detection.
        # -----------------------------------------------------

        else:

            selected_agents = self.get_agents_from_request(request)

            print(
                "ROUTING PRIORITY: REGISTRY RELEVANCE",
            )

        print(
            "RELEVANT AGENTS:",
            [agent.name for agent in selected_agents],
        )

        # =====================================================
        # 4. SINGLE / MULTI-AGENT QUERY
        # =====================================================

        if len(selected_agents) > 1:
            print("ROUTING: MULTI-AGENT QUERY")
            print(
                "SELECTED MULTI-AGENTS:",
                [agent.name for agent in selected_agents],
            )
            return self.process_multi_agent_query(
                request=request,
                user=user,
                role=role,
                credentials=credentials,
                conversation_history=conversation_history,
            )

        elif len(selected_agents) == 1:

            agent = selected_agents[0]

            intent_result = {
                "intent": agent.name,
                "agent": agent,
            }

        else:

            agent = None

            intent_result = {
                "intent": "unknown",
                "agent": None,
            }

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
            agent=agent,
            agent_request=request,
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
