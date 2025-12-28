import React, { useState } from 'react';
import { useAuth } from '@site/src/context/AuthContext';

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
    <div className="auth-container">
      <div className="auth-form">
        <h1 className="auth-title">Create Account</h1>

        <form onSubmit={handleSubmit} className="form-vertical">
          {/* Email Input */}
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="form-input"
              placeholder="you@example.com"
              disabled={loading}
            />
          </div>

          {/* Password Input */}
          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Password (min 8 characters)
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className="form-input"
              placeholder="•••••••••"
              disabled={loading}
            />
          </div>

          {/* Confirm Password Input */}
          <div className="form-group">
            <label htmlFor="confirmPassword" className="form-label">
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength={8}
              className="form-input"
              placeholder="•••••••••"
              disabled={loading}
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary btn-full"
          >
            {loading ? (
              <span className="loading-dots">...</span>
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        {/* Link to Sign In */}
        <p className="auth-link">
          Already have an account?{' '}
          <a href="/sign-in" className="link-primary">
            Sign in
          </a>
        </p>
      </div>
    </div>
  );
}
