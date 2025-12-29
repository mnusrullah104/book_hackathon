import React from 'react';
import Layout from '@theme/Layout';
import BrowserOnly from '@docusaurus/BrowserOnly';

// Import styles
import '@site/src/css/chatbot.css';

// ChatBot component loaded only on client side
function ChatBotLoader() {
  const [Component, setComponent] = React.useState(null);

  React.useEffect(() => {
    // Dynamically import ChatBot to avoid SSR issues
    import('@site/src/components/chat/ChatBot').then((mod) => {
      setComponent(() => mod.default);
    });
  }, []);

  if (!Component) {
    return (
      <div className="chat-loading">
        <div className="chat-loading-spinner"></div>
        <p>Loading chat...</p>
      </div>
    );
  }

  return <Component />;
}

export default function ChatPage() {
  return (
    <Layout
      title="AI Chat"
      description="AI-powered robotics assistant"
      noFooter
    >
      <BrowserOnly
        fallback={
          <div className="chat-loading">
            <div className="chat-loading-spinner"></div>
            <p>Loading chat...</p>
          </div>
        }
      >
        {() => <ChatBotLoader />}
      </BrowserOnly>
    </Layout>
  );
}
