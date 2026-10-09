import re
from .base_agent import BaseAgent
from tools.crm_tool import CRMTool
from knowledge_base.rag import RAGSystem


class SalesAgent(BaseAgent):
    name = "Sales Agent"
    description = "Handles sales, leads, follow-ups and orders"

    def __init__(self):
        self.crm_tool = CRMTool()
        self.rag = RAGSystem()

    # ============================================================
    # CRM HELPERS
    # ============================================================

    def _crm_execute(self, action, user):
        """Execute an action through the existing CRMTool interface."""
        try:
            return self.crm_tool.execute(action, user)
        except Exception as exc:
            print(f"Sales Agent CRM ERROR [{action}]: {exc}")
            return None

    def _extract_data(self, result):
        """Safely return the CRM data object."""
        if not isinstance(result, dict) or result.get("status") != "success":
            return {}

        data = result.get("data", {})
        return data if isinstance(data, dict) else {}

    def _extract_list_from_result(self, result, key):
        """Extract a list from a normalized CRM response."""
        if not isinstance(result, dict) or result.get("status") != "success":
            return []

        data = result.get("data", {})

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            value = data.get(key, [])
            return value if isinstance(value, list) else []

        return []

    def _extract_current_question(self, request):
        """Extract the actual user question from a contextual request."""
        request = str(request or "")
        marker = "current user question:"

        if marker in request.lower():
            position = request.lower().rfind(marker)
            return request[position + len(marker) :].strip().lower()

        return request.strip().lower()

    def _safe_days_pending(self, followup):
        """Safely convert days_pending into an integer."""
        if not isinstance(followup, dict):
            return 0

        try:
            return int(followup.get("days_pending", 0))
        except (TypeError, ValueError):
            return 0

    # ============================================================
    # TOPIC AND CONTEXT HELPERS
    # ============================================================

    def _get_contextual_topic(self, request_lower, current_question):
        """
        Identify the topic of a contextual request.

        Explicit topic references are checked before broad wording.
        Generic references to lead details in an instruction should
        not automatically override a clearly stated follow-up topic.
        """
        request_lower = str(request_lower or "").lower()
        current_question = str(current_question or "").lower()

        # Explicit, specific topic labels first.
        explicit_topic_patterns = [
            (r"previous\s+(?:sales\s+)?topic\s*:\s*(?:new\s+)?leads?\b", "leads"),
            (r"previous\s+(?:sales\s+)?topic\s*:\s*follow[\s-]?ups?\b", "followups"),
            (r"previous\s+(?:sales\s+)?topic\s*:\s*orders?\b", "orders"),
            (r"previous\s+(?:sales\s+)?topic\s*:\s*customers?\b", "customers"),
        ]

        for pattern, topic in explicit_topic_patterns:
            if re.search(pattern, request_lower):
                return topic

        # A named customer in the contextual request must be
        # preserved when the current question is a vague follow-up.
        known_entities = [
            "abc technologies",
            "xyz solutions",
            "global systems",
        ]
        if any(entity in request_lower for entity in known_entities):
            if not any(
                term in current_question
                for term in [
                    "follow-up",
                    "follow up",
                    "followups",
                    "follow-ups",
                    "lead",
                    "leads",
                    "order",
                    "orders",
                ]
            ):
                return "customers"

        # Specific previous-topic wording is more reliable than generic
        # instructions that mention several sales data types.
        previous_topic_phrases = [
            (
                [
                    "previous conversation was about pending follow-ups",
                    "previous conversation was about follow-ups",
                    "previous question was about follow-ups",
                    "previous topic was follow-ups",
                    "focus on the same follow-up topic",
                    "focus only on pending follow-ups",
                    "focus specifically on pending follow-ups",
                    "previous user question was about follow-ups",
                    "previous user question about follow-ups",
                ],
                "followups",
            ),
            (
                [
                    "previous conversation was about new leads",
                    "previous conversation was about leads",
                    "previous conversation was specifically about new leads",
                    "previous conversation was specifically about leads",
                    "previous question was about new leads",
                    "previous question was about leads",
                    "previous topic was leads",
                    "focus only on new leads",
                    "focus only on those new leads",
                    "focus specifically on new leads",
                    "focus specifically on those new leads",
                    "previous user question was about leads",
                    "previous user question about leads",
                ],
                "leads",
            ),
            (
                [
                    "previous conversation was about orders",
                    "previous question was about orders",
                    "previous topic was orders",
                    "focus only on orders",
                    "previous user question was about orders",
                ],
                "orders",
            ),
            (
                [
                    "previous conversation was about customers",
                    "previous question was about customers",
                    "previous topic was customers",
                    "focus only on customers",
                    "previous user question was about customers",
                ],
                "customers",
            ),
        ]

        for phrases, topic in previous_topic_phrases:
            if any(phrase in request_lower for phrase in phrases):
                return topic

        # Broad sales status is a fallback, after specific topic instructions.
        if re.search(
            r"previous\s+(?:sales\s+)?topic\s*:\s*(?:sales\s+)?(?:status|summary|overview)\b",
            request_lower,
        ):
            return "sales_status"

        # Current question explicitly names its topic.
        if any(
            term in current_question
            for term in [
                "follow-up",
                "follow up",
                "followups",
                "follow-ups",
            ]
        ):
            return "followups"

        if any(
            term in current_question
            for term in [
                "new lead",
                "new leads",
                "lead details",
                "lead information",
                "about the leads",
                "about leads",
                "which leads",
                "these leads",
                "those leads",
            ]
        ) or re.search(r"\bleads?\b", current_question):
            return "leads"

        if "order" in current_question or "ord-" in current_question:
            return "orders"

        if "customer" in current_question:
            return "customers"

        if any(
            term in current_question
            for term in [
                "sales summary",
                "sales overview",
                "sales status",
                "sales information",
                "current sales",
            ]
        ):
            return "sales_status"

        # Contextual request instructions can identify a topic even when
        # the user's follow-up itself is vague.
        if any(
            term in request_lower
            for term in [
                "pending sales follow-up",
                "pending follow-up",
                "pending follow up",
                "customers requiring follow-up",
                "customers requiring follow up",
                "pending followups",
                "follow-up records",
                "follow up records",
                "follow-up information",
                "follow-up details",
            ]
        ):
            return "followups"

        if any(
            term in request_lower
            for term in [
                "orders discussed previously",
                "order discussed previously",
                "pending orders",
                "order details",
                "order information",
                "about orders",
                "about order",
                "order list",
                "order record",
            ]
        ):
            return "orders"

        if any(
            term in request_lower
            for term in [
                "customers discussed previously",
                "customer details",
                "customer information",
                "about customers",
                "customer record",
            ]
        ):
            return "customers"

        # Avoid generic terms such as "individual lead details" here:
        # a generic attention instruction may mention them even when the
        # user's actual previous topic was follow-ups.
        if any(
            term in request_lower
            for term in [
                "leads discussed previously",
                "leads discussed in the previous",
                "information specifically about the leads",
                "more information specifically about the leads",
                "new-lead counts",
                "new lead counts",
                "previous question about leads",
                "previous lead",
                "previous leads",
                "leads discussed",
            ]
        ):
            return "leads"

        if any(
            term in request_lower
            for term in [
                "current sales status",
                "sales status",
                "current sales summary",
                "sales summary",
                "current sales overview",
                "sales overview",
                "current sales information",
                "sales information",
            ]
        ):
            return "sales_status"

        return None

    def _is_contextual_request(self, request_lower):
        """Check whether the orchestrator supplied conversation context."""
        return any(
            marker in request_lower
            for marker in [
                "contextual agent request:",
                "previous conversation context:",
                "specific entity context:",
                "specific sales entity context:",
            ]
        )

    def _is_attention_question(self, question):
        """Detect questions asking what needs attention or prioritization."""
        phrases = [
            "which one needs attention",
            "which ones need attention",
            "who needs attention",
            "needs attention",
            "need attention",
            "which lead needs attention",
            "which leads need attention",
            "which one should i prioritize",
            "which should i prioritize",
            "which lead should i prioritize",
            "which leads should i prioritize",
            "which one is priority",
            "which lead is priority",
            "priority lead",
            "what should i focus on",
            "what do i need to focus on",
            "which lead is most urgent",
            "which leads are most urgent",
            "which one is most urgent",
            "who should i follow up with first",
            "which lead should i follow up with first",
            "which customer should i follow up with first",
            "who should i contact first",
            "which one should i handle first",
            "what needs my attention first",
            "what is most important",
            "what should i handle first",
            "what should i prioritize",
            "what needs prioritizing",
        ]
        return any(phrase in question for phrase in phrases)

    def _is_explicit_lead_attention(self, question):
        """Detect attention questions that clearly refer to leads."""
        return "lead" in question and self._is_attention_question(question)

    def _is_explicit_followup_attention(self, question):
        """Detect attention questions that clearly refer to follow-ups."""
        has_followup_term = any(
            term in question
            for term in [
                "follow-up",
                "follow up",
                "followups",
                "follow-ups",
            ]
        )
        return has_followup_term and self._is_attention_question(question)

    def _is_more_request(self, question):
        """Detect requests for more details about the current topic."""
        phrases = [
            "tell me more",
            "more details",
            "more information",
            "explain more",
            "describe them",
            "who are they",
            "which ones",
            "show me more",
            "give me details",
        ]
        return self._get_ordinal(question) is not None or any(
            phrase in question for phrase in phrases
        )

    # ============================================================
    # FOLLOW-UP HELPERS
    # ============================================================

    def _get_pending_followups(self, user):
        """Retrieve pending follow-ups from CRM."""
        result = self._crm_execute("get_pending_followups", user)
        return self._extract_list_from_result(result, "pending_followups")

    def _is_longest_followup_request(self, question):
        """Detect comparative follow-up questions."""
        phrases = [
            "waiting the longest",
            "waited the longest",
            "longest waiting",
            "longest-waiting",
            "longest pending",
            "most days pending",
            "who has been waiting longest",
            "who is waiting longest",
            "which customer has waited longest",
            "which customer is waiting longest",
            "who waited the longest",
            "most overdue",
            "longest outstanding follow-up",
            "oldest follow-up",
        ]
        return any(phrase in question for phrase in phrases)

    def _get_longest_followup_response(self, user):
        """
        Find the longest-waiting follow-up using CRM durations only.
        CRM retrieval failures are not reported as an empty list.
        """
        result = self._crm_execute("get_pending_followups", user)

        if not isinstance(result, dict) or result.get("status") != "success":
            return {
                "agent": self.name,
                "status": "error",
                "data": {},
                "message": "I could not retrieve the pending follow-up information.",
            }

        followups = self._extract_list_from_result(
            result,
            "pending_followups",
        )

        if not followups:
            return {
                "agent": self.name,
                "status": "success",
                "data": {"pending_followups": []},
                "message": "There are currently no pending sales follow-ups.",
            }

        valid_followups = []
        for followup in followups:
            if not isinstance(followup, dict):
                continue

            days = self._safe_days_pending(followup)
            if days >= 0:
                valid_followups.append(
                    {
                        "customer": followup.get("customer", "Unknown customer"),
                        "days_pending": days,
                    }
                )

        if not valid_followups:
            return {
                "agent": self.name,
                "status": "success",
                "data": {"pending_followups": followups},
                "message": (
                    "The pending follow-ups were retrieved, but their "
                    "waiting durations could not be compared."
                ),
            }

        max_days = max(item["days_pending"] for item in valid_followups)
        longest = [item for item in valid_followups if item["days_pending"] == max_days]

        if len(longest) == 1:
            item = longest[0]
            message = (
                f"{item['customer']} has the longest pending follow-up, "
                f"at {max_days} days. Based on waiting time, this is "
                f"the follow-up to review first."
            )
        else:
            customers = ", ".join(item["customer"] for item in longest)
            message = (
                f"{customers} are tied for the longest pending follow-up "
                f"at {max_days} days. They can be reviewed first based "
                f"on waiting time."
            )

        return {
            "agent": self.name,
            "status": "success",
            "data": {
                "longest_followups": longest,
                "pending_followups": valid_followups,
            },
            "message": message,
        }

    def _get_followups_response(self, user):
        """Return pending follow-ups with their waiting durations."""
        result = self._crm_execute("get_pending_followups", user)

        if not isinstance(result, dict) or result.get("status") != "success":
            return {
                "agent": self.name,
                "status": "error",
                "data": {},
                "message": "I could not retrieve the pending follow-up information.",
            }

        followups = self._extract_list_from_result(
            result,
            "pending_followups",
        )

        lines = []
        for followup in followups:
            if not isinstance(followup, dict):
                continue

            customer = followup.get("customer", "Unknown customer")
            days = followup.get("days_pending", "unknown")
            lines.append(f"{customer} – pending for {days} days")

        message = (
            "The pending sales follow-ups are:\n" + "\n".join(lines)
            if lines
            else "There are currently no pending sales follow-ups."
        )

        return {
            "agent": self.name,
            "status": "success",
            "data": {"pending_followups": followups},
            "message": message,
        }

    # ============================================================
    # ENTITY HELPERS
    # ============================================================

    def _get_requested_entity(self, question):
        """Detect known customer or business names in a question."""
        question_lower = str(question or "").lower()
        entities = [
            "abc technologies",
            "xyz solutions",
            "global systems",
        ]

        for entity in entities:
            if entity in question_lower:
                return entity

        return None

    def _find_entity_in_records(self, records, entity):
        """Find CRM records containing a requested entity name."""
        if not entity or not isinstance(records, list):
            return []

        matches = []
        for record in records:
            if not isinstance(record, dict):
                continue

            searchable_text = " ".join(str(value).lower() for value in record.values())
            if entity in searchable_text:
                matches.append(record)

        return matches

    # ============================================================
    # ORDER HELPERS
    # ============================================================

    def _get_requested_order_id(self, question):
        """Extract an order ID such as ORD-1003."""
        match = re.search(r"\bord-\d+\b", question, re.IGNORECASE)
        return match.group(0).upper() if match else None

    def _get_ordinal(self, question):
        """Extract ordinal references such as first one or 2nd order."""
        ordinal_map = {
            "first one": 1,
            "second one": 2,
            "third one": 3,
            "fourth one": 4,
            "first order": 1,
            "second order": 2,
            "third order": 3,
            "fourth order": 4,
            "1st one": 1,
            "2nd one": 2,
            "3rd one": 3,
            "4th one": 4,
            "1st order": 1,
            "2nd order": 2,
            "3rd order": 3,
            "4th order": 4,
        }

        for phrase, number in ordinal_map.items():
            if phrase in question:
                return number

        return None

    def _format_order_message(self, order, prefix="Order"):
        """Create a consistent order response."""
        return (
            f"{prefix} {order.get('order_id', 'Unknown order')} for "
            f"{order.get('customer', 'Unknown customer')}. "
            f"The amount is ₹{order.get('amount', 0)} and the status is "
            f"{order.get('status', 'Unknown status')}."
        )

    def _get_orders_response(self, user, question, request_lower):
        """Retrieve orders and resolve exact IDs or ordinal references."""
        requested_order_id = self._get_requested_order_id(question)
        pending_scope = (
            "pending order" in question
            or "pending orders" in question
            or "pending order" in request_lower
            or "pending orders" in request_lower
        )

        action = "get_pending_orders" if pending_scope else "get_orders"
        result = self._crm_execute(action, user)

        if not isinstance(result, dict) or result.get("status") != "success":
            return {
                "agent": self.name,
                "status": "error",
                "data": {},
                "message": "I could not retrieve the order information at the moment.",
            }

        orders = self._extract_list_from_result(result, "orders")
        scope = "pending" if pending_scope else "all"

        if requested_order_id:
            for order in orders:
                if not isinstance(order, dict):
                    continue

                order_id = str(order.get("order_id", "")).upper()
                if order_id == requested_order_id:
                    return {
                        "agent": self.name,
                        "status": "success",
                        "data": {"order": order, "order_scope": scope},
                        "message": self._format_order_message(
                            order,
                            f"Order {requested_order_id}:",
                        ),
                    }

            return {
                "agent": self.name,
                "status": "success",
                "data": {
                    "orders": orders,
                    "requested_order_id": requested_order_id,
                    "order_scope": scope,
                },
                "message": (
                    f"I could not find {requested_order_id} in the "
                    f"{scope} orders returned by the CRM."
                ),
            }

        ordinal = self._get_ordinal(question)
        if ordinal is not None:
            index = ordinal - 1

            if 0 <= index < len(orders):
                order = orders[index]
                if isinstance(order, dict):
                    return {
                        "agent": self.name,
                        "status": "success",
                        "data": {
                            "order": order,
                            "ordinal": ordinal,
                            "order_scope": scope,
                        },
                        "message": (
                            f"The order at position {ordinal} is "
                            f"{order.get('order_id', 'Unknown order')} for "
                            f"{order.get('customer', 'Unknown customer')}. "
                            f"The amount is ₹{order.get('amount', 0)} "
                            f"and the status is {order.get('status', 'Unknown status')}."
                        ),
                    }

            return {
                "agent": self.name,
                "status": "success",
                "data": {"orders": orders, "order_scope": scope},
                "message": (
                    f"There is no order at position {ordinal} in the "
                    f"{scope} orders returned by the CRM."
                ),
            }

        return {
            "agent": self.name,
            "status": "success",
            "data": {"orders": orders, "order_scope": scope},
            "message": (
                f"There are {len(orders)} "
                f"{'pending ' if pending_scope else ''}orders available."
            ),
        }

    # ============================================================
    # LEAD AND CUSTOMER HELPERS
    # ============================================================

    def _get_leads_response(self, user, requested_entity=None):
        """Retrieve lead counts and any individual records provided by CRM."""
        result = self._crm_execute("get_leads", user)

        if not isinstance(result, dict) or result.get("status") != "success":
            return {
                "agent": self.name,
                "status": "error",
                "data": {},
                "message": "I could not retrieve the lead information at the moment.",
            }

        data = self._extract_data(result)
        total = data.get("total_leads", data.get("total", 0))
        new = data.get("new_leads", data.get("new", 0))
        leads = data.get("leads", [])
        if not isinstance(leads, list):
            leads = []

        if requested_entity and leads:
            matches = self._find_entity_in_records(leads, requested_entity)
            if matches:
                first = matches[0]
                name = first.get("name", requested_entity.title())
                return {
                    "agent": self.name,
                    "status": "success",
                    "data": {
                        "total_leads": total,
                        "new_leads": new,
                        "leads": matches,
                        "requested_entity": requested_entity,
                    },
                    "message": f"Here are the available lead details for {name}.",
                }

        # If no individual lead list is provided, a matching follow-up
        # may still give relevant customer follow-up information. It is
        # kept clearly separate from individual lead records.
        if requested_entity and not leads:
            followup_result = self._crm_execute("get_pending_followups", user)
            followups = self._extract_list_from_result(
                followup_result,
                "pending_followups",
            )
            matches = self._find_entity_in_records(followups, requested_entity)

            if matches:
                followup = matches[0]
                days = self._safe_days_pending(followup)
                return {
                    "agent": self.name,
                    "status": "success",
                    "data": {
                        "total_leads": total,
                        "new_leads": new,
                        "leads": [],
                        "requested_entity": requested_entity,
                        "followup": followup,
                    },
                    "message": (
                        f"{requested_entity.title()} appears in the current "
                        f"sales follow-up data and has been waiting {days} "
                        f"days for a follow-up. Individual lead details are "
                        f"not currently available from the CRM."
                    ),
                }

        if leads:
            return {
                "agent": self.name,
                "status": "success",
                "data": {
                    "total_leads": total,
                    "new_leads": new,
                    "leads": leads,
                },
                "message": (
                    f"There are {total} sales leads in total, including "
                    f"{new} new leads. Here are the individual lead records "
                    f"available from the CRM."
                ),
            }

        return {
            "agent": self.name,
            "status": "success",
            "data": {
                "total_leads": total,
                "new_leads": new,
                "leads": [],
            },
            "message": (
                f"There are {total} sales leads in total, including {new} "
                f"new leads. Individual lead details are not currently "
                f"available from the CRM."
            ),
        }

    def _get_lead_attention_response(self, user):
        """Answer lead-attention questions without inventing priority."""
        result = self._crm_execute("get_leads", user)

        if not isinstance(result, dict) or result.get("status") != "success":
            return {
                "agent": self.name,
                "status": "error",
                "data": {},
                "message": "I could not retrieve the lead information at the moment.",
            }

        data = self._extract_data(result)
        total = data.get("total_leads", data.get("total", 0))
        new = data.get("new_leads", data.get("new", 0))
        leads = data.get("leads", [])
        if not isinstance(leads, list):
            leads = []

        if leads:
            return {
                "agent": self.name,
                "status": "success",
                "data": {
                    "total_leads": total,
                    "new_leads": new,
                    "leads": leads,
                    "priority_available": False,
                },
                "message": (
                    "I retrieved individual lead records, but the available "
                    "CRM data does not define a priority or attention score. "
                    "You can review the listed lead status, follow-up date, "
                    "or other available criteria to decide which to handle first."
                ),
            }

        return {
            "agent": self.name,
            "status": "success",
            "data": {
                "total_leads": total,
                "new_leads": new,
                "leads": [],
                "priority_available": False,
            },
            "message": (
                f"There are {total} sales leads, including {new} new leads. "
                "The CRM currently provides aggregate lead counts, but no "
                "individual lead records or priority details. I therefore "
                "cannot identify a specific lead that needs attention from "
                "the available data."
            ),
        }

    def _get_customers_response(self, user, requested_entity=None):
        """Retrieve all customers or a specific requested customer."""
        result = self._crm_execute("get_customers", user)

        if not isinstance(result, dict) or result.get("status") != "success":
            return {
                "agent": self.name,
                "status": "error",
                "data": {},
                "message": (
                    "I could not retrieve the customer information " "at the moment."
                ),
            }

        customers = self._extract_list_from_result(result, "customers")

        if requested_entity:
            entity_lower = requested_entity.strip().lower()

            name_fields = (
                "name",
                "customer_name",
                "company",
                "company_name",
                "customer",
            )

            matching_customers = []

            for customer in customers:
                if not isinstance(customer, dict):
                    continue

                for field in name_fields:
                    value = customer.get(field)

                    if isinstance(value, str) and value.strip().lower() == entity_lower:
                        matching_customers.append(customer)
                        break

            if not matching_customers:
                return {
                    "agent": self.name,
                    "status": "success",
                    "data": {
                        "customer": requested_entity,
                        "customers": [],
                    },
                    "message": (
                        f"No matching CRM customer record was found "
                        f"for {requested_entity}."
                    ),
                }

            return {
                "agent": self.name,
                "status": "success",
                "data": {
                    "customer": requested_entity,
                    "customers": matching_customers,
                },
                "message": (
                    f"Here is the available CRM information for " f"{requested_entity}."
                ),
            }

        return {
            "agent": self.name,
            "status": "success",
            "data": {"customers": customers},
            "message": ("Here is the available customer information from the CRM."),
        }

    def _get_customer_details_response(
        self,
        user,
        requested_entity,
        attention_only=False,
    ):
        """Retrieve CRM details related to one named customer."""
        customer_result = self._get_customers_response(
            user,
            requested_entity,
        )

        if customer_result.get("status") != "success":
            return customer_result

        customers = customer_result.get("data", {}).get("customers", [])

        if not customers:
            return customer_result

        def normalize_name(value):
            return " ".join(
                str(value or "")
                .replace("\u00a0", " ")
                .replace("\u202f", " ")
                .casefold()
                .split()
            )

        target_name = normalize_name(requested_entity)

        def belongs_to_customer(record):
            if not isinstance(record, dict):
                return False

            for field in (
                "customer",
                "customer_name",
                "name",
                "company",
                "company_name",
            ):
                if normalize_name(record.get(field)) == target_name:
                    return True

            return False

        followup_result = self._get_followups_response(user)
        order_result = self._get_orders_response(user, "", "")
        followups = []
        orders = []
        if followup_result.get("status") == "success":
            all_followups = followup_result.get("data", {}).get("pending_followups", [])
            followups = [item for item in all_followups if belongs_to_customer(item)]

        if order_result.get("status") == "success":
            all_orders = order_result.get("data", {}).get("orders", [])
            orders = [item for item in all_orders if belongs_to_customer(item)]

        if attention_only:
            orders = [
                order
                for order in orders
                if str(order.get("status", "")).casefold() == "pending"
            ]
        customer = customers[0]
        customer_name = customer.get("name", requested_entity)
        details = [
            f"Customer: {customer_name}",
            f"Status: {customer.get('status', 'Not available')}",
            f"Contact email: {customer.get('email', 'Not available')}",
        ]

        if followups:
            details.append("Pending follow-ups:")
            for item in followups:
                details.append(
                    f"- Follow-up pending for "
                    f"{item.get('days_pending', 'unknown')} days"
                )

        elif attention_only:
            details.append("No pending follow-ups were found for this customer.")
        else:
            details.append("No pending follow-ups were found for this customer.")

        if orders:
            details.append("Related orders:")
            for order in orders:
                details.append(
                    f"- {order.get('order_id', 'Unknown order')}: "
                    f"₹{order.get('amount', 'Not available')} "
                    f"({order.get('status', 'Unknown status')})"
                )

        elif attention_only:
            details.append("No pending orders were found for this customer.")
        else:
            details.append("No related orders were found for this customer.")

        if attention_only:
            details.append(
                "These are the available pending items. The CRM data does "
                "not provide a priority ranking."
            )

        return {
            "agent": self.name,
            "status": "success",
            "data": {
                "customer": customer,
                "followups": followups,
                "orders": orders,
            },
            "message": "\n".join(details),
        }

    # ============================================================
    # SALES SUMMARY
    # ============================================================

    def _get_sales_summary_response(self, user):
        """Retrieve all supported sales summary sections."""
        leads_result = self._crm_execute("get_leads", user)
        followups_result = self._crm_execute("get_pending_followups", user)
        customers_result = self._crm_execute("get_customers", user)
        orders_result = self._crm_execute("get_orders", user)

        data = {}

        if isinstance(leads_result, dict) and leads_result.get("status") == "success":
            data["leads"] = self._extract_data(leads_result)

        if (
            isinstance(followups_result, dict)
            and followups_result.get("status") == "success"
        ):
            data["followups"] = self._extract_list_from_result(
                followups_result,
                "pending_followups",
            )

        if (
            isinstance(customers_result, dict)
            and customers_result.get("status") == "success"
        ):
            data["customers"] = self._extract_list_from_result(
                customers_result,
                "customers",
            )

        if isinstance(orders_result, dict) and orders_result.get("status") == "success":
            data["orders"] = self._extract_list_from_result(
                orders_result,
                "orders",
            )

        if not data:
            return {
                "agent": self.name,
                "status": "error",
                "data": {},
                "message": "I could not retrieve the sales summary at the moment.",
            }

        return {
            "agent": self.name,
            "status": "success",
            "data": data,
            "message": (
                "Here is the current sales summary, including the sales "
                "information successfully retrieved from the CRM."
            ),
        }

    # ============================================================
    # AGENT ROUTING
    # ============================================================

    def can_handle(self, request):
        sales_keywords = [
            "sales",
            "sale",
            "lead",
            "leads",
            "follow-up",
            "follow up",
            "followups",
            "follow-ups",
            "customer",
            "customers",
            "order",
            "orders",
            "revenue",
            "sales policy",
            "sales sop",
            "sales process",
        ]

        request_lower = str(request or "").lower()
        return any(keyword in request_lower for keyword in sales_keywords)

    # ============================================================
    # PERMISSIONS
    # ============================================================

    def get_required_permission(self, request):
        request_lower = str(request or "").lower()

        knowledge_keywords = [
            "policy",
            "sop",
            "process",
            "procedure",
            "how can",
            "how do",
            "how soon",
            "follow-up process",
            "follow up process",
        ]

        if any(keyword in request_lower for keyword in knowledge_keywords):
            return None

        if "lead" in request_lower:
            return "view_leads"

        if "customer" in request_lower:
            return "view_customers"

        if "ord-" in request_lower or "order" in request_lower:
            return "view_orders"

        if (
            "sales" in request_lower
            or "sale" in request_lower
            or "revenue" in request_lower
        ):
            return "view_sales"

        return "view_sales"

    # ============================================================
    # MAIN PROCESS
    # ============================================================

    def process(self, request, user, credentials=None):
        request = str(request or "")
        request_lower = request.lower()
        current_question = self._extract_current_question(request)

        is_contextual_request = self._is_contextual_request(request_lower)
        contextual_topic = self._get_contextual_topic(
            request_lower,
            current_question,
        )

        is_attention_question = self._is_attention_question(current_question)
        is_more_request = self._is_more_request(current_question)
        requested_entity = self._get_requested_entity(
            current_question
        ) or self._get_requested_entity(request)

        print(
            "[SALES CONTEXT DEBUG]",
            {
                "current_question": current_question,
                "is_contextual_request": is_contextual_request,
                "contextual_topic": contextual_topic,
                "is_attention_question": is_attention_question,
                "is_more_request": is_more_request,
                "requested_entity": requested_entity,
            },
        )

        # --------------------------------------------------------
        # KNOWLEDGE / SOP QUESTIONS
        # --------------------------------------------------------

        knowledge_keywords = [
            "policy",
            "sop",
            "process",
            "procedure",
            "how can",
            "how do",
            "how soon",
            "follow-up process",
            "follow up process",
        ]

        if any(keyword in current_question for keyword in knowledge_keywords):
            knowledge_answer = self.rag.generate_answer(request)

            if knowledge_answer:
                return {
                    "agent": self.name,
                    "status": "success",
                    "data": {"knowledge_answer": knowledge_answer},
                    "message": knowledge_answer,
                }

        # --------------------------------------------------------
        # ATTENTION QUESTIONS
        #
        # Topic-specific handling is based on explicit current
        # wording first, then the contextual topic supplied by
        # the orchestrator.
        # --------------------------------------------------------

        if is_attention_question:
            if self._is_explicit_followup_attention(current_question):
                return self._get_longest_followup_response(user)

            if self._is_explicit_lead_attention(current_question):
                return self._get_lead_attention_response(user)

            # Retrieve attention items for the specifically named customer.
            if requested_entity and is_contextual_request:
                return self._get_customer_details_response(
                    user,
                    requested_entity,
                    attention_only=True,
                )

            if is_contextual_request:
                if contextual_topic == "followups":
                    return self._get_longest_followup_response(user)

                if contextual_topic == "leads":
                    return self._get_lead_attention_response(user)

                if contextual_topic == "orders":
                    return self._get_orders_response(
                        user,
                        current_question,
                        request_lower,
                    )

                if contextual_topic == "customers":
                    return self._get_customers_response(user)

                if contextual_topic == "sales_status":
                    return self._get_sales_summary_response(user)

        # --------------------------------------------------------
        # LONGEST FOLLOW-UP QUESTIONS
        # --------------------------------------------------------

        if self._is_longest_followup_request(current_question):
            return self._get_longest_followup_response(user)

        # --------------------------------------------------------
        # CONTEXTUAL SALES STATUS
        # --------------------------------------------------------

        if (
            is_contextual_request
            and contextual_topic == "sales_status"
            and (is_more_request or current_question)
        ):
            return self._get_sales_summary_response(user)

        # --------------------------------------------------------
        # CONTEXTUAL LEADS
        # --------------------------------------------------------

        if (
            is_contextual_request
            and contextual_topic == "leads"
            and (
                is_more_request
                or requested_entity
                or "lead" in current_question
                or not current_question.strip()
            )
        ):
            return self._get_leads_response(user, requested_entity)

        # --------------------------------------------------------
        # CONTEXTUAL FOLLOW-UPS
        # --------------------------------------------------------

        if (
            is_contextual_request
            and contextual_topic == "followups"
            and (is_more_request or current_question)
        ):
            return self._get_followups_response(user)

        # --------------------------------------------------------
        # CONTEXTUAL ORDERS
        # --------------------------------------------------------

        if (
            is_contextual_request
            and contextual_topic == "orders"
            and (
                is_more_request
                or self._get_requested_order_id(current_question)
                or self._get_ordinal(current_question) is not None
                or "order" in current_question
                or "ord-" in current_question
                or is_attention_question
            )
        ):
            return self._get_orders_response(
                user,
                current_question,
                request_lower,
            )

        # --------------------------------------------------------
        # CONTEXTUAL CUSTOMERS
        # --------------------------------------------------------

        if (
            is_contextual_request
            and contextual_topic == "customers"
            and (
                is_more_request
                or requested_entity
                or "customer" in current_question
                or "status" in current_question
            )
        ):
            if requested_entity and is_more_request:
                return self._get_customer_details_response(
                    user,
                    requested_entity,
                    attention_only=False,
                )

            return self._get_customers_response(
                user,
                requested_entity,
            )

        # --------------------------------------------------------
        # GENERAL SALES SUMMARY
        # --------------------------------------------------------

        is_general_sales_request = any(
            phrase in current_question
            for phrase in [
                "sales",
                "sale",
                "sales status",
                "sales summary",
                "sales overview",
                "current sales",
                "revenue",
            ]
        )

        if is_general_sales_request:
            return self._get_sales_summary_response(user)

        # --------------------------------------------------------
        # STANDALONE FOLLOW-UPS
        # --------------------------------------------------------

        if any(
            term in current_question
            for term in [
                "follow-up",
                "follow up",
                "followups",
                "follow-ups",
            ]
        ):
            return self._get_followups_response(user)

        # --------------------------------------------------------
        # STANDALONE LEADS
        # --------------------------------------------------------

        if "lead" in current_question:
            return self._get_leads_response(user, requested_entity)

        # --------------------------------------------------------
        # STANDALONE CUSTOMERS
        # --------------------------------------------------------

        if "customer" in current_question:
            return self._get_customers_response(user)

        # --------------------------------------------------------
        # STANDALONE ORDERS
        # --------------------------------------------------------

        if "order" in current_question or "ord-" in current_question:
            return self._get_orders_response(
                user,
                current_question,
                request_lower,
            )

        # --------------------------------------------------------
        # STANDALONE NAMED CUSTOMER
        # --------------------------------------------------------

        if requested_entity:
            return self._get_customers_response(
                user,
                requested_entity,
            )

        # --------------------------------------------------------
        # UNSUPPORTED
        # --------------------------------------------------------

        return {
            "agent": self.name,
            "status": "unsupported",
            "data": {},
            "message": "The requested sales information is not currently supported.",
        }
