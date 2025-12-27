import React from 'react';
import Layout from '@theme/Layout';
import SignInForm from '@site/src/components/auth/SignInForm';

export default function SignInPage() {
  return (
    <Layout title="Sign In" description="Sign in to your account">
      <main style={{
        minHeight: 'calc(100vh - var(--ifm-navbar-height))',
        display: 'flex',
        alignItems: 'center',
        padding: '2rem 1rem',
      }}>
        <SignInForm />
      </main>
    </Layout>
  );
}
