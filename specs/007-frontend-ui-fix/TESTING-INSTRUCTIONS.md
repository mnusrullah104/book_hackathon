# Testing Instructions for Frontend UI Fix

**Feature**: 007-frontend-ui-fix
**Date**: 2025-12-22
**Status**: Ready for Manual Testing

## Quick Start

To test the implemented UI fixes:

1. **Start Dev Server**:
   ```bash
   cd frontend
   npm start
   ```

2. **Open Browser**: Navigate to `http://localhost:3000`

3. **Follow Test Suites**: Use `specs/007-frontend-ui-fix/quickstart.md` for comprehensive testing

## Critical Tests to Run

### Test 1: Light Mode Text Readability
- [ ] Visit homepage - verify hero text, card text visible
- [ ] Toggle to light mode if needed
- [ ] Check sidebar links are readable
- [ ] Navigate to a doc page - verify body text, headings readable

### Test 2: Dark Mode Text Readability
- [ ] Toggle to dark mode (moon icon)
- [ ] Verify all text from Test 1 remains readable
- [ ] Check contrast is comfortable for reading

### Test 3: Homepage Cards
- [ ] Desktop (≥1200px): 3 cards visible, equal size
- [ ] Tablet (800px): 2 cards visible, equal size
- [ ] Mobile (400px): 1 card stacked, full width
- [ ] All cards same background, border, shadow
- [ ] Hover over each card - same animation

### Test 4: Color Scheme
- [ ] No purple colors visible anywhere
- [ ] All links and buttons use dark green
- [ ] Hero banner has solid green background (no gradient)
- [ ] Footer has solid green background (no gradient)

### Test 5: Responsive Layout
- [ ] Resize browser from 320px to 1440px
- [ ] No horizontal scrolling at any width
- [ ] Text line length reasonable (not too wide)
- [ ] Layout doesn't break at any breakpoint

## Expected Results

**Color Scheme**:
- Light mode: Green accent color `#1b5e20`
- Dark mode: Light green accent `#66bb6a`
- Hero banner: Solid green (not gradient)
- Cards: White background (light), dark background (dark)

**Contrast**:
- All text should be easily readable
- No eye strain in either mode
- Sufficient contrast for accessibility

**Cards**:
- Uniform size within each row
- Same styling (background, border, shadow)
- Smooth hover animation

## Full Testing Checklist

For comprehensive testing, execute all 8 test suites from:
`specs/007-frontend-ui-fix/quickstart.md`

## Reporting Issues

If you find any issues:
1. Take screenshots
2. Note the viewport width and theme mode
3. Describe what's wrong vs expected behavior
4. Check browser console for errors

## Implementation Changes Summary

**Files Modified**:
1. `frontend/src/css/custom.css`:
   - Replaced purple with Material Design green palette
   - Removed table header gradients
   - Removed footer gradient

2. `frontend/src/pages/index.module.css`:
   - Replaced hero banner gradient with solid green
   - Added explicit responsive grid breakpoints

**What Changed**:
- Purple → Dark green throughout
- Gradients → Solid colors
- Auto-fit grid → Explicit breakpoints
- All text uses high-contrast colors

**What Stayed the Same**:
- Typography (18px base, 1.6 line height)
- Spacing and padding
- Card structure and layout
- Navigation and routing
- Markdown content
