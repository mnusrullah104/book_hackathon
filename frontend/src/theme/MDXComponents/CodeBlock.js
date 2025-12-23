import React, { useState, useRef, useEffect } from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';
import useIsBrowser from '@docusaurus/useIsBrowser';

const CopyButton = ({ code }) => {
  const [copied, setCopied] = useState(false);
  const [supported, setSupported] = useState(true);

  useEffect(() => {
    setSupported(!!navigator.clipboard);
  }, []);

  if (!supported) {
    return null;
  }

  const handleCopyCode = () => {
    navigator.clipboard.writeText(code).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <button
      type="button"
      aria-label={copied ? 'Copied' : 'Copy'}
      title={copied ? 'Copied' : 'Copy to clipboard'}
      onClick={handleCopyCode}
      style={{
        position: 'absolute',
        right: '8px',
        top: '8px',
        width: '2rem',
        height: '2rem',
        borderRadius: '4px',
        background: 'var(--ifm-color-emphasis-200)',
        border: 'none',
        cursor: 'pointer',
        opacity: 0.5,
        transition: 'opacity 0.2s ease',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '0.875rem',
      }}
      onMouseEnter={(e) => (e.currentTarget.style.opacity = '1')}
      onMouseLeave={(e) => (e.currentTarget.style.opacity = '0.5')}
    >
      {copied ? (
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 16.17L4.83 12L3.41 13.41L9 19L21 7L19.59 5.59L9 16.17Z" fill="currentColor" />
        </svg>
      ) : (
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M19 21H8V7H19M19 5H8C6.89 5 6 5.89 6 7V21C6 22.1 6.9 23 8 23H19C20.1 23 21 22.1 21 21V7C21 5.9 20.1 5 19 5M16 1H4C2.89 1 2 1.89 2 3V17H4V3H16V1Z" fill="currentColor" />
        </svg>
      )}
    </button>
  );
};

const EnhancedCodeBlock = (props) => {
  const { children, ...rest } = props;
  const isBrowser = useIsBrowser();
  const ref = useRef(null);

  const code = isBrowser ? ref.current?.textContent || '' : '';

  return (
    <div style={{ position: 'relative' }}>
      <div ref={ref}>
        {children}
      </div>
      {code && <CopyButton code={code} />}
    </div>
  );
};

export default EnhancedCodeBlock;