# Screenshots Directory

**Feature**: 007-frontend-ui-fix
**Purpose**: Store before/after visual comparison screenshots

## How to Capture Screenshots

1. Start dev server: `cd frontend && npm start`
2. Open browser to `http://localhost:3000`
3. Use browser screenshot tools or OS screenshot utility
4. Save screenshots with descriptive names

## Required Screenshots

### Before Screenshots (if available)
- `before-homepage-light-desktop.png`
- `before-homepage-dark-desktop.png`
- `before-homepage-mobile.png`
- `before-doc-page-light.png`
- `before-doc-page-dark.png`

### After Screenshots (capture these)
- `after-homepage-light-desktop.png` - Homepage in light mode, ≥1200px width
- `after-homepage-dark-desktop.png` - Homepage in dark mode, ≥1200px width
- `after-homepage-mobile.png` - Homepage in light mode, 375px width
- `after-doc-page-light.png` - Documentation page in light mode
- `after-doc-page-dark.png` - Documentation page in dark mode
- `after-cards-desktop.png` - Close-up of 3 cards showing consistency
- `after-cards-hover.png` - Card in hover state

## What to Show

**Homepage Screenshots**:
- Hero banner with new green background (no gradient)
- All 3 feature cards visible
- Clear text readability

**Doc Page Screenshots**:
- Body text with 75ch line length
- Sidebar navigation with green accents
- Headings with readable contrast

**Mobile Screenshots**:
- Cards stacked vertically (1 column)
- No horizontal scrolling
- Readable text at 16px font size

## Comparison Checklist

When reviewing screenshots, verify:
- [ ] Text more readable (higher contrast)
- [ ] Cards uniform in size and styling
- [ ] Green color scheme instead of purple
- [ ] No gradients behind text
- [ ] Professional appearance

## Storage

Place all screenshots in this directory (`specs/007-frontend-ui-fix/screenshots/`).

**File naming convention**: `{before|after}-{page}-{theme}-{device}.{png|jpg}`

Examples:
- `after-homepage-light-desktop.png`
- `after-doc-page-dark-mobile.png`
