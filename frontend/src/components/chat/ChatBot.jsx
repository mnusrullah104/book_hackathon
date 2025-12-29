import React, { useState, useEffect, useRef, useCallback } from 'react';
import { API_URL, sendChatMessage } from '@site/src/utils/api';

// Generate unique ID (fallback for browsers without crypto.randomUUID)
function generateId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return 'msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
}

/**
 * Professional ChatBot UI Component
 * Features: Chat bubbles, typing indicator, timestamps, sources, responsive design
 */
export default function ChatBot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll to bottom when messages change
  const scrollToBottom = useCallback(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping, scrollToBottom]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const newHeight = Math.min(textareaRef.current.scrollHeight, 120);
      textareaRef.current.style.height = newHeight + 'px';
    }
  }, [input]);

  // Clear error after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const handleSend = async (e) => {
    if (e) e.preventDefault();
    if (!input.trim() || isTyping) return;

    const userMessage = {
      id: generateId(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setError(null);
    setIsTyping(true);

    const result = await sendChatMessage(userMessage.content);

    setIsTyping(false);

    if (result.success) {
      const botMessage = {
        id: result.data.response_message_id || generateId(),
        role: 'assistant',
        content: result.data.response,
        sources: result.data.sources || [],
        timestamp: new Date(result.data.timestamp || Date.now()),
      };
      setMessages((prev) => [...prev, botMessage]);
    } else {
      setError(result.error);
      if (result.status === 401) {
        setTimeout(() => {
          window.location.href = '/sign-in';
        }, 2000);
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleQuickPrompt = (prompt) => {
    setInput(prompt);
  };

  const formatTime = (date) => {
    try {
      return new Date(date).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return '';
    }
  };

  const renderSources = (sources) => {
    if (!sources || sources.length === 0) return null;
    return (
      <div className="chatbot-sources">
        <span className="sources-title">Sources:</span>
        <ul className="sources-list">
          {sources.map((source, idx) => (
            <li key={idx}>
              <a href={source} target="_blank" rel="noopener noreferrer">
                {source.length > 60 ? source.substring(0, 60) + '...' : source}
              </a>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <div className="chatbot-container">
      {/* Chat Header */}
      <div className="chatbot-header">
        <div className="chatbot-header-info">
          <div className="chatbot-avatar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z"></path>
              <circle cx="8" cy="14" r="1"></circle>
              <circle cx="12" cy="14" r="1"></circle>
              <circle cx="16" cy="14" r="1"></circle>
            </svg>
          </div>
          <div className="chatbot-header-text">
            <h3>Robotics AI Assistant</h3>
            <span className="chatbot-status">
              <span className="status-dot"></span>
              {isTyping ? 'Typing...' : 'Online'}
            </span>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="chatbot-messages">
        {messages.length === 0 ? (
          <div className="chatbot-welcome">
            <div className="welcome-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
            </div>
            <h3>Welcome to Robotics AI</h3>
            <p>Ask me about ROS2, Isaac Sim, robotics, or VLA models!</p>
            <div className="quick-prompts">
              <button type="button" onClick={() => handleQuickPrompt('What is ROS2?')}>
                What is ROS2?
              </button>
              <button type="button" onClick={() => handleQuickPrompt('Explain Isaac Sim')}>
                Explain Isaac Sim
              </button>
              <button type="button" onClick={() => handleQuickPrompt('How do VLA models work?')}>
                How do VLA models work?
              </button>
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <div key={msg.id} className={'chatbot-message ' + msg.role}>
                <div className="message-avatar">
                  {msg.role === 'user' ? (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                      <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                  ) : (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z"></path>
                    </svg>
                  )}
                </div>
                <div className="message-wrapper">
                  <div className="message-bubble">
                    <div className="message-content">{msg.content}</div>
                    {msg.role === 'assistant' && renderSources(msg.sources)}
                  </div>
                  <div className="message-timestamp">{formatTime(msg.timestamp)}</div>
                </div>
              </div>
            ))}

            {/* Typing Indicator */}
            {isTyping && (
              <div className="chatbot-message assistant">
                <div className="message-avatar">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z"></path>
                  </svg>
                </div>
                <div className="message-wrapper">
                  <div className="message-bubble typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Error Toast */}
      {error && (
        <div className="chatbot-error">
          <span className="error-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
          </span>
          <span>{error}</span>
          <button type="button" onClick={() => setError(null)} className="error-close">×</button>
        </div>
      )}

      {/* Input Area */}
      <div className="chatbot-input-area">
        <form onSubmit={handleSend} className="chatbot-form">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            disabled={isTyping}
            rows={1}
          />
          <button
            type="submit"
            disabled={isTyping || !input.trim()}
            className={isTyping ? 'sending' : ''}
          >
            {isTyping ? (
              <span className="send-loader"></span>
            ) : (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            )}
          </button>
        </form>
        <p className="input-hint">Press Enter to send, Shift+Enter for new line</p>
      </div>
    </div>
  );
}
