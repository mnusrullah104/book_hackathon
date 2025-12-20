import React from 'react';
import OriginalMDXComponents from '@theme-original/MDXComponents';
import CodeBlock from '@theme/CodeBlock';

// Enhanced CodeBlock component with copy functionality
const EnhancedCodeBlock = (props) => {
  return (
    <div style={{ position: 'relative' }}>
      <CodeBlock {...props} />
    </div>
  );
};

// Custom components for enhanced content presentation
const CustomBlockquote = (props) => {
  return (
    <blockquote
      style={{
        borderLeft: '4px solid var(--ifm-color-primary)',
        paddingLeft: '1rem',
        marginLeft: '0',
        color: 'var(--ifm-color-emphasis-800)',
        fontStyle: 'italic',
      }}
      {...props}
    />
  );
};

// Export all components
const MDXComponents = {
  ...OriginalMDXComponents,
  pre: (props) => <EnhancedCodeBlock {...props} />,
  blockquote: CustomBlockquote,
};

export default MDXComponents;