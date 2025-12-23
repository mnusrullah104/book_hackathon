# Quickstart: Frontend Refactor & UI Fix (Book-Only Phase)

**Feature**: 006-frontend-book-refactor
**Date**: 2025-12-22

## Prerequisites

- Node.js 18+
- npm or yarn
- Git

## New Development Workflow

### After Migration

```bash
# Clone the repository
git clone <repo-url>
cd BookWriting_Hackathon1

# Navigate to frontend
cd frontendBook

# Install dependencies
npm install

# Start development server
npm start
```

Opens at `http://localhost:3000`

### Build for Production

```bash
cd frontendBook
npm run build
npm run serve  # Preview production build
```

## Folder Structure After Migration

```
BookWriting_Hackathon1/
├── frontendBook/           # Docusaurus site
│   ├── docs/               # Markdown content
│   ├── src/
│   │   ├── css/custom.css  # Theme styles
│   │   └── pages/          # Custom pages
│   ├── static/             # Images, assets
│   ├── docusaurus.config.js
│   ├── sidebars.js
│   └── package.json
├── backend/                # Empty (future backend)
├── specs/                  # Feature specifications
├── history/                # Prompt history
└── README.md               # Updated with new structure
```

## Testing Checklist

### 1. Folder Structure (US1)

```bash
# Verify frontendBook runs independently
cd frontendBook && npm install && npm start
# Expected: Site loads at localhost:3000

# Verify backend folder exists
ls -la ../backend
# Expected: Empty directory exists
```

### 2. Text Visibility (US2)

- Open any documentation page
- Toggle between light/dark mode (navbar toggle)
- Verify all text is clearly readable
- Check sidebar, headings, body, code blocks

### 3. Full-Width Hero (US3)

- Open homepage (localhost:3000/)
- Resize browser window
- Verify hero spans full viewport width (edge to edge)
- No container margins visible on hero

### 4. Mobile Navigation (US4)

- Open Chrome DevTools
- Set device to iPhone 12 (390px width)
- Verify hamburger menu appears
- Open sidebar drawer
- Navigate through chapters

### 5. Responsive Cards (US5)

- Open homepage
- Test at widths: 320px, 768px, 1200px, 1920px
- Verify cards adapt:
  - <768px: Single column
  - 768-1200px: 2 columns
  - >1200px: 3 columns

### 6. Reading Comfort (US6)

- Open any docs page
- Verify paragraph width (~75 characters)
- Check line height (1.5-1.7)
- Ensure comfortable spacing

## Common Commands

```bash
# From frontendBook directory:
npm start          # Dev server
npm run build      # Production build
npm run serve      # Preview build
npm run clear      # Clear cache
npm run swizzle    # Customize Docusaurus components
```

## Troubleshooting

### "Cannot find module" errors

```bash
cd frontendBook
rm -rf node_modules
npm install
```

### Old paths still referenced

- Check docusaurus.config.js for any root-level paths
- Update any hardcoded paths to be relative to frontendBook

### CSS not loading

- Verify custom.css is imported in docusaurus.config.js
- Check for syntax errors in CSS

## Notes

- All development happens in /frontendBook
- Root README.md explains new structure
- Backend folder is empty placeholder
- Spec/history folders unchanged at root
