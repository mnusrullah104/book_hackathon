import React from 'react';
import Layout from '@theme/Layout';
import SignInForm from '@site/src/components/auth/SignInForm';

export default function SignInPage() {
  return (
    <Layout title="Sign In" description="Sign in to your account">
      <div className="auth-page">
        <SignInForm />
      </div>
    </Layout>
  );
}
