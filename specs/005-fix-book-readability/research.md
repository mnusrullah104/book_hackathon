# Research: Fix & Redesign Book UI for Readability

**Feature**: 005-fix-book-readability
**Date**: 2025-12-22
**Purpose**: Resolve NEEDS CLARIFICATION items and research best practices

## Research Tasks

### 1. Current CSS Analysis

**Finding**: The existing `src/css/custom.css` (1,149 lines) has these readability problems:

| Issue | Current State | Problem |
|-------|---------------|---------|
| Body text color | Not explicitly defined | Relies on browser/Docusaurus defaults |
| Heading colors | `--ifm-color-purple-dark: #5a189a` for H1 | Dark purple on dark bg = poor contrast |
| Sidebar text | Purple-based colors | Can blend with backgrounds |
| Dark mode body | No explicit text color | May inherit poor contrast |

**Decision**: Override default text colors with high-contrast values
**Rationale**: WCAG AA requires 4.5:1 contrast for body text

### 2. WCAG AA Contrast Requirements

**Finding**: WCAG 2.1 AA standards require:
- Body text (under 18pt): 4.5:1 contrast ratio minimum
- Large text (18pt+ or 14pt bold): 3:1 contrast ratio minimum
- Non-text elements: 3:1 contrast ratio

**Decision**: Use these color combinations:
- Light mode: `#1a1a1a` text on `#ffffff` background (contrast: 16.1:1)
- Dark mode: `#e8e8e8` text on `#121212` background (contrast: 14.5:1)

**Alternatives Considered**:
- Pure black (#000000) - Rejected: too harsh, causes eye strain
- Gray (#666666) - Rejected: only 5.7:1 contrast, borderline

### 3. Heading Color Strategy

**Finding**: Current headings use various purple shades:
- H1: `--ifm-color-purple-dark: #5a189a`
- H2: `--ifm-color-purple-darker: #6a16c2`
- H3: `--ifm-color-purple-primary: #8a2be2`

**Problem**: Purple (#8a2be2) on white has 6.5:1 contrast (passes AA), but on dark backgrounds (#121212) contrast drops to 4.8:1 (borderline).

**Decision**: 
- Keep purple for H1 only (larger text, 3:1 sufficient)
- Use dark gray/near-black for H2-H6 to ensure readability
- In dark mode, use lighter shades for headings

**Rationale**: Maintains brand identity while ensuring readability

### 4. Sidebar Navigation Contrast

**Finding**: Current sidebar uses:
- `--ifm-color-purple-darker: #6a16c2` for active items
- Opacity-based hover states
- Purple gradients on mobile nav

**Problem**: Purple text on dark sidebar backgrounds creates contrast issues.

**Decision**: 
- Use high-contrast neutral colors for sidebar text
- Reserve purple for active/selected states only
- Remove opacity-based text styling

### 5. Code Block Readability

**Finding**: Current code blocks have:
- Purple gradient backgrounds
- Purple borders
- Syntax highlighting with various colors

**Problem**: Gradient backgrounds can interfere with syntax highlighting readability.

**Decision**: 
- Use flat, solid backgrounds (light gray in light mode, dark gray in dark mode)
- Ensure syntax highlighting colors have sufficient contrast
- Remove purple gradients from code block backgrounds

### 6. Mobile Responsiveness

**Finding**: Current mobile breakpoints:
- 996px: Sidebar collapses
- 768px: Typography scales
- 576px: Font size reduces to 16px

**Decision**: Keep existing breakpoints, but ensure:
- Minimum 16px font size on all screens
- Touch targets minimum 44x44px
- All contrast requirements apply at all sizes

## Key Research Conclusions

1. **Text Colors**: Define explicit body text colors (not relying on defaults)
2. **Heading Strategy**: Keep purple for H1 only; neutral colors for body headings
3. **Sidebar**: High-contrast neutral text; purple only for active states
4. **Code Blocks**: Flat backgrounds; readable syntax colors
5. **No Breaking Changes**: All changes are CSS-only; no structural changes needed

## CSS Variables to Add/Modify

```css
/* Light mode body text */
--text-color-body: #1a1a1a;
--text-color-heading: #2d2d2d;
--text-color-muted: #4a4a4a;

/* Dark mode body text */
--text-color-body-dark: #e8e8e8;
--text-color-heading-dark: #f0f0f0;
--text-color-muted-dark: #b0b0b0;

/* Sidebar text */
--sidebar-text-color: #333333;
--sidebar-text-color-dark: #d0d0d0;
--sidebar-active-color: #8a2be2; /* Keep purple for active */
```
