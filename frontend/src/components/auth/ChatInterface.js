import React, { useState, useEffect } from 'react';

// API URL from environment variable
const API_URL = process.env.API_URL || 'http://localhost:7860/api';

export default function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Critical: ensures session cookie is sent
        body: JSON.stringify({ message: userMessage.content }),
      });

      if (response.status === 401) {
        setError('Session expired. Please sign in again.');
        setTimeout(() => {
          window.location.href = '/sign-in';
        }, 2000);
        return;
      }

      if (response.status === 429) {
        setError('Rate limit exceeded. Please wait before sending another message.');
        setLoading(false);
        return;
      }

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();

      const systemMessage = {
        id: data.response_message_id || crypto.randomUUID(),
        sender: 'system',
        content: data.response,
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

  return (
    <div style={{
      backgroundColor: 'var(--ifm-color-background)',
      minHeight: '100vh',
      padding: '2rem 1rem',
    }}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: '2rem' }}>
          <h2 style={{ marginBottom: '0.5rem', fontSize: '2rem' }}>
            RAG Chat
          </h2>
          <p style={{ color: 'var(--ifm-color-emphasis-500)', fontSize: '1rem' }}>
            Authenticated chat interface
          </p>
        </div>

        {/* Chat Messages */}
        <div style={{
          height: '500px',
          overflowY: 'auto',
          marginBottom: '2rem',
          padding: '1rem',
          backgroundColor: 'var(--ifm-color-surface)',
          borderRadius: '8px',
          border: '1px solid var(--ifm-color-emphasis-300)',
        }}>
          {messages.length === 0 ? (
            <div style={{
              textAlign: 'center',
              color: 'var(--ifm-color-emphasis-500)',
              padding: '2rem',
            }}>
              Send a message to start chatting with the RAG system.
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                style={{
                  marginBottom: '1rem',
                  display: 'flex',
                  flexDirection: msg.sender === 'user' ? 'row-reverse' : 'row',
                }}
              >
                <div style={{
                  maxWidth: '70%',
                  padding: '0.75rem 1rem',
                  borderRadius: '8px',
                  backgroundColor: msg.sender === 'user'
                    ? 'var(--ifm-color-primary)'
                    : 'var(--ifm-color-emphasis-100)',
                  color: msg.sender === 'user' ? 'white' : 'var(--ifm-color-text)',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                }}>
                  <div style={{
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    marginBottom: '0.25rem',
                    opacity: 0.9,
                  }}>
                    {msg.sender === 'user' ? 'You' : 'System'}
                  </div>
                  <div style={{ fontSize: '1rem', lineHeight: 1.5 }}>
                    {msg.content}
                  </div>
                  <div style={{
                    fontSize: '0.75rem',
                    opacity: 0.7,
                    marginTop: '0.5rem',
                  }}>
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div style={{
            marginBottom: '2rem',
            padding: '1rem',
            backgroundColor: 'var(--ifm-color-danger-contrast-background)',
            color: 'var(--ifm-color-danger-contrast-foreground)',
            borderRadius: '8px',
            fontSize: '0.875rem',
          }}>
            {error}
          </div>
        )}

        {/* Input Form */}
        <form onSubmit={sendMessage} style={{
          border: '1px solid var(--ifm-color-emphasis-300)',
          borderRadius: '8px',
          padding: '1rem',
          backgroundColor: 'var(--ifm-color-surface)',
        }}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message here..."
            style={{
              width: '100%',
              minHeight: '100px',
              padding: '0.75rem',
              border: '1px solid var(--ifm-color-emphasis-300)',
              borderRadius: '4px',
              fontSize: '1rem',
              fontFamily: 'inherit',
              resize: 'vertical',
            }}
            disabled={loading}
            rows={4}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            style={{
              marginTop: '1rem',
              padding: '0.75rem 2rem',
              backgroundColor: 'var(--ifm-color-primary)',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              fontSize: '1rem',
              fontWeight: 600,
              cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
              opacity: loading || !input.trim() ? 0.6 : 1,
            }}
          >
            {loading ? 'Sending...' : 'Send Message'}
          </button>
        </form>
      </div>
    </div>
  );
}
