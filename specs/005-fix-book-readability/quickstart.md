# Quickstart: Fix & Redesign Book UI for Readability

**Feature**: 005-fix-book-readability
**Date**: 2025-12-22

## Prerequisites

- Node.js 18+
- npm or yarn
- Browser with DevTools (Chrome/Firefox recommended)

## Setup

```bash
# Clone and install
cd D:/BookWriting_Hackathon1
npm install

# Start development server
npm start
```

## Development Workflow

### 1. Start Dev Server

```bash
npm start
```

Opens at `http://localhost:3000`

### 2. CSS File Location

All changes will be in:
```
src/css/custom.css
```

### 3. Testing Contrast

Use these tools to verify WCAG AA compliance:

1. **Chrome DevTools**:
   - Elements > Styles > hover over color swatch
   - Shows contrast ratio automatically

2. **WebAIM Contrast Checker**:
   - https://webaim.org/resources/contrastchecker/
   - Enter foreground and background colors

3. **Lighthouse Audit**:
   ```bash
   # In Chrome DevTools > Lighthouse tab
   # Select "Accessibility" and run
   ```

### 4. Theme Toggle

- Use the moon/sun icon in navbar to switch themes
- Test all changes in BOTH light and dark modes

### 5. Key CSS Sections to Modify

| Line Range | Section | What to Change |
|------------|---------|----------------|
| 10-87 | Root variables | Add body text colors |
| 96-145 | Dark theme | Add dark body text colors |
| 429-447 | Main wrapper | Body text color |
| 511-576 | Sidebar | Navigation text colors |
| 1050-1127 | Headings | H2-H6 colors (keep H1 purple) |

### 6. Quick Verification Checklist

After each change:

- [ ] Light mode body text readable?
- [ ] Dark mode body text readable?
- [ ] Headings distinguishable from body?
- [ ] Sidebar text clearly visible?
- [ ] Code blocks readable?
- [ ] Mobile view (use DevTools responsive mode)?

## Common Commands

```bash
# Development
npm start

# Build
npm run build

# Serve production build locally
npm run serve

# Type check (if applicable)
npm run typecheck
```

## Files to Watch

```
src/css/custom.css    # Main stylesheet - ALL changes here
docusaurus.config.js  # Theme configuration (no changes needed)
```

## Notes

- Hot reload works for CSS changes
- Save file to see changes immediately
- Test on actual mobile device before finalizing
