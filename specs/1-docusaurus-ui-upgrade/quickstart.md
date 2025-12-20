# Quickstart: Docusaurus UI/UX Upgrade

## Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Git for version control
- Basic knowledge of React and CSS

## Setup Environment

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd BookWriting_Hackathon1
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Switch to the feature branch**:
   ```bash
   git checkout 1-docusaurus-ui-upgrade
   ```

## Development Server

1. **Start the development server**:
   ```bash
   npm run start
   ```

2. **Open your browser** to `http://localhost:3000`

## Key Customization Files

### CSS & Theme Variables
- `src/css/custom.css` - Main CSS overrides and custom styles
- `docusaurus.config.js` - Theme configuration and color modes

### Components
- `src/theme/DocSidebar/` - Custom sidebar with collapsible navigation
- `src/theme/MDXComponents/` - Enhanced components for documentation content
- `src/pages/index.js` - Custom homepage layout

## Making Customizations

### Typography Changes
1. Edit CSS variables in `src/css/custom.css`
2. Use standard web typography (16-18px base font, 1.5-1.6 line height)
3. Ensure scalable headings for visual hierarchy

### Theme Customization
1. Define CSS variables for light/dark themes in `src/css/custom.css`
2. Add theme configuration to `docusaurus.config.js`
3. Test theme switching functionality

### Navigation Enhancements
1. Modify the sidebar component in `src/theme/DocSidebar`
2. Implement collapsible sections for modules
3. Add active state indicators

## Testing Changes

1. **Visual Testing**:
   - Check all pages in both light and dark modes
   - Verify responsive behavior on different screen sizes
   - Test navigation functionality

2. **Performance Testing**:
   - Verify page load times remain under 3 seconds
   - Check that bundle size hasn't increased significantly

3. **Accessibility Testing**:
   - Verify WCAG 2.1 AA compliance
   - Test keyboard navigation
   - Check color contrast ratios

## Building for Production

```bash
npm run build
```

## Deploying

```bash
npm run deploy
```

## Troubleshooting

- If styles don't appear: Clear browser cache and restart development server
- If navigation doesn't work: Check that sidebar configuration matches documentation structure
- If theme switching fails: Verify CSS variables are properly defined