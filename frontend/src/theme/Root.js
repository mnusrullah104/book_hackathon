import React from 'react';
import AuthProvider from '../context/AuthContext';

// Wrap Docusaurus app with AuthProvider to provide auth context to all pages
export default function Root({ children }) {
  return <AuthProvider>{children}</AuthProvider>;
}
