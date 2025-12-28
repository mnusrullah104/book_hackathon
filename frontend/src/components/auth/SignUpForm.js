import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import Link from '@docusaurus/Link';

export default function SignUpForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { register, signIn } = useAuth();

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Validate password length
    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);

    const result = await register(email, password);

    if (result.success) {
      // Registration successful, automatically sign in
      const signInResult = await signIn(email, password);
      if (signInResult.success) {
        window.location.href = '/chat';
      } else {
        // Redirect to sign in page
        window.location.href = '/sign-in';
      }
    } else {
      setError(result.error);
      setLoading(false);
    }
  }

  return (
    <div style={{
      maxWidth: '400px',
      margin: '2rem auto',
      padding: '2rem',
      border: '1px solid var(--ifm-color-emphasis-300)',
      borderRadius: '8px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    }}>
      <h1 style={{ marginBottom: '1.5rem', textAlign: 'center' }}>
        Create Account
      </h1>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {/* Email Input */}
        <div>
          <label htmlFor="email" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid var(--ifm-color-emphasis-300)',
              borderRadius: '4px',
              fontSize: '1rem',
            }}
            placeholder="you@example.com"
          />
        </div>

        {/* Password Input */}
        <div>
          <label htmlFor="password" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
            Password (min 8 characters)
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid var(--ifm-color-emphasis-300)',
              borderRadius: '4px',
              fontSize: '1rem',
            }}
            placeholder="•••••••••••"
          />
        </div>

        {/* Confirm Password Input */}
        <div>
          <label htmlFor="confirmPassword" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
            Confirm Password
          </label>
          <input
            id="confirmPassword"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            minLength={8}
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid var(--ifm-color-emphasis-300)',
              borderRadius: '4px',
              fontSize: '1rem',
            }}
            placeholder="•••••••••••"
          />
        </div>

        {/* Error Message */}
        {error && (
          <div style={{
            padding: '0.75rem',
            backgroundColor: 'var(--ifm-color-danger-contrast-background)',
            color: 'var(--ifm-color-danger-contrast-foreground)',
            borderRadius: '4px',
            fontSize: '0.875rem',
          }}>
            {error}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          style={{
            padding: '0.875rem',
            backgroundColor: 'var(--ifm-color-primary)',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontSize: '1rem',
            fontWeight: 600,
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1,
          }}
        >
          {loading ? 'Creating account...' : 'Create Account'}
        </button>
      </form>

      {/* Link to Sign In */}
      <p style={{ textAlign: 'center', marginTop: '1rem', fontSize: '0.875rem' }}>
        Already have an account?{' '}
        <Link to="/sign-in" style={{ color: 'var(--ifm-color-primary)', fontWeight: 600 }}>
          Sign in
        </Link>
      </p>
    </div>
  );
}
