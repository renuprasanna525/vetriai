import json

from django.conf import settings
from groq import Groq


class LLMService:
    """
    Service responsible for generating natural-language
    responses using the Groq LLM.

    The LLM only explains and organizes verified
    application data. It must not invent business facts.
    """

    GROQ_TIMEOUT_SECONDS = 10.0

    def __init__(self):
        """Initialize the Groq client safely."""

        self.client = None

        self.api_key = getattr(
            settings,
            "GROQ_API_KEY",
            "",
        )

        self.model = getattr(
            settings,
            "GROQ_MODEL",
            "openai/gpt-oss-120b",
        )

        if self.api_key:
            try:
                self.client = Groq(
                    api_key=self.api_key,
                    timeout=self.GROQ_TIMEOUT_SECONDS,
                    max_retries=0,
                )
            except Exception as error:
                print(
                    "GROQ CLIENT INITIALIZATION ERROR:",
                    str(error),
                )
                self.client = None

    def _get_client(self):
        """Return the existing Groq client or initialize it."""

        if self.client is not None:
            return self.client

        if not self.api_key:
            print("GROQ API KEY IS NOT CONFIGURED.")
            return None

        try:
            self.client = Groq(
                api_key=self.api_key,
                timeout=self.GROQ_TIMEOUT_SECONDS,
                max_retries=0,
            )

            return self.client

        except Exception as error:
            print(
                "GROQ CLIENT INITIALIZATION ERROR:",
                str(error),
            )
            return None

    def _is_daily_quota_error(self, error_message):
        """Detect quota or rate-limit errors."""

        quota_indicators = [
            "rate_limit_exceeded",
            "rate limit",
            "quota exceeded",
            "quota exhausted",
            "tokens per day",
            "requests per day",
            "429",
        ]

        return any(indicator in error_message for indicator in quota_indicators)

    def _is_temporary_error(self, error_message):
        """Detect temporary or network availability errors."""

        temporary_indicators = [
            "503",
            "502",
            "500",
            "unavailable",
            "high demand",
            "temporarily unavailable",
            "timeout",
            "timed out",
            "readtimeout",
            "connecttimeout",
            "connection reset",
            "server disconnected",
            "service unavailable",
        ]

        return any(indicator in error_message for indicator in temporary_indicators)

    def _generate_response(self, prompt):
        """
        Generate a response using Groq.

        Returns None on failure so the orchestrator
        can use its application fallback response.
        """

        client = self._get_client()

        if client is None:
            print("GROQ API IS NOT AVAILABLE.")
            return None

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            print("GROQ RESPONSE SUCCESS")
            print("GROQ MODEL:", self.model)

            if not response or not response.choices:
                print("GROQ RETURNED EMPTY RESPONSE.")
                return None

            response_text = response.choices[0].message.content

            if not response_text:
                print("GROQ RETURNED NO TEXT RESPONSE.")
                return None

            return response_text.strip()

        except Exception as error:
            error_message = str(error).lower()

            print(
                "GROQ RESPONSE ERROR:",
                str(error),
            )

            if self._is_daily_quota_error(error_message):
                print(
                    "GROQ RATE LIMIT OR QUOTA REACHED. "
                    "USING APPLICATION FALLBACK RESPONSE."
                )

            elif self._is_temporary_error(error_message):
                print(
                    "GROQ TEMPORARY OR NETWORK ERROR. "
                    "USING APPLICATION FALLBACK RESPONSE."
                )

            else:
                print("GROQ RESPONSE FAILED. " "USING APPLICATION FALLBACK RESPONSE.")

            return None

    def generate_answer(self, question, context):
        """
        Generate an answer using company knowledge.
        """

        prompt = f"""
You are Vetri AI, a professional business assistant.

Answer the user's question using ONLY the verified
company knowledge provided below.

Rules:

1. Do not invent facts, numbers, names, dates, or business information.
2. Do not change any numerical values.
3. If the requested information is not available, clearly say so.
4. Answer the user's actual question first.
5. Use natural, professional language.
6. Explain the information clearly instead of simply repeating raw data.
7. Keep the response concise but useful.
8. Do not mention prompts, models, APIs, or internal implementation.

VERIFIED COMPANY KNOWLEDGE:
{context}

USER QUESTION:
{question}

Provide the final answer directly to the user.
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
        using verified results returned by authorized agents.
        """

        agent_results_text = json.dumps(
            agent_results,
            indent=2,
            default=str,
        )

        prompt = f"""
You are Vetri AI, a professional business AI assistant.

Your task is to convert verified business information
returned by authorized application agents into a natural,
helpful, ChatGPT-style response.

The application has already handled:

- user authentication
- permissions
- agent selection
- business-data retrieval
- tool execution
- authorization

Therefore, your job is NOT to decide permissions,
invent business information, or perform business operations.

Your job is to explain the verified results naturally.

STRICT DATA RULES:

1. Use ONLY the information contained in AUTHORIZED AGENT RESULTS.
2. Never invent facts, numbers, names, dates, statuses, tasks,
   events, customers, projects, leads, or other business information.
3. Never change numerical values.
4. Never assume information that is not present.
5. If information is missing, clearly say that it is not available.
6. If an agent result contains an error, do not hide the error
   by inventing an answer.
7. Never claim that an action was completed unless the result
   explicitly confirms that it was completed.
8. Do not create fictional examples and present them as company data.

CONVERSATION RULES:

9. Use the previous conversation to understand references such as:
   "it", "its", "them", "that project", "that customer",
   "what about sales", or "tell me more".
10. Treat the CURRENT USER QUESTION as the main question.
11. Use previous conversation only to understand context.
12. Do not repeat the entire previous conversation.
13. If the current question changes to another business area,
    answer the new question normally.
14. If several authorized results are available, combine them
    into one coherent response.
15. Do not expose internal routing or processing details.

RESPONSE STYLE:

16. Answer the user's question first.
17. Use complete natural sentences.
18. Make the response conversational rather than a raw data dump.
19. Give useful supporting details when they are available.
20. Use short paragraphs or bullet points when they improve readability.
21. Do not make every response follow the same template.
22. Avoid repeatedly using phrases such as:
    "Here is the information",
    "Based on the data",
    or
    "Would you like to know more?"
23. Ask a follow-up question only when it is genuinely useful
    and the available information supports a meaningful next step.
24. Do not force a follow-up question after every response.
25. Do not make unsupported judgments such as:
    "good", "bad", "strong", "weak", "healthy",
    "unhealthy", "successful", or "needs improvement"
    unless the verified results explicitly support that wording.
26. Do not expose Groq, Gemini, OpenAI, the LLM, prompts,
    API calls, or internal implementation details.
27. Do not mention "Agent 1", "Agent 2", or internal agent names
    unless the user specifically asks how the system works.
28. Keep the answer focused on the user's request.
29. If the available information is only a summary,
    clearly present it as a summary.
30. If multiple business areas are involved, organize the
    information so that the relationship between them is clear.

IMPORTANT:

The verified agent results are the source of truth.

Conversation context helps you understand what the user means,
but conversation context must NOT be treated as new business data.

If the conversation says something previously but the current
authorized results do not contain that information, do not
reconstruct or invent the missing business information.

PREVIOUS CONVERSATION:
{conversation_context}

CURRENT USER QUESTION:
{question}

AUTHORIZED AGENT RESULTS:
{agent_results_text}

Now write the final response that Vetri AI should show to the user.
"""

        return self._generate_response(prompt)
