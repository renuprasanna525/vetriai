import json
import time

from django.conf import settings
from google import genai
from google.genai import types


class LLMService:
    """
    Service responsible for generating natural-language
    answers using the Gemini LLM.
    """

    # Gemini network timeout in milliseconds.
    # 30 seconds prevents the Render worker from waiting indefinitely.
    GEMINI_TIMEOUT_MS = 30000

    def __init__(self):
        """
        Initialize the Gemini client safely.

        If the API key is missing or the client cannot be
        initialized, the application can continue running.
        """

        self.client = None
        self.api_key = getattr(settings, "GEMINI_API_KEY", "")

        if self.api_key:
            try:
                self.client = genai.Client(
                    api_key=self.api_key,
                    http_options=types.HttpOptions(
                        timeout=self.GEMINI_TIMEOUT_MS,
                    ),
                )
            except Exception as error:
                print(
                    "GEMINI CLIENT INITIALIZATION ERROR:",
                    str(error),
                )
                self.client = None

    def _get_client(self):
        """
        Return the existing Gemini client.

        If the client is not available, try to create it again.
        """

        if self.client is not None:
            return self.client

        if not self.api_key:
            print("GEMINI API KEY IS NOT CONFIGURED.")
            return None

        try:
            self.client = genai.Client(
                api_key=self.api_key,
                http_options=types.HttpOptions(
                    timeout=self.GEMINI_TIMEOUT_MS,
                ),
            )
            return self.client

        except Exception as error:
            print(
                "GEMINI CLIENT INITIALIZATION ERROR:",
                str(error),
            )
            return None

    def _is_daily_quota_error(self, error_message):
        """
        Detect Gemini daily/free-tier quota errors.
        """

        daily_quota_indicators = [
            "generaterequestsperdayperprojectpermodel-freetier",
            "generate_content_free_tier_requests",
            "quota exceeded for metric",
            "you exceeded your current quota",
            "quota exhausted",
            "daily quota",
            "rpd",
        ]

        return any(indicator in error_message for indicator in daily_quota_indicators)

    def _is_temporary_error(self, error_message):
        """
        Detect temporary Gemini/network availability errors.
        """

        temporary_error_indicators = [
            "503",
            "unavailable",
            "service unavailable",
            "high demand",
            "temporarily unavailable",
            "timeout",
            "timed out",
            "readtimeout",
            "connecttimeout",
            "connect error",
            "connection reset",
            "server disconnected",
        ]

        return any(
            indicator in error_message for indicator in temporary_error_indicators
        )

    def _generate_response(self, prompt):
        """
        Generate a text response using Gemini.

        Behavior:

        - Successful Gemini request -> return Gemini response.
        - Daily quota error -> stop immediately and use fallback.
        - Temporary/network error -> retry once.
        - Final Gemini failure -> return None.
        - Returning None allows the orchestrator to use its
          verified application fallback response.
        """

        client = self._get_client()

        if client is None:
            print("GEMINI API IS NOT AVAILABLE.")
            return None

        max_retries = 1
        retry_delay = 2

        for attempt in range(max_retries + 1):
            try:
                response = client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=prompt,
                )

                if not response:
                    print("GEMINI RETURNED EMPTY RESPONSE.")
                    return None

                response_text = getattr(
                    response,
                    "text",
                    None,
                )

                if not response_text:
                    print("GEMINI RETURNED NO TEXT RESPONSE.")
                    return None

                return response_text.strip()

            except Exception as error:
                error_message = str(error).lower()

                print(
                    f"GEMINI ERROR ON ATTEMPT {attempt + 1}:",
                    str(error),
                )

                # Daily quota errors should not be retried.
                if self._is_daily_quota_error(error_message):
                    print(
                        "GEMINI DAILY QUOTA EXHAUSTED. "
                        "USING APPLICATION FALLBACK RESPONSE."
                    )
                    return None

                # Retry temporary/network failures only once.
                if self._is_temporary_error(error_message) and attempt < max_retries:
                    print(
                        "GEMINI TEMPORARY OR NETWORK ERROR. "
                        f"Retrying once in {retry_delay} seconds..."
                    )

                    time.sleep(retry_delay)
                    continue

                # Final failure.
                print("GEMINI RESPONSE FAILED. " "USING APPLICATION FALLBACK RESPONSE.")

                return None

        return None

    def generate_answer(self, question, context):
        """
        Generate a natural-language answer using company knowledge.
        """

        prompt = f"""
You are a helpful company AI assistant.

Answer the user's question using ONLY the company
knowledge provided below.

If the answer cannot be found in the provided
company knowledge, say that the information is
not available in the company knowledge base.

Do not invent facts, numbers, names, or business
information.

Company Knowledge:
{context}

User Question:
{question}

Provide a clear and useful answer.
"""

        return self._generate_response(prompt)

    def generate_chat_response(
        self,
        question,
        agent_results,
        conversation_context="",
    ):
        """
        Generate the final conversational response
        using the authorized agent results.
        """

        agent_results_text = json.dumps(
            agent_results,
            indent=2,
            default=str,
        )

        prompt = f"""
You are Vetri AI, a professional business AI assistant.

Your job is to answer the user's question naturally,
clearly, and conversationally using the verified
business information returned by the authorized agents.

IMPORTANT RULES:

1. Use ONLY the information provided in the agent results.
2. Do not invent numbers, facts, names, events, or business information.
3. Do not change numerical values.
4. Do not claim that an action was completed unless the agent result says so.
5. Respect the user's previous conversation context.
6. If multiple agents provided information, combine the information
   into one coherent answer.
7. Do not expose internal agent-processing details unless useful.
8. Do not say "Agent 1", "Agent 2", etc.
9. Use natural business language.
10. Give enough explanation to feel like a real AI assistant.
11. Avoid extremely short one-line answers when useful details are available.
12. Do not add information that is not present in the results.
13. Do not make unsupported judgments such as "good", "bad",
    "positive", "negative", "strong", "weak", "healthy", or
    "needs improvement" unless the agent results explicitly
    support that statement.
14. You may explain or reorganize the provided information,
    but do not introduce new business facts.
15. If an agent provides only summary figures, clearly describe
    those figures without pretending that additional detailed
    information is available.
16. If an agent failed, clearly mention that the information could
    not be retrieved rather than guessing.
17. Use headings or bullet points only when they improve readability.
18. Do not repeatedly use the same follow-up wording.
19. Keep the answer focused on the user's question.
20. If the user asks a follow-up question, use the previous conversation
    context to understand what they are referring to.
21. Do not mention Gemini, OpenAI, the LLM, prompts, or internal
    implementation details to the user.
22. If the available information is limited, clearly state what is
    available instead of making assumptions.
23. When several business areas are available, organize the response
    so that the information is easy to understand.
24. Prefer complete sentences and short explanations over raw data dumps.
25. Answer the user's actual question first, then provide supporting
    details when useful.

PREVIOUS CONVERSATION:
{conversation_context}

CURRENT USER QUESTION:
{question}

AUTHORIZED AGENT RESULTS:
{agent_results_text}

Now provide the final response to the user.
"""

        return self._generate_response(prompt)
