import React from 'react';
import Layout from '@theme/Layout';
import BrowserOnly from '@docusaurus/BrowserOnly';
import '@site/src/css/chatbot.css';

function ChatPageContent() {
  const { useAuth } = require('@site/src/context/AuthContext');
  const ChatBot = require('@site/src/components/chat/ChatBot').default;

  const { user, loading } = useAuth();

  // Redirect to sign-in if not authenticated
  React.useEffect(() => {
    if (!loading && !user) {
      window.location.href = '/sign-in';
    }
  }, [user, loading]);

  // Show loading state
  if (loading) {
    return (
      <div className="chat-loading">
        <div className="chat-loading-spinner"></div>
        <p>Loading chat...</p>
      </div>
    );
  }

  // Don't render if no user (will redirect)
  if (!user) {
    return (
      <div className="chat-loading">
        <p>Redirecting to sign in...</p>
      </div>
    );
  }

  return <ChatBot />;
}

export default function ChatPage() {
  return (
    <Layout
      title="AI Chat"
      description="AI-powered robotics assistant"
      noFooter
    >
      <BrowserOnly fallback={
        <div className="chat-loading">
          <div className="chat-loading-spinner"></div>
          <p>Loading chat...</p>
        </div>
      }>
        {() => <ChatPageContent />}
      </BrowserOnly>
    </Layout>
  );
}
