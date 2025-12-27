import React from 'react';
import { AuthProvider } from '@site/src/components/auth/AuthContext';

// Wrap app with AuthProvider to provide auth context to all pages
export default function Root({ children }) {
  return <AuthProvider>{children}</AuthProvider>;
}
