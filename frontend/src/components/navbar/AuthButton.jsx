import React, { useState, useEffect } from 'react';
import { API_URL } from '@site/src/utils/api';

/**
 * Navbar Auth Button Component
 * Self-contained auth state management to avoid SSR issues
 */
export default function AuthButton() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showDropdown, setShowDropdown] = useState(false);

  // Check auth status on mount
  useEffect(() => {
    let mounted = true;

    async function checkAuth() {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);

        const response = await fetch(`${API_URL}/auth/verify`, {
          method: 'GET',
          credentials: 'include',
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (mounted && response.ok) {
          const data = await response.json();
          setUser(data.user);
        }
      } catch (err) {
        // Silently fail - user is not logged in
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    // Small delay to ensure browser is ready
    const timer = setTimeout(checkAuth, 100);

    // Also set a fallback to show button after 2 seconds
    const fallbackTimer = setTimeout(() => {
      if (mounted) setLoading(false);
    }, 2000);

    return () => {
      mounted = false;
      clearTimeout(timer);
      clearTimeout(fallbackTimer);
    };
  }, []);

  const handleLogout = async () => {
    setShowDropdown(false);
    try {
      await fetch(`${API_URL}/auth/sign-out`, {
        method: 'POST',
        credentials: 'include',
      });
    } catch (err) {
      // Continue with logout even if API fails
    }
    setUser(null);
    window.location.href = '/';
  };

  const handleLogin = () => {
    window.location.href = '/sign-in';
  };

  const handleSignUp = () => {
    window.location.href = '/sign-up';
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest('.navbar-auth-container')) {
        setShowDropdown(false);
      }
    };

    if (showDropdown) {
      document.addEventListener('click', handleClickOutside);
    }

    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, [showDropdown]);

  // Show loading state briefly
  if (loading) {
    return (
      <div className="navbar-auth-button loading">
        <span className="auth-loader"></span>
      </div>
    );
  }

  // User is logged in - show user icon with dropdown
  if (user) {
    return (
      <div className="navbar-auth-container logged-in">
        <button
          type="button"
          className="navbar-auth-button logout"
          onClick={() => setShowDropdown(!showDropdown)}
          title={user.email ? 'Signed in as ' + user.email : 'Account menu'}
        >
          <span className="auth-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </span>
          <span className="auth-text">{user.email?.split('@')[0] || 'Account'}</span>
          <svg className="dropdown-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </button>
        {showDropdown && (
          <div className="auth-dropdown">
            <div className="auth-dropdown-header">
              <span className="dropdown-email">{user.email}</span>
            </div>
            <button type="button" className="auth-dropdown-item" onClick={handleLogout}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                <polyline points="16 17 21 12 16 7"></polyline>
                <line x1="21" y1="12" x2="9" y2="12"></line>
              </svg>
              Sign Out
            </button>
          </div>
        )}
      </div>
    );
  }

  // User is not logged in - show Sign In and Sign Up buttons
  return (
    <div className="navbar-auth-container logged-out">
      <button
        type="button"
        className="navbar-auth-button sign-up"
        onClick={handleSignUp}
      >
        <span className="auth-text">Sign Up</span>
      </button>
      <button
        type="button"
        className="navbar-auth-button login"
        onClick={handleLogin}
      >
        <span className="auth-text">Sign In</span>
      </button>
    </div>
  );
}
