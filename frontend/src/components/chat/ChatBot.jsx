import React, { useState, useEffect, useRef, useCallback } from 'react';
import { sendChatMessage } from '@site/src/utils/api';

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
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping, scrollToBottom]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
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
    e?.preventDefault();
    if (!input.trim() || isTyping) return;

    const userMessage = {
      id: crypto.randomUUID(),
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
        id: result.data.response_message_id || crypto.randomUUID(),
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

  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const renderSources = (sources) => {
    if (!sources || sources.length === 0) return null;
    return (
      <div className="chatbot-sources">
        <span className="sources-title">📚 Sources:</span>
        <ul className="sources-list">
          {sources.map((source, idx) => (
            <li key={idx}>
              <a href={source} target="_blank" rel="noopener noreferrer">
                {source.length > 60 ? `${source.substring(0, 60)}...` : source}
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
          <div className="chatbot-avatar">🤖</div>
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
            <div className="welcome-icon">💬</div>
            <h3>Welcome to Robotics AI</h3>
            <p>Ask me about ROS2, Isaac Sim, robotics, or VLA models!</p>
            <div className="quick-prompts">
              <button onClick={() => setInput('What is ROS2?')}>What is ROS2?</button>
              <button onClick={() => setInput('Explain Isaac Sim')}>Explain Isaac Sim</button>
              <button onClick={() => setInput('How do VLA models work?')}>How do VLA models work?</button>
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <div key={msg.id} className={`chatbot-message ${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? '👤' : '🤖'}
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
                <div className="message-avatar">🤖</div>
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
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
          <button onClick={() => setError(null)} className="error-close">×</button>
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
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 2L11 13M22 2L15 22L11 13L2 9L22 2Z" />
              </svg>
            )}
          </button>
        </form>
        <p className="input-hint">Press Enter to send, Shift+Enter for new line</p>
      </div>
    </div>
  );
}
