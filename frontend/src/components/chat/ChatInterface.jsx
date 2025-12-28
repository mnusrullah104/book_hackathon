import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';

// Backend API URL
const API_URL = process.env.API_URL || 'http://localhost:7860/api';

export default function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const { user, signOut } = useAuth();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function sendMessage(e) {
    e.preventDefault();
    setError(null);
    if (!input.trim()) return;

    const userMessage = {
      id: crypto.randomUUID(),
      sender: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ message: userMessage.content }),
      });

      if (response.status === 401) {
        setError('Session expired. Please sign in again.');
        setTimeout(() => { window.location.href = '/sign-in'; }, 2000);
        return;
      }
      if (response.status === 429) {
        setError('Rate limit exceeded. Please wait.');
        setLoading(false);
        return;
      }
      if (response.status === 503) {
        setError('Chat service unavailable. Try again later.');
        setLoading(false);
        return;
      }
      if (!response.ok) throw new Error('Failed to send message');

      const data = await response.json();
      const systemMessage = {
        id: data.response_message_id || crypto.randomUUID(),
        sender: 'system',
        content: data.response,
        sources: data.sources || [],
        timestamp: data.timestamp || new Date().toISOString(),
      };
      setMessages((prev) => [...prev, systemMessage]);
    } catch (err) {
      setError('Failed to send message. Please try again.');
      console.error('Chat error:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleSignOut() {
    const result = await signOut();
    if (result.success) window.location.href = '/sign-in';
  }

  function renderSources(sources) {
    if (!sources || sources.length === 0) return null;
    return (
      <div className="message-sources">
        <div className="sources-label">Sources:</div>
        <ul className="sources-list">
          {sources.map((source, idx) => (
            <li key={idx}>
              <a href={source} target="_blank" rel="noopener noreferrer">
                {source.length > 50 ? source.substring(0, 50) + '...' : source}
              </a>
            </li>
          ))}
        </ul>
      </div>
    );
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="user-info"><span className="user-email">{user?.email}</span></div>
        <button onClick={handleSignOut} className="btn btn-secondary btn-sm">Sign Out</button>
      </div>

      <div className="chat-messages" ref={messagesEndRef}>
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">💬</div>
            <p>Ask about ROS2, Isaac Sim, robotics, or VLA models</p>
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className={`message-bubble ${msg.sender === 'user' ? 'user' : 'system'}`}>
              <div className="message-sender">{msg.sender === 'user' ? 'You' : 'AI'}</div>
              <div className="message-content">{msg.content}</div>
              {msg.sender === 'system' && renderSources(msg.sources)}
              <div className="message-time">
                {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          ))
        )}
      </div>

      {error && (<div className="error-toast"><span className="error-icon">⚠️</span>{error}</div>)}

      <div className="chat-input-container">
        <form onSubmit={sendMessage} className="chat-input-form">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about ROS2, Isaac Sim, robotics, or VLA..."
            className="chat-textarea"
            disabled={loading}
            rows={1}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(e); }
            }}
          />
          <button type="submit" disabled={loading || !input.trim()} className={`btn-send ${loading ? 'btn-loading' : ''}`}>
            {loading ? <span className="loading-dots">...</span> : <span className="send-icon">➤</span>}
          </button>
        </form>
      </div>
    </div>
  );
}
