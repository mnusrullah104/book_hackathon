import React, { createContext, useContext, useState, useEffect } from 'react';

// Backend API URL
const API_URL = process.env.API_URL || 'http://localhost:7860/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    async function checkSession() {
      try {
        // Ping protected endpoint to validate session
        const response = await fetch(`${API_URL}/auth/verify`, {
          method: 'GET',
          credentials: 'include',
        });

        if (response.ok) {
          const data = await response.json();
          setUser(data.user);
        } else {
          setUser(null);
        }
        setLoading(false);
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
