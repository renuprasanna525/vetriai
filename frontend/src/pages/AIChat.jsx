import { useEffect, useRef, useState } from "react";
import "./AIChat.css";
import { authFetch } from "../services/authFetch";

const API_BASE_URL =
  "https://vetri-ai-backend-i3pw.onrender.com/api";
const AI_BOT_IMAGE = "/ai-bot.gif";

function AIChat() {
  const [messages, setMessages] = useState([
    {
      sender: "ai",
      text: "Hello! I am Vetri AI BO Assistant. How can I help you today?",
    },
  ]);

  const [conversationId, setConversationId] = useState(null);
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  /*
   * Load the current user's latest conversation
   * when AI Chat page opens.
   */
  useEffect(() => {
    const loadConversationHistory = async () => {
      const accessToken = localStorage.getItem("access_token");

      if (!accessToken) {
        setIsLoadingHistory(false);
        return;
      }

      try {
        const response = await authFetch(
          `${API_BASE_URL}/conversations/`,
          {
            method: "GET",
            credentials: "include",
          }
        );

        if (!response.ok) {
          throw new Error("Failed to load conversations");
        }

        const data = await response.json();

        const conversations = data.conversations || [];

        if (conversations.length > 0) {
          const latestConversation = conversations[0];

          setConversationId(latestConversation.id);

          const detailResponse = await authFetch(
            `${API_BASE_URL}/conversations/${latestConversation.id}/`,
            {
              method: "GET",
              credentials: "include",
            }
          );

          if (!detailResponse.ok) {
            throw new Error(
              "Failed to load conversation details"
            );
          }

          const detailData = await detailResponse.json();

          const savedMessages =
            detailData.conversation?.messages || [];

          const formattedMessages = savedMessages.map(
            (message) => ({
              sender:
                message.sender === "user"
                  ? "user"
                  : "ai",
              text: message.content,
            })
          );

          if (formattedMessages.length > 0) {
            setMessages(formattedMessages);
          }
        }
      } catch (error) {
        console.error(
          "Conversation History Error:",
          error
        );
      } finally {
        setIsLoadingHistory(false);
      }
    };

    loadConversationHistory();
  }, []);

  /*
   * Keep chat scrolled to the latest message.
   */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, isLoading]);

  /*
   * Send message to Vetri AI.
   */
  const handleSend = async () => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || isLoading) {
      return;
    }

    const userMessage = {
      sender: "user",
      text: trimmedQuestion,
    };

    setMessages((previousMessages) => [
      ...previousMessages,
      userMessage,
    ]);

    setQuestion("");
    setIsLoading(true);

    const accessToken = localStorage.getItem("access_token");

    if (!accessToken) {
      setIsLoading(false);

      const aiMessage = {
        sender: "ai",
        text: "You are not logged in. Please login again.",
      };

      setMessages((previousMessages) => [
        ...previousMessages,
        aiMessage,
      ]);

      return;
    }

    try {
      const requestBody = {
        message: trimmedQuestion,
      };

      if (conversationId) {
        requestBody.conversation_id = conversationId;
      }

      const response = await authFetch(
        `${API_BASE_URL}/chat/`,
        {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestBody),
        }
      );

      if (!response.ok) {
        throw new Error(
          "Failed to get response from AI"
        );
      }

      const data = await response.json();

      if (data.conversation_id) {
        setConversationId(data.conversation_id);
      }

      const aiMessage = {
        sender: "ai",
        text:
          data.response ||
          "No response received from AI.",
        metadata: data.metadata || null,
      };

      setMessages((previousMessages) => [
        ...previousMessages,
        aiMessage,
      ]);
    } catch (error) {
      console.error("Chat API Error:", error);

      const aiMessage = {
        sender: "ai",
        text: "Sorry, I could not connect to the AI service.",
      };

      setMessages((previousMessages) => [
        ...previousMessages,
        aiMessage,
      ]);
    } finally {
      setIsLoading(false);

      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  };

  /*
   * Enter key support.
   */
  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  /*
   * Suggestion button.
   */
  const handleSuggestion = (text) => {
    setQuestion(text);
    inputRef.current?.focus();
  };

  const handleNewChat = () => {
    setConversationId(null);

    setMessages([
      {
        sender: "ai",
        text: "Hello! I am Vetri AI BO Assistant. How can I help you today?",
      },
    ]);

    setQuestion("");

    setTimeout(() => {
      inputRef.current?.focus();
    }, 100);
  };

  return (
    <div className="ai-chat-page">

      {/* =====================================================
          PAGE HEADER
      ===================================================== */}

      <div className="ai-chat-topbar">

        <div>
          <h2 className="ai-chat-page-title">
            AI Chat
          </h2>

          <p className="ai-chat-page-subtitle">
            Interact with Vetri AI Business Operations Assistant
          </p>
        </div>

        <div className="ai-status">
          <span className="ai-status-dot"></span>
          AI Online
        </div>

      </div>


      {/* =====================================================
          CHAT CONTAINER
      ===================================================== */}

      <div className="ai-chat-container">


        {/* ===================================================
            CHAT HEADER
        =================================================== */}

        <div className="ai-chat-header">

          <div className="ai-chat-brand">

            {/* Animated AI GIF */}

            <div className="ai-chat-avatar">

              <img
                src={AI_BOT_IMAGE}
                alt="Vetri AI"
                className="ai-bot-gif"
              />

            </div>


            <div>

              <h5 className="mb-1">
                Vetri AI BO Assistant
              </h5>

              <div className="ai-chat-online">
                <span></span>
                Ready to assist
              </div>

            </div>

          </div>


          <div className="ai-chat-header-actions">

            <button
              type="button"
              className="ai-new-chat-button"
              onClick={handleNewChat}
              title="Start a new conversation"
            >
              <i className="bi bi-plus-lg"></i>
              <span>New Chat</span>
            </button>

            <div className="ai-chat-header-icon">
              <i className="bi bi-three-dots-vertical"></i>
            </div>

          </div>

        </div>


        {/* ===================================================
            MESSAGES
        =================================================== */}

        <div className="ai-chat-messages">


          {/* =================================================
              WELCOME SECTION
          ================================================= */}

          {!isLoadingHistory &&
            messages.length === 1 &&
            messages[0].sender === "ai" && (

              <div className="ai-welcome">


                {/* Bot GIF */}

                <div className="ai-welcome-icon">

                  <img
                    src={AI_BOT_IMAGE}
                    alt="Vetri AI Assistant"
                    className="ai-welcome-bot"
                  />

                </div>


                <h4>
                  How can I help you?
                </h4>

                <p>
                  Ask me about employees, projects,
                  sales, reports, tasks and more.
                </p>


                {/* Quick Suggestions */}

                <div className="ai-suggestions">

                  <button
                    type="button"
                    onClick={() =>
                      handleSuggestion(
                        "Show finance summary"
                      )
                    }
                  >
                    <i className="bi bi-currency-rupee"></i>
                    Finance summary
                  </button>


                  <button
                    type="button"
                    onClick={() =>
                      handleSuggestion(
                        "Show my projects"
                      )
                    }
                  >
                    <i className="bi bi-kanban"></i>
                    My projects
                  </button>


                  <button
                    type="button"
                    onClick={() =>
                      handleSuggestion(
                        "Show pending tasks"
                      )
                    }
                  >
                    <i className="bi bi-list-check"></i>
                    Pending tasks
                  </button>

                </div>

              </div>

            )}


          {/* =================================================
              CHAT MESSAGES
          ================================================= */}

          {messages.map((message, index) => (

            <div
              key={index}
              className={`ai-message-row ${message.sender === "user"
                ? "user-message-row"
                : "ai-message-row-left"
                }`}
            >


              {/* =================================================
                  AI BOT AVATAR
              ================================================= */}

              {message.sender === "ai" && (

                <div className="message-avatar ai-avatar">

                  <img
                    src={AI_BOT_IMAGE}
                    alt="Vetri AI"
                    className="ai-message-bot"
                  />

                </div>

              )}


              {/* =================================================
                  MESSAGE BUBBLE
              ================================================= */}

              <div
                className={`ai-message ${message.sender === "user"
                  ? "user-message"
                  : "assistant-message"
                  }`}
              >

                <div className="message-name">

                  {message.sender === "user"
                    ? "You"
                    : "Vetri AI"}

                </div>


                <div className="message-text">
                  {message.text}
                </div>


                {/* =================================================
                    METADATA
                ================================================= */}

                {message.sender === "ai" &&
                  message.metadata && (

                    <div className="ai-message-metadata">

                      <div>
                        <strong>Source:</strong>{" "}
                        {message.metadata.source ||
                          "Vetri AI"}
                      </div>

                      <div>
                        <strong>Updated:</strong>{" "}
                        {message.metadata.updated_at
                          ? new Date(
                            message.metadata.updated_at
                          ).toLocaleString()
                          : "Not available"}
                      </div>

                      <div>
                        <strong>Confidence:</strong>{" "}
                        {message.metadata.confidence ||
                          "Not available"}
                      </div>

                    </div>

                  )}

              </div>


              {/* =================================================
                  USER AVATAR
              ================================================= */}

              {message.sender === "user" && (

                <div className="message-avatar user-avatar">

                  <i className="bi bi-person-fill"></i>

                </div>

              )}

            </div>

          ))}


          {/* =================================================
              TYPING INDICATOR
          ================================================= */}

          {isLoading && (

            <div className="ai-message-row ai-message-row-left">

              <div className="message-avatar ai-avatar">

                <img
                  src={AI_BOT_IMAGE}
                  alt="Vetri AI"
                  className="ai-message-bot"
                />

              </div>


              <div className="ai-message assistant-message typing-message">

                <div className="message-name">
                  Vetri AI
                </div>


                <div className="typing-indicator">

                  <span></span>
                  <span></span>
                  <span></span>

                </div>

              </div>

            </div>

          )}


          <div ref={messagesEndRef}></div>

        </div>


        {/* =====================================================
            INPUT AREA
        ===================================================== */}

        <div className="ai-chat-input-area">

          <div className="ai-chat-input-wrapper">

            <input
              ref={inputRef}
              type="text"
              className="ai-chat-input"
              placeholder="Ask Vetri AI anything..."
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              onKeyDown={handleKeyDown}
              disabled={isLoading}
            />


            <button
              type="button"
              className="ai-send-button"
              onClick={handleSend}
              disabled={
                !question.trim() || isLoading
              }
              aria-label="Send message"
            >

              <i className="bi bi-send-fill"></i>

            </button>

          </div>


          <div className="ai-chat-footer-text">

            <i className="bi bi-shield-check"></i>

            Vetri AI can make mistakes. Verify important information.

          </div>

        </div>

      </div>

    </div>
  );
}

export default AIChat;