import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export default function SignInForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { signIn } = useAuth();

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const result = await signIn(email, password);

    if (result.success) {
      // Redirect to chat page
      window.location.href = '/chat';
    } else {
      setError(result.error);
      setLoading(false);
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-form">
        <h1 className="auth-title">Sign In</h1>

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
              Password
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
              'Sign In'
            )}
          </button>
        </form>

        {/* Link to Sign Up */}
        <p className="auth-link">
          Don't have an account?{' '}
          <a href="/sign-up" className="link-primary">
            Sign up
          </a>
        </p>
      </div>
    </div>
  );
}
