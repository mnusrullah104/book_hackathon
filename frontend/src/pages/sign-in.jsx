import React from 'react';
import Layout from '@theme/Layout';
import BrowserOnly from '@docusaurus/BrowserOnly';

export default function SignInPage() {
  return (
    <Layout title="Sign In" description="Sign in to your account">
      <div className="auth-page">
        <BrowserOnly fallback={<div className="loading-container"><p>Loading...</p></div>}>
          {() => {
            const SignInForm = require('@site/src/components/auth/SignInForm').default;
            return <SignInForm />;
          }}
        </BrowserOnly>
      </div>
    </Layout>
  );
}
