import React from 'react';
import { ThemeProvider } from '../contexts/ThemeContext';

export default function Root({ children }) {
  return <ThemeProvider>{children}</ThemeProvider>;
}
