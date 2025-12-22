import React, { createContext, useContext } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import { useColorMode } from '@docusaurus/theme-common';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  // Return Docusaurus theme if context not available
  if (!context) {
    try {
      const { colorMode, setColorMode } = useColorMode();
      return {
        theme: colorMode,
        toggleTheme: () => setColorMode(colorMode === 'light' ? 'dark' : 'light'),
        setTheme: setColorMode,
      };
    } catch {
      return {
        theme: 'light',
        toggleTheme: () => {},
        setTheme: () => {},
      };
    }
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  // Use Docusaurus's built-in color mode hook
  const { colorMode, setColorMode } = useColorMode();

  const toggleTheme = () => {
    setColorMode(colorMode === 'light' ? 'dark' : 'light');
  };

  const value = {
    theme: colorMode,
    toggleTheme,
    setTheme: setColorMode,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};