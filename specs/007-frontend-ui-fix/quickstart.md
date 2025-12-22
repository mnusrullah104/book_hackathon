# Quickstart: Testing Guide for Frontend UI Fix

**Feature**: 007-frontend-ui-fix
**Date**: 2025-12-22
**Purpose**: Step-by-step manual testing checklist for verifying UI fixes

This guide provides a comprehensive testing workflow for validating that all UI fixes meet the specification requirements. Use this checklist after implementing CSS changes.

---

## Prerequisites

Before testing, ensure:
- [ ] Docusaurus development server is running (`npm start` in `frontend/` directory)
- [ ] Browser DevTools are open (F12 or Cmd+Option+I)
- [ ] WebAIM Contrast Checker available (https://webaim.org/resources/contrastchecker/)
- [ ] Test browsers installed: Chrome (primary), Firefox, Safari, Edge

---

## Test Suite 1: Text Readability & Contrast

### 1.1 Light Mode Text Contrast

**Objective**: Verify all text meets WCAG AA contrast requirements in light mode

**Steps**:
1. Navigate to homepage (`http://localhost:3000`)
2. Ensure light mode is active (toggle if needed)
3. Open DevTools → Elements tab
4. For each text element below, inspect computed color values:

| Element | Expected Text Color | Expected Background | Min Contrast | Pass/Fail |
|---------|---------------------|---------------------|--------------|-----------|
| Hero title | `#ffffff` (white) | `#1b5e20` (dark green) | 9.7:1 | [ ] |
| Hero subtitle | `#ffffff` (white) | `#1b5e20` (dark green) | 9.7:1 | [ ] |
| Card title | `#2d2d2d` | `#ffffff` (white) | 12.6:1 | [ ] |
| Card description | `#1a1a1a` | `#ffffff` (white) | 16.1:1 | [ ] |
| Sidebar links | `#333333` | `#ffffff` (white) | 10.4:1 | [ ] |
| Body text (doc page) | `#1a1a1a` | `#ffffff` (white) | 16.1:1 | [ ] |
| Headings (doc page) | `#2d2d2d` | `#ffffff` (white) | 12.6:1 | [ ] |

**Verification Method**:
1. Right-click element → Inspect
2. Note `color` and `background-color` values
3. Paste into WebAIM Contrast Checker
4. Verify ratio meets or exceeds "Min Contrast" column

**Expected Result**: All elements pass with contrast ≥ listed value

---

### 1.2 Dark Mode Text Contrast

**Objective**: Verify all text meets WCAG AA contrast requirements in dark mode

**Steps**:
1. Toggle to dark mode (moon icon in navbar)
2. Repeat inspection process from 1.1

| Element | Expected Text Color | Expected Background | Min Contrast | Pass/Fail |
|---------|---------------------|---------------------|--------------|-----------|
| Hero title | `#ffffff` (white) | `#0c0c0d` or dark green | 14.5:1+ | [ ] |
| Hero subtitle | `#ffffff` (white) | `#0c0c0d` or dark green | 14.5:1+ | [ ] |
| Card title | `#f0f0f0` | `#1c1e21` | 14.1:1 | [ ] |
| Card description | `#e8e8e8` | `#1c1e21` | 11.8:1 | [ ] |
| Sidebar links | `#d0d0d0` | `#1c1e21` | 9.5:1 | [ ] |
| Body text (doc page) | `#e8e8e8` | `#0c0c0d` | 14.5:1 | [ ] |
| Headings (doc page) | `#f0f0f0` | `#0c0c0d` | 16.8:1 | [ ] |

**Expected Result**: All elements pass with contrast ≥ listed value

---

### 1.3 Accent Color Contrast

**Objective**: Verify dark green accent colors meet contrast requirements

**Steps**:
1. Test in light mode first
2. Find a link or button on homepage or doc page
3. Inspect computed color

| Mode | Element | Expected Color | Expected Background | Min Contrast | Pass/Fail |
|------|---------|----------------|---------------------|--------------|-----------|
| Light | Links | `#1b5e20` | `#ffffff` | 9.7:1 | [ ] |
| Light | Active menu item | `#1b5e20` | `#ffffff` | 9.7:1 | [ ] |
| Dark | Links | `#66bb6a` | `#0c0c0d` | 7.8:1 | [ ] |
| Dark | Active menu item | `#66bb6a` | `#0c0c0d` | 7.8:1 | [ ] |

**Expected Result**: All accent colors pass WCAG AA (≥4.5:1 for normal text)

---

## Test Suite 2: Homepage Card Consistency

### 2.1 Card Dimensions - Desktop

**Objective**: Verify all cards have identical dimensions on desktop

**Steps**:
1. Resize browser to ≥1200px width (desktop breakpoint)
2. Navigate to homepage
3. Scroll to cards section
4. Open DevTools → Elements tab
5. Inspect each card and measure dimensions

| Card | Width (px) | Min-Height (px) | Padding | Pass/Fail |
|------|------------|-----------------|---------|-----------|
| Card 1 (ROS 2) | [ ] | [ ] | [ ] | [ ] |
| Card 2 (AI Agents) | [ ] | [ ] | [ ] | [ ] |
| Card 3 (Humanoid) | [ ] | [ ] | [ ] | [ ] |

**Verification Method**:
1. Right-click card → Inspect
2. In Computed tab, note `width`, `min-height`, `padding`
3. All widths should be identical (within 1px tolerance)
4. All padding values should match exactly

**Expected Result**:
- All cards have identical width (± 1px)
- All cards have same padding: `2rem` (32px)
- Cards expand vertically based on content (no fixed height)

---

### 2.2 Card Dimensions - Tablet

**Objective**: Verify cards maintain consistency at tablet breakpoint

**Steps**:
1. Resize browser to 800px width (tablet breakpoint)
2. Repeat measurement process from 2.1

**Expected Result**:
- 2 columns visible
- Cards in same row have identical width
- Cards in same row have identical height

---

### 2.3 Card Dimensions - Mobile

**Objective**: Verify cards stack properly on mobile

**Steps**:
1. Resize browser to 400px width (mobile breakpoint)
2. Repeat measurement process from 2.1

**Expected Result**:
- 1 column visible (cards stacked vertically)
- Each card spans full container width (minus padding)
- All cards have identical width

---

### 2.4 Card Visual Consistency

**Objective**: Verify all cards have identical styling (background, border, shadow)

**Steps**:
1. Inspect each card's computed styles

| Property | Card 1 | Card 2 | Card 3 | All Match? |
|----------|--------|--------|--------|------------|
| **Light Mode** | | | | |
| `background-color` | [ ] | [ ] | [ ] | [ ] |
| `border` (color, width, style) | [ ] | [ ] | [ ] | [ ] |
| `box-shadow` | [ ] | [ ] | [ ] | [ ] |
| `border-radius` | [ ] | [ ] | [ ] | [ ] |
| **Dark Mode** | | | | |
| `background-color` | [ ] | [ ] | [ ] | [ ] |
| `border` (color, width, style) | [ ] | [ ] | [ ] | [ ] |
| `box-shadow` | [ ] | [ ] | [ ] | [ ] |
| `border-radius` | [ ] | [ ] | [ ] | [ ] |

**Expected Values**:
- **Light Mode**:
  - Background: `#ffffff`
  - Border: `1px solid #585c63`
  - Shadow: `0 10px 30px rgba(0,0,0,0.08)`
  - Border radius: `12px`
- **Dark Mode**:
  - Background: `#1c1e21`
  - Border: `1px solid #3a3d42`
  - Shadow: `0 10px 30px rgba(0,0,0,0.25)`
  - Border radius: `12px`

**Expected Result**: All cards match exactly in both light and dark modes

---

### 2.5 Card Hover States

**Objective**: Verify all cards respond identically to hover

**Steps**:
1. Hover over each card slowly
2. Observe animation and shadow change

| Card | Transform (hover) | Shadow (hover) | Transition Smooth? | Pass/Fail |
|------|-------------------|----------------|--------------------|-----------|
| Card 1 | `translateY(-5px)` | `0 20px 40px rgba(0,0,0,0.15)` | [ ] | [ ] |
| Card 2 | `translateY(-5px)` | `0 20px 40px rgba(0,0,0,0.15)` | [ ] | [ ] |
| Card 3 | `translateY(-5px)` | `0 20px 40px rgba(0,0,0,0.15)` | [ ] | [ ] |

**Verification Method**:
1. Open DevTools → Elements → Styles tab
2. Trigger `:hover` state using DevTools
3. Check computed `transform` and `box-shadow` values

**Expected Result**: All cards lift up 5px and gain enhanced shadow on hover with smooth 0.3s transition

---

## Test Suite 3: Color System Validation

### 3.1 Three-Color Palette Audit

**Objective**: Verify only approved colors (white/black/dark-green) are used

**Steps**:
1. Use DevTools → Elements → Computed styles
2. Check for any hardcoded purple colors (old scheme)

**Prohibited Colors** (should NOT appear anywhere):
- [ ] `#8a2be2` (old purple primary)
- [ ] `#9a46e8` (old purple dark mode)
- [ ] `#7a1ad2`, `#6a16c2`, `#aa60ee`, `#c285f3` (old purple shades)

**Grep Command** (run in `frontend/src/` directory):
```bash
grep -r "#8a2be2\|#9a46e8\|#7a1ad2" --include="*.css" --include="*.jsx" --include="*.js"
```

**Expected Result**: Zero matches (all purple colors replaced with green)

---

### 3.2 Gradient Removal Verification

**Objective**: Verify no gradients exist behind text

**Steps**:
1. Inspect hero banner background
2. Inspect table headers (if any)
3. Inspect footer (if it contains text)

| Element | CSS Background | Contains Gradient? | Text Overlap? | Pass/Fail |
|---------|----------------|-------------------|---------------|-----------|
| Hero banner | [ ] | [ ] NO | [ ] YES | [ ] |
| Table headers | [ ] | [ ] NO | [ ] YES | [ ] |
| Footer | [ ] | [ ] NO / OK if no text | [ ] YES / NO | [ ] |

**Grep Command**:
```bash
grep -r "linear-gradient\|radial-gradient" frontend/src/css/ frontend/src/pages/
```

**Expected Result**:
- Zero gradients behind text-containing elements
- Hero banner uses solid dark green or black background
- Table headers use solid light green tint

---

### 3.3 Theme Variable Usage

**Objective**: Verify all colors use CSS variables (no hardcoded hex)

**Steps**:
1. Review CSS files for hardcoded colors

**Grep Command** (find hardcoded hex colors):
```bash
grep -E "#[0-9a-fA-F]{3,6}" frontend/src/css/custom.css frontend/src/pages/index.module.css | grep -v "var(--"
```

**Expected Result**:
- Only theme variable definitions (`:root`, `html[data-theme='dark']`) contain hex colors
- All component styles use `var(--variable-name)` pattern

---

## Test Suite 4: Responsive Layout

### 4.1 Breakpoint Behavior

**Objective**: Verify layout reflows correctly at each breakpoint

**Steps**:
1. Use Chrome DevTools Device Toolbar (Cmd+Shift+M or Ctrl+Shift+M)
2. Test at specific widths

| Viewport Width | Expected Card Columns | Actual Columns | Text Line Length (<75ch) | Pass/Fail |
|----------------|----------------------|----------------|--------------------------|-----------|
| 320px (mobile) | 1 | [ ] | [ ] | [ ] |
| 400px (mobile) | 1 | [ ] | [ ] | [ ] |
| 768px (tablet) | 2 | [ ] | [ ] | [ ] |
| 900px (tablet) | 2 | [ ] | [ ] | [ ] |
| 1200px (desktop) | 3 | [ ] | [ ] | [ ] |
| 1440px (desktop) | 3 | [ ] | [ ] | [ ] |

**Text Line Length Check**:
1. Navigate to a documentation page with body text
2. Inspect a paragraph element
3. In Computed tab, check `max-width` = `75ch`

**Expected Result**: Cards reflow at correct breakpoints, text line length limited to 75 characters

---

### 4.2 Mobile Responsiveness

**Objective**: Verify no horizontal scrolling, proper spacing on mobile

**Steps**:
1. Set viewport to 375px (iPhone size)
2. Navigate to homepage and doc pages
3. Scroll vertically through entire page

**Checklist**:
- [ ] No horizontal scrollbar appears
- [ ] All content fits within viewport width
- [ ] Cards stack vertically with consistent spacing
- [ ] Text reflows properly (no overflow)
- [ ] Sidebar opens/closes smoothly (hamburger menu)

**Expected Result**: Entire site usable on mobile with no horizontal scrolling

---

## Test Suite 5: Theme Switching

### 5.1 Theme Toggle Performance

**Objective**: Verify theme switch completes in <300ms with no FOUC

**Steps**:
1. Open DevTools → Performance tab
2. Start recording
3. Toggle theme (light → dark or dark → light)
4. Stop recording
5. Analyze timeline

**Metrics to Check**:
- [ ] Theme switch completes in <300ms
- [ ] No flash of unstyled content (FOUC)
- [ ] No layout shift (CLS = 0)
- [ ] Smooth color transition visible

**Expected Result**: Theme changes smoothly within 300ms with no visual glitches

---

### 5.2 Theme Persistence

**Objective**: Verify theme preference persists across page reloads

**Steps**:
1. Set theme to dark mode
2. Refresh page (F5)
3. Verify dark mode persists

**Checklist**:
- [ ] Dark mode persists after refresh
- [ ] Theme preference stored in localStorage
- [ ] No theme flicker on initial page load

**Expected Result**: User's theme choice persists across sessions

---

## Test Suite 6: Cross-Browser Testing

### 6.1 Browser Compatibility

**Objective**: Verify UI works consistently across modern browsers

**Browsers to Test**:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest, macOS only)
- [ ] Edge (latest)

