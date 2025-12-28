import React, { useEffect } from 'react';
import Layout from '@theme/Layout';
import { useAuth } from '@site/src/context/AuthContext';
import ChatInterface from '@site/src/components/chat/ChatInterface';

export default function ChatPage() {
  const { user, loading } = useAuth();

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
        <div className="loading-container">
          <div className="loading-spinner">
            <span className="loading-dots">...</span>
          </div>
          <p>Loading...</p>
        </div>
      </Layout>
    );
  }

  // Don't render if no user (will redirect)
  if (!user) {
    return null;
  }

  return (
    <Layout
      title="Chat"
      description="AI-powered chat interface"
      noFooter
    >
      <div className="chat-page">
        <ChatInterface />
      </div>
    </Layout>
  );
}
