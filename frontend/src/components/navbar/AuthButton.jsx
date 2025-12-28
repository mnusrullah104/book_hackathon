import React from 'react';
import { useAuth } from '@site/src/context/AuthContext';

/**
 * Navbar Auth Button Component
 * Displays Login/Logout based on auth state
 */
export default function AuthButton() {
  const { user, loading, signOut } = useAuth();

  const handleLogout = async () => {
    const result = await signOut();
    if (result.success) {
      window.location.href = '/sign-in';
    }
  };

  const handleLogin = () => {
    window.location.href = '/sign-in';
  };

  // Show nothing while loading auth state
  if (loading) {
    return (
      <div className="navbar-auth-button loading">
        <span className="auth-loader"></span>
      </div>
    );
  }

  if (user) {
    return (
      <button
        className="navbar-auth-button logout"
        onClick={handleLogout}
        title={`Signed in as ${user.email}`}
      >
        <span className="auth-icon">👤</span>
        <span className="auth-text">Logout</span>
      </button>
    );
  }

  return (
    <button
      className="navbar-auth-button login"
      onClick={handleLogin}
    >
      <span className="auth-icon">🔐</span>
      <span className="auth-text">Login</span>
    </button>
  );
}
