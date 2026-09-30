
import { useCallback, useEffect, useRef, useState } from "react";
import "./AIChat.css";
import { authFetch } from "../services/authFetch";

const API_BASE_URL = "https://vetri-ai-backend-i3pw.onrender.com/api";
const AI_BOT_IMAGE = "/ai-bot.gif";
const NEW_CHAT_KEY = "vetri_ai_new_chat";

const WELCOME_MESSAGE = {
  sender: "ai",
  text: "Hello! I am Vetri AI BO Assistant. How can I help you today?",
};

function formatMessages(savedMessages = []) {
  return savedMessages.map((message) => ({
    id: message.id,
    sender: message.sender === "user" ? "user" : "ai",
    text: message.content,
    createdAt: message.created_at,
  }));
}

function formatConversationDate(dateValue) {
  if (!dateValue) return "";

  const date = new Date(dateValue);
  if (Number.isNaN(date.getTime())) return "";

  const today = new Date();
  const isToday = date.toDateString() === today.toDateString();

  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);
  const isYesterday = date.toDateString() === yesterday.toDateString();

  if (isToday) {
    return date.toLocaleTimeString([], {
      hour: "numeric",
      minute: "2-digit",
    });
  }

  if (isYesterday) return "Yesterday";

  return date.toLocaleDateString([], {
    month: "short",
    day: "numeric",
    year: date.getFullYear() === today.getFullYear() ? undefined : "numeric",
  });
}

function getConversationTitle(conversation) {
  return conversation.title?.trim() || "New Conversation";
}

