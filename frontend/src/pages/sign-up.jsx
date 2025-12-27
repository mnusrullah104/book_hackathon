import React from 'react';
import Layout from '@theme/Layout';
import SignUpForm from '@site/src/components/auth/SignUpForm';

export default function SignUpPage() {
  return (
    <Layout title="Sign Up" description="Create a new account">
      <div className="auth-page">
        <SignUpForm />
      </div>
    </Layout>
  );
}