**Test Checklist** (repeat Tests 1-5 in each browser):
| Test Suite | Chrome | Firefox | Safari | Edge |
|------------|--------|---------|--------|------|
| Text Contrast (Light) | [ ] | [ ] | [ ] | [ ] |
| Text Contrast (Dark) | [ ] | [ ] | [ ] | [ ] |
| Card Consistency | [ ] | [ ] | [ ] | [ ] |
| Color System | [ ] | [ ] | [ ] | [ ] |
| Responsive Layout | [ ] | [ ] | [ ] | [ ] |
| Theme Switching | [ ] | [ ] | [ ] | [ ] |

**Expected Result**: All tests pass in all browsers (CSS custom properties supported in all modern browsers)

---

## Test Suite 7: Accessibility

### 7.1 Automated Accessibility Testing

**Objective**: Verify WCAG 2.1 Level AA compliance using automated tools

**Tools**:
1. **Lighthouse** (Chrome DevTools → Lighthouse tab)
2. **axe DevTools** (browser extension: https://www.deque.com/axe/devtools/)

**Steps**:
1. Run Lighthouse accessibility audit
2. Run axe DevTools scan
3. Review and fix any issues

**Expected Lighthouse Score**: ≥90 (accessibility category)

**Expected axe Results**: Zero violations for:
- [ ] Color contrast
- [ ] Keyboard navigation
- [ ] Focus indicators
- [ ] ARIA labels (if applicable)

---

### 7.2 Keyboard Navigation

**Objective**: Verify all interactive elements are keyboard accessible

**Steps**:
1. Navigate site using only keyboard (Tab, Shift+Tab, Enter, Space)
2. Verify focus indicators visible

**Checklist**:
- [ ] Can tab through all links and buttons
- [ ] Focus indicators visible (2px solid border, `--ifm-color-primary`)
- [ ] Can open sidebar on mobile using keyboard
- [ ] Can toggle theme using keyboard
- [ ] No keyboard traps (can escape from all elements)

**Expected Result**: Full keyboard navigation support with visible focus indicators

---

## Test Suite 8: Visual Regression

### 8.1 Before/After Screenshots

**Objective**: Document visual changes for stakeholder review

**Steps**:
1. Capture screenshots of:
   - Homepage (light mode, desktop)
   - Homepage (dark mode, desktop)
   - Homepage (mobile, 375px)
   - Doc page (light mode)
   - Doc page (dark mode)
2. Compare with "before" screenshots (if available)

**Storage**: Save to `specs/007-frontend-ui-fix/screenshots/` directory

**Comparison Checklist**:
- [ ] Text more readable (higher contrast)
- [ ] Cards more consistent (uniform sizing)
- [ ] Color scheme simplified (green instead of purple)
- [ ] Gradients removed from text areas
- [ ] Overall more professional appearance

---

## Summary Checklist

Use this high-level checklist to track overall testing progress:

- [ ] **Test Suite 1**: Text Readability & Contrast (Light & Dark)
- [ ] **Test Suite 2**: Homepage Card Consistency (Desktop, Tablet, Mobile)
- [ ] **Test Suite 3**: Color System Validation (3-color palette, no gradients)
- [ ] **Test Suite 4**: Responsive Layout (Breakpoints, mobile)
- [ ] **Test Suite 5**: Theme Switching (Performance, persistence)
- [ ] **Test Suite 6**: Cross-Browser Testing (Chrome, Firefox, Safari, Edge)
- [ ] **Test Suite 7**: Accessibility (Lighthouse, axe, keyboard nav)
- [ ] **Test Suite 8**: Visual Regression (Before/after comparison)

---

## Troubleshooting

### Common Issues and Solutions

**Issue**: Text contrast fails in light mode
- **Solution**: Verify `--rb-text-body` is `#1a1a1a`, not a lighter gray
- **Check**: Ensure no inline styles overriding CSS variables

**Issue**: Cards have different heights
- **Solution**: Ensure CSS Grid is using `grid-auto-rows: 1fr` or remove fixed heights
- **Check**: Verify no `height: 100%` on card content children

**Issue**: Purple colors still visible
- **Solution**: Search for hardcoded purple hex values (`#8a2be2`) and replace with `var(--ifm-color-primary)`
- **Check**: Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)

**Issue**: Theme switch causes FOUC
- **Solution**: Ensure Docusaurus theme persistence is enabled in `docusaurus.config.js`
- **Check**: Verify localStorage contains theme preference

**Issue**: Gradient still visible in hero banner
- **Solution**: Replace `background: linear-gradient(...)` with `background: var(--ifm-color-primary)` or solid color
- **Check**: Verify DevTools Computed styles show no gradient

---

## Sign-Off

After completing all tests:

**Tester Name**: ___________________________
**Date**: ___________________________
**Overall Result**: [ ] PASS / [ ] FAIL (with issues noted below)

**Issues Found**:
1. ___________________________
2. ___________________________
3. ___________________________

**Ready for Production**: [ ] YES / [ ] NO
