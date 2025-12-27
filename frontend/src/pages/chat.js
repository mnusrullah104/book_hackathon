import React, { useEffect } from 'react';
import Layout from '@theme/Layout';
import { useAuth } from '@site/src/components/auth/AuthContext';
import ChatInterface from '@site/src/components/auth/ChatInterface';

export default function ChatPage() {
  const { user, loading, signOut } = useAuth();

  // Redirect to sign-in if not authenticated
  useEffect(() => {
    if (!loading && !user) {
      window.location.href = '/sign-in';
    }
  }, [user, loading]);

  // Show loading state
  if (loading) {
    return (
      <Layout title="Loading...">
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: 'calc(100vh - var(--ifm-navbar-height))',
        }}>
          <div style={{ fontSize: '1.25rem', color: 'var(--ifm-color-emphasis-500)' }}>
            Loading...
          </div>
        </div>
      </Layout>
    );
  }

  // Don't render if no user (will redirect)
  if (!user) {
    return null;
  }

  async function handleSignOut() {
    const result = await signOut();
    if (result.success) {
      window.location.href = '/sign-in';
    }
  }

  return (
    <Layout
      title="Chat"
      description="Authenticated RAG chat interface"
      noFooter
    >
      <main>
        {/* Header */}
        <header style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '2rem',
          padding: '1rem',
          backgroundColor: 'var(--ifm-color-surface)',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', margin: 0 }}>
              Chat
            </h1>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span style={{ fontSize: '0.875rem', color: 'var(--ifm-color-emphasis-500)' }}>
              {user.email}
            </span>
            <button
              onClick={handleSignOut}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: 'var(--ifm-color-emphasis-100)',
                color: 'var(--ifm-color-emphasis-700)',
                border: '1px solid var(--ifm-color-emphasis-300)',
                borderRadius: '4px',
                fontSize: '0.875rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
              onMouseOver={(e) => {
                e.target.style.backgroundColor = 'var(--ifm-color-emphasis-200)';
              }}
              onMouseOut={(e) => {
                e.target.style.backgroundColor = 'var(--ifm-color-emphasis-100)';
              }}
            >
              Sign Out
            </button>
          </div>
        </header>

        {/* Chat Interface */}
        <ChatInterface />
      </main>
    </Layout>
  );
}
