# Quickstart: Textbook UI Design Development

**Feature**: 003-textbook-ui-design
**Date**: 2025-12-21

## Prerequisites

- Node.js 18.0 or higher
- npm or yarn
- Git
- Modern browser (Chrome, Firefox, Safari, Edge)

## Setup

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/mnusrullah104/BookWriting_Hackathon1.git
cd BookWriting_Hackathon1

# Checkout the feature branch
git checkout 003-textbook-ui-design

# Install dependencies
npm install
```

### 2. Start Development Server

```bash
npm start
```

This will start the Docusaurus development server at `http://localhost:3000`.

### 3. Build for Production

```bash
npm run build
```

Output will be in the `build/` directory.

## Project Structure for UI Development

```text
src/
├── css/
│   └── custom.css        # ← PRIMARY: All CSS customizations
├── theme/
│   ├── DocSidebar/       # Sidebar customizations
│   ├── MDXComponents/    # MDX component overrides
│   └── Root.js           # Theme provider
├── components/           # Reusable components
├── contexts/             # React contexts (theme state)
└── pages/                # Custom pages

docs/                     # Book content (for testing UI)
```

## Key Files to Modify

| File | Purpose | When to Modify |
|------|---------|----------------|
| `src/css/custom.css` | All visual styling | Typography, colors, spacing, responsive |
| `src/theme/DocSidebar/index.js` | Sidebar component | Navigation behavior |
| `docusaurus.config.js` | Site configuration | Theme settings, navbar |

## Development Workflow

### Making CSS Changes

1. Open `src/css/custom.css`
2. Make changes to relevant section (variables, components, responsive)
3. Save - hot reload will apply changes
4. Test in both light and dark mode
5. Test responsive at multiple breakpoints

### Testing Responsive Design

Use browser DevTools (F12) → Device Toolbar:

| Breakpoint | Width | Test Focus |
|------------|-------|------------|
| Mobile S | 320px | Minimum viable layout |
| Mobile L | 425px | Typical phone |
| Tablet | 768px | Sidebar collapse point |
| Laptop | 1024px | Full desktop layout |
| Desktop | 1440px | Large screens |
| 4K | 2560px | Maximum width |

### Testing Accessibility

1. **Lighthouse Audit**:
   ```bash
   # Build and serve
   npm run build
   npm run serve
   ```
   Open Chrome DevTools → Lighthouse → Run Accessibility audit

2. **Keyboard Navigation**:
   - Tab through all interactive elements
   - Verify focus states are visible
   - Test sidebar expand/collapse with keyboard

3. **Color Contrast**:
   - Use browser extension (e.g., WAVE, axe)
   - Check text on all background colors
   - Verify in both light and dark modes

## CSS Variable Reference

### Colors (Light Theme)

```css
--ifm-color-primary: #8a2be2;        /* Main purple */
--ifm-color-primary-dark: #7a1ad2;   /* Hover states */
--ifm-color-primary-light: #9a46e8;  /* Highlights */
```

### Colors (Dark Theme)

```css
--ifm-color-primary: #9a46e8;        /* Lighter purple */
--ifm-background-color: #1b1b1d;     /* Page background */
```

### Typography

```css
--ifm-font-size-base: 18px;          /* Body text */
--ifm-line-height-base: 1.6;         /* Reading comfort */
--ifm-heading-line-height: 1.3;      /* Headings */
```

### Spacing

```css
--ifm-spacing-md: 1rem;              /* Standard gap */
--ifm-spacing-lg: 1.5rem;            /* Section spacing */
--ifm-spacing-xl: 2rem;              /* Large gaps */
```

## Common Tasks

### Change Primary Color

```css
:root {
  --ifm-color-primary: #NEW_COLOR;
  --ifm-color-primary-dark: /* 10% darker */;
  --ifm-color-primary-light: /* 10% lighter */;
}
```

### Adjust Reading Width

```css
.markdown {
  max-width: 75ch; /* 65-80ch recommended */
}
```

### Modify Sidebar Width

```css
:root {
  --doc-sidebar-width: 300px;
}
```

### Style Code Blocks

```css
.prism-code {
  /* Custom code block styling */
}
```

## Deployment

The site deploys automatically to Vercel on push to main branch.

Manual deployment:
```bash
npm run build
# Deploy build/ directory to your hosting
```

## Troubleshooting

### Hot reload not working

```bash
npm run clear
npm start
```

### CSS changes not applying

1. Hard refresh (Ctrl+Shift+R)
2. Clear browser cache
3. Check CSS specificity

### Build errors

```bash
npm run clear
rm -rf node_modules
npm install
npm run build
```

## Resources

- [Docusaurus Styling Guide](https://docusaurus.io/docs/styling-layout)
- [Infima CSS Framework](https://infima.dev/)
- [Prism Themes](https://prismjs.com/)
- [WCAG Color Contrast Checker](https://webaim.org/resources/contrastchecker/)