function AIChat() {
  const [messages, setMessages] = useState([WELCOME_MESSAGE]);
  const [conversations, setConversations] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [isLoadingConversation, setIsLoadingConversation] = useState(false);
  const [historyError, setHistoryError] = useState("");
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const loadConversations = useCallback(async () => {
    const response = await authFetch(`${API_BASE_URL}/conversations/`, {
      method: "GET",
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error("Failed to load conversations.");
    }

    const data = await response.json();
    const items = Array.isArray(data.conversations)
      ? data.conversations
      : [];

    const sortedItems = [...items].sort((a, b) => {
      const dateA = new Date(a.updated_at || a.created_at || 0).getTime();
      const dateB = new Date(b.updated_at || b.created_at || 0).getTime();
      return dateB - dateA;
    });

    setConversations(sortedItems);
    return sortedItems;
  }, []);

  const loadConversation = useCallback(async (id) => {
    setIsLoadingConversation(true);
    setHistoryError("");

    try {
      const response = await authFetch(
        `${API_BASE_URL}/conversations/${id}/`,
        {
          method: "GET",
          credentials: "include",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to load this conversation.");
      }

      const data = await response.json();
      const conversation = data.conversation;

      if (!conversation) {
        throw new Error("Conversation details were not returned.");
      }

      setConversationId(conversation.id);
      setMessages(formatMessages(conversation.messages));

      sessionStorage.removeItem(NEW_CHAT_KEY);
      setIsSidebarOpen(false);
    } catch (error) {
      console.error("Conversation Detail Error:", error);
      setHistoryError("Unable to open this conversation. Please try again.");
    } finally {
      setIsLoadingConversation(false);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;

    const initializeChat = async () => {
      if (sessionStorage.getItem(NEW_CHAT_KEY) === "true") {
        if (isMounted) {
          setMessages([WELCOME_MESSAGE]);
          setConversationId(null);
          setIsLoadingHistory(false);
        }
        return;
      }

      if (!localStorage.getItem("access_token")) {
        if (isMounted) setIsLoadingHistory(false);
        return;
      }

      try {
        const items = await loadConversations();

        if (!isMounted) return;

        if (items.length > 0) {
          await loadConversation(items[0].id);
        } else {
          setMessages([WELCOME_MESSAGE]);
          setConversationId(null);
        }
      } catch (error) {
        console.error("Conversation History Error:", error);
        if (isMounted) {
          setHistoryError("Unable to load conversation history.");
        }
      } finally {
        if (isMounted) setIsLoadingHistory(false);
      }
    };

    initializeChat();

    return () => {
      isMounted = false;
    };
  }, [loadConversations, loadConversation]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, isLoading, isLoadingConversation]);

  const handleNewChat = () => {
    sessionStorage.setItem(NEW_CHAT_KEY, "true");
    setConversationId(null);
    setMessages([WELCOME_MESSAGE]);
    setQuestion("");
    setHistoryError("");
    setIsSidebarOpen(false);

    setTimeout(() => inputRef.current?.focus(), 100);
  };

  const handleSelectConversation = (id) => {
    if (isLoading || isLoadingConversation || id === conversationId) {
      setIsSidebarOpen(false);
      return;
    }

    loadConversation(id);
  };

  const handleSend = async () => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || isLoading || isLoadingConversation) return;

    if (!localStorage.getItem("access_token")) {
      setMessages((previous) => [
        ...previous,
        {
          sender: "ai",
          text: "You are not logged in. Please login again.",
        },
      ]);
      return;
    }

    const userMessage = {
      sender: "user",
      text: trimmedQuestion,
      createdAt: new Date().toISOString(),
    };

    setMessages((previous) => [...previous, userMessage]);
    setQuestion("");
    setIsLoading(true);
    setHistoryError("");

    try {
      const requestBody = { message: trimmedQuestion };

      if (conversationId) {
        requestBody.conversation_id = conversationId;
      }

      const response = await authFetch(`${API_BASE_URL}/chat/`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error("Failed to get response from AI.");
      }

      const data = await response.json();

      if (data.conversation_id) {
        setConversationId(data.conversation_id);
        sessionStorage.removeItem(NEW_CHAT_KEY);
      }

      setMessages((previous) => [
        ...previous,
        {
          sender: "ai",
          text: data.response || "No response received from AI.",
          metadata: data.metadata || null,
          createdAt: data.metadata?.updated_at || new Date().toISOString(),
        },
      ]);

      const items = await loadConversations();

      // Keep the newly active conversation visible in the history list.
      if (
        data.conversation_id &&
        !items.some((item) => item.id === data.conversation_id)
      ) {
        await loadConversations();
      }
    } catch (error) {
      console.error("Chat API Error:", error);

      setMessages((previous) => [
        ...previous,
        {
          sender: "ai",
          text: "Sorry, I could not connect to the AI service. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const handleSuggestion = (text) => {
    setQuestion(text);
    inputRef.current?.focus();
  };

  return (
    <div className="ai-chat-page">
      <div className="ai-chat-topbar">
        <div className="ai-chat-title-group">
          <button
            type="button"
            className="ai-sidebar-toggle"
            onClick={() => setIsSidebarOpen((open) => !open)}
            aria-label={isSidebarOpen ? "Close conversation history" : "Open conversation history"}
            aria-expanded={isSidebarOpen}
          >
            <i className="bi bi-list"></i>
          </button>

          <div>
            <h2 className="ai-chat-page-title">AI Chat</h2>
            <p className="ai-chat-page-subtitle">
              Interact with Vetri AI Business Operations Assistant
            </p>
          </div>
        </div>

        <div className="ai-status">
          <span className="ai-status-dot"></span>
          AI Online
        </div>
      </div>

      <div className={`ai-chat-workspace ${isSidebarOpen ? "sidebar-open" : ""}`}>
        {isSidebarOpen && (
          <button
            type="button"
            className="ai-sidebar-backdrop"
            onClick={() => setIsSidebarOpen(false)}
            aria-label="Close sidebar"
          />
        )}

        <aside className="ai-history-sidebar">
          <div className="ai-history-heading">
            <div>
              <h3>Chat history</h3>
              <p>Your previous conversations</p>
            </div>
            <button
              type="button"
              className="ai-sidebar-close"
              onClick={() => setIsSidebarOpen(false)}
              aria-label="Close history"
            >
              <i className="bi bi-x-lg"></i>
            </button>
          </div>

          <button
            type="button"
            className="ai-history-new-chat"
            onClick={handleNewChat}
          >
            <i className="bi bi-plus-lg"></i>
            <span>New Chat</span>
          </button>

          <div className="ai-history-list">
            {isLoadingHistory && (
              <div className="ai-history-message">
                <span className="ai-history-spinner"></span>
                Loading conversations...
              </div>
            )}

            {!isLoadingHistory && historyError && (
              <div className="ai-history-error">
                {historyError}
                <button
                  type="button"
                  onClick={async () => {
                    setHistoryError("");
                    setIsLoadingHistory(true);
                    try {
                      await loadConversations();
                    } catch (error) {
                      setHistoryError("Unable to load conversation history.");
                    } finally {
                      setIsLoadingHistory(false);
                    }
                  }}
                >
                  Retry
                </button>
              </div>
            )}

            {!isLoadingHistory && !historyError && conversations.length === 0 && (
              <div className="ai-history-empty">
                <i className="bi bi-chat-square-text"></i>
                <span>No previous conversations</span>
                <small>Your chats will appear here.</small>
              </div>
            )}

            {!isLoadingHistory &&
              conversations.map((conversation) => (
                <button
                  type="button"
                  key={conversation.id}
                  className={`ai-history-item ${conversation.id === conversationId ? "active" : ""
                    }`}
                  onClick={() => handleSelectConversation(conversation.id)}
                  disabled={isLoadingConversation || isLoading}
                >
                  <i className="bi bi-chat-left-text"></i>
                  <span className="ai-history-item-content">
                    <span className="ai-history-item-title">
                      {getConversationTitle(conversation)}
                    </span>
                    <span className="ai-history-item-date">
                      {formatConversationDate(
                        conversation.updated_at || conversation.created_at
                      )}
                    </span>
                  </span>
                </button>
              ))}
          </div>

          <div className="ai-history-footer">
            <i className="bi bi-shield-check"></i>
            Your conversations are private to your account.
          </div>
        </aside>

        <section className="ai-chat-container">
          <div className="ai-chat-header">
            <div className="ai-chat-brand">
              <div className="ai-chat-avatar">
                <img src={AI_BOT_IMAGE} alt="Vetri AI" className="ai-bot-gif" />
              </div>

              <div>
                <h5 className="mb-1">Vetri AI BO Assistant</h5>
                <div className="ai-chat-online">
                  <span></span>
                  {isLoadingConversation ? "Loading conversation..." : "Ready to assist"}
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
              <div className="ai-chat-header-icon" title="Vetri AI">
                <i className="bi bi-three-dots-vertical"></i>
              </div>
            </div>
          </div>

          <div className="ai-chat-messages">
            {isLoadingConversation && (
              <div className="ai-conversation-loading">
                <span className="ai-history-spinner"></span>
                Loading messages...
              </div>
            )}

            {!isLoadingHistory &&
              !isLoadingConversation &&
              messages.length === 1 &&
              messages[0].sender === "ai" && (
                <div className="ai-welcome">
                  <div className="ai-welcome-icon">
                    <img
                      src={AI_BOT_IMAGE}
                      alt="Vetri AI Assistant"
                      className="ai-welcome-bot"
                    />
                  </div>

                  <h4>How can I help you?</h4>
                  <p>
                    Ask me about employees, projects, sales, reports, tasks and more.
                  </p>

                  <div className="ai-suggestions">
                    <button type="button" onClick={() => handleSuggestion("Show finance summary")}>
                      <i className="bi bi-currency-rupee"></i>
                      Finance summary
                    </button>
                    <button type="button" onClick={() => handleSuggestion("Show my projects")}>
                      <i className="bi bi-kanban"></i>
                      My projects
                    </button>
                    <button type="button" onClick={() => handleSuggestion("Show pending tasks")}>
                      <i className="bi bi-list-check"></i>
                      Pending tasks
                    </button>
                  </div>
                </div>
              )}

            {messages.map((message, index) => (
              <div
                key={message.id || `${message.sender}-${index}`}
                className={`ai-message-row ${message.sender === "user" ? "user-message-row" : "ai-message-row-left"
                  }`}
              >
                {message.sender === "ai" && (
                  <div className="message-avatar ai-avatar">
                    <img src={AI_BOT_IMAGE} alt="Vetri AI" className="ai-message-bot" />
                  </div>
                )}

                <div
                  className={`ai-message ${message.sender === "user" ? "user-message" : "assistant-message"
                    }`}
                >
                  <div className="message-name">
                    {message.sender === "user" ? "You" : "Vetri AI"}
                  </div>

                  <div className="message-text">{message.text}</div>

                  {message.sender === "ai" && message.metadata && (
                    <div className="ai-message-metadata">
                      <div>
                        <strong>Source:</strong> {message.metadata.source || "Vetri AI"}
                      </div>
                      <div>
                        <strong>Updated:</strong>{" "}
                        {message.metadata.updated_at
                          ? new Date(message.metadata.updated_at).toLocaleString()
                          : "Not available"}
                      </div>
                      <div>
                        <strong>Confidence:</strong>{" "}
                        {message.metadata.confidence || "Not available"}
                      </div>
                    </div>
                  )}
                </div>

                {message.sender === "user" && (
                  <div className="message-avatar user-avatar">
                    <i className="bi bi-person-fill"></i>
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="ai-message-row ai-message-row-left">
                <div className="message-avatar ai-avatar">
                  <img src={AI_BOT_IMAGE} alt="Vetri AI" className="ai-message-bot" />
                </div>
                <div className="ai-message assistant-message typing-message">
                  <div className="message-name">Vetri AI</div>
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

          <div className="ai-chat-input-area">
            <div className="ai-chat-input-wrapper">
              <input
                ref={inputRef}
                type="text"
                className="ai-chat-input"
                placeholder="Ask Vetri AI anything..."
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isLoading || isLoadingConversation}
              />

              <button
                type="button"
                className="ai-send-button"
                onClick={handleSend}
                disabled={!question.trim() || isLoading || isLoadingConversation}
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
        </section>
      </div>
    </div>
  );
}

export default AIChat;