import React from 'react';
import Layout from '@theme/Layout';
import BrowserOnly from '@docusaurus/BrowserOnly';

export default function SignUpPage() {
  return (
    <Layout title="Sign Up" description="Create a new account">
      <div className="auth-page">
        <BrowserOnly fallback={<div className="loading-container"><p>Loading...</p></div>}>
          {() => {
            const SignUpForm = require('@site/src/components/auth/SignUpForm').default;
            return <SignUpForm />;
          }}
        </BrowserOnly>
      </div>
    </Layout>
  );
}
