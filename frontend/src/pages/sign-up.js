import React from 'react';
import Layout from '@theme/Layout';
import SignUpForm from '@site/src/components/auth/SignUpForm';

export default function SignUpPage() {
  return (
    <Layout title="Sign Up" description="Create a new account">
      <main style={{
        minHeight: 'calc(100vh - var(--ifm-navbar-height))',
        display: 'flex',
        alignItems: 'center',
        padding: '2rem 1rem',
      }}>
        <SignUpForm />
      </main>
    </Layout>
  );
}
