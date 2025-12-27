import React, { createContext, useContext, useState, useEffect } from 'react';

// API URL from environment variable (will be configured in docusaurus.config.js)
const API_URL = process.env.API_URL || 'http://localhost:7860/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    async function checkSession() {
      try {
        // Make a request to backend to check if session is valid
        // This will trigger auth middleware which validates the cookie
        const response = await fetch(`${API_URL}/chat/message`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ message: 'ping' }),
        });

        if (response.ok) {
          // Session is valid, user is authenticated
          // We'll extract user info from a separate endpoint if needed
          setLoading(false);
        } else if (response.status === 401) {
          // No valid session
          setUser(null);
          setLoading(false);
        } else {
          setLoading(false);
        }
      } catch (error) {
        console.error('Session check error:', error);
        setUser(null);
        setLoading(false);
      }
    }

    checkSession();
  }, []);

  async function register(email, password) {
    try {
      const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Registration failed');
      }

      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async function signIn(email, password) {
    try {
      const response = await fetch(`${API_URL}/auth/sign-in`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Sign in failed');
      }

      // Set user state
      setUser({ id: data.user_id, email: data.email });

      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async function signOut() {
    try {
      const response = await fetch(`${API_URL}/auth/sign-out`, {
        method: 'POST',
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Sign out failed');
      }

      setUser(null);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  const value = {
    user,
    loading,
    register,
    signIn,
    signOut,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
