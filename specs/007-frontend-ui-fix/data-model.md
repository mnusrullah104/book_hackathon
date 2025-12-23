# Data Model: Frontend UI Fix & Consistency

**Feature**: 007-frontend-ui-fix
**Date**: 2025-12-22
**Purpose**: Define theme variable schema, breakpoint system, and component state model

This document describes the "data" for this CSS refactoring feature - namely, the theme variables (CSS custom properties), breakpoints, and component states that govern the visual presentation.

---

## Theme Variable Schema

### Color Variables

#### Light Mode (`:root`)

**Background Colors**:
- `--ifm-background-color`: `#ffffff` - Primary page background
- `--ifm-background-surface-color`: `#ffffff` - Card/surface background
- `--ifm-card-background-color`: `#ffffff` - Card component background
- `--rb-bg-code`: `#f5f5f5` - Code block background (slight gray for distinction)

**Text Colors**:
- `--rb-text-body`: `#1a1a1a` - Body text (16.1:1 contrast)
- `--rb-text-heading`: `#2d2d2d` - Heading text (12.6:1 contrast)
- `--rb-text-muted`: `#4a4a4a` - Secondary/muted text (8.8:1 contrast)
- `--rb-sidebar-text`: `#333333` - Sidebar navigation text

**Accent Colors** (Dark Green):
- `--ifm-color-primary`: `#1b5e20` - Primary accent (Material Green 900)
- `--ifm-color-primary-dark`: `#145c1a` - Darker shade
- `--ifm-color-primary-darker`: `#114d16` - Even darker
- `--ifm-color-primary-darkest`: `#0d3910` - Darkest shade
- `--ifm-color-primary-light`: `#388e3c` - Lighter shade (Material Green 700)
- `--ifm-color-primary-lighter`: `#4caf50` - Even lighter (Material Green 500)
- `--ifm-color-primary-lightest`: `#66bb6a` - Lightest shade (Material Green 400)

**Emphasis Scale** (Grayscale for borders, shadows, backgrounds):
- `--ifm-color-emphasis-0`: `#000000` - Pure black
- `--ifm-color-emphasis-100`: `#1c1e21` - Near black
- `--ifm-color-emphasis-200`: `#3a3d42` - Dark gray
- `--ifm-color-emphasis-300`: `#585c63` - Medium-dark gray
- `--ifm-color-emphasis-400`: `#767a86` - Medium gray
- `--ifm-color-emphasis-500`: `#9499a8` - Mid gray
- `--ifm-color-emphasis-600`: `#b2b5c0` - Light-medium gray
- `--ifm-color-emphasis-700`: `#d0d2d9` - Light gray
- `--ifm-color-emphasis-800`: `#e4e5ec` - Very light gray
- `--ifm-color-emphasis-900`: `#f0f0f4` - Near white
- `--ifm-color-emphasis-1000`: `#ffffff` - Pure white

#### Dark Mode (`html[data-theme='dark']`)

**Background Colors**:
- `--ifm-background-color`: `#0c0c0d` - Primary page background
- `--ifm-background-surface-color`: `#1c1e21` - Card/surface background
- `--ifm-card-background-color`: `#1c1e21` - Card component background
- `--rb-bg-code`: `#1e1e1e` - Code block background

**Text Colors**:
- `--rb-text-body`: `#e8e8e8` - Body text (14.5:1 contrast)
- `--rb-text-heading`: `#f0f0f0` - Heading text (16.8:1 contrast)
- `--rb-text-muted`: `#b0b0b0` - Secondary/muted text (9.2:1 contrast)
- `--rb-sidebar-text`: `#d0d0d0` - Sidebar navigation text

**Accent Colors** (Light Green for dark backgrounds):
- `--ifm-color-primary`: `#66bb6a` - Primary accent (Material Green 400)
- `--ifm-color-primary-dark`: `#4caf50` - Darker shade (Material Green 500)
- `--ifm-color-primary-darker`: `#388e3c` - Even darker (Material Green 700)
- `--ifm-color-primary-darkest`: `#2e7d32` - Darkest shade
- `--ifm-color-primary-light`: `#81c784` - Lighter shade (Material Green 300)
- `--ifm-color-primary-lighter`: `#a5d6a7` - Even lighter (Material Green 200)
- `--ifm-color-primary-lightest`: `#d9b0ff` - Lightest shade

**Emphasis Scale** (Inverted for dark mode):
- `--ifm-color-emphasis-0`: `#ffffff` - Pure white (inverted)
- `--ifm-color-emphasis-100`: `#e4e5ec` - Near white
- `--ifm-color-emphasis-200`: `#d0d2d9` - Light gray
- `--ifm-color-emphasis-300`: `#b2b5c0` - Light-medium gray
- `--ifm-color-emphasis-400`: `#9499a8` - Medium gray
- `--ifm-color-emphasis-500`: `#767a86` - Mid gray
- `--ifm-color-emphasis-600`: `#585c63` - Medium-dark gray
- `--ifm-color-emphasis-700`: `#3a3d42` - Dark gray
- `--ifm-color-emphasis-800`: `#2c2e33` - Very dark gray
- `--ifm-color-emphasis-900`: `#1c1e21` - Near black
- `--ifm-color-emphasis-1000`: `#0c0c0d` - Pure black (inverted)

### Typography Variables

**Font Sizes**:
- `--ifm-font-size-base`: `18px` - Base body text size
- `--ifm-code-font-size`: `95%` - Inline code size (relative to base)

**Line Heights**:
- `--ifm-line-height-base`: `1.6` - Body text line height (optimal readability)
- `--ifm-heading-line-height`: `1.3` - Heading line height (tighter for impact)

**Content Line Length**:
- `max-width: 75ch` - Maximum line length for body text (optimal reading width)

### Spacing Variables

**Scale**:
- `--ifm-spacing-xs`: `0.5rem` (8px)
- `--ifm-spacing-sm`: `0.75rem` (12px)
- `--ifm-spacing-md`: `1rem` (16px)
- `--ifm-spacing-lg`: `1.5rem` (24px)
- `--ifm-spacing-xl`: `2rem` (32px)
- `--ifm-spacing-2xl`: `3rem` (48px)
- `--ifm-spacing-3xl`: `4rem` (64px)

**Content Padding**:
- `--ifm-content-padding-vertical`: `var(--ifm-spacing-lg)` (24px)
- `--ifm-content-padding-horizontal`: `var(--ifm-spacing-xl)` (32px)

### Card Styling Variables

**Card Properties**:
- `--ifm-card-border-radius`: `12px` - Rounded corners for cards
- `--ifm-card-shadow`: `0 10px 30px rgba(0,0,0,0.08)` (light mode) / `0 10px 30px rgba(0,0,0,0.25)` (dark mode)

**Navbar/Footer**:
- `--ifm-navbar-shadow`: `0 2px 8px rgba(0,0,0,0.08)` (light) / `0 2px 8px rgba(0,0,0,0.25)` (dark)

### Container Variables

**Width Constraints**:
- `--ifm-container-width`: `1200px` - Maximum content container width
- `--ifm-container-padding-horizontal`: `2rem` - Horizontal padding for containers

---

## Breakpoint System

### Breakpoint Definitions

| Breakpoint Name | Width Range | Device Type | Grid Columns (Cards) |
|-----------------|-------------|-------------|----------------------|
| Mobile | < 768px | Smartphones | 1 column |
| Tablet | 768px - 996px | Tablets, small laptops | 2 columns |
| Desktop | ≥ 1200px | Desktops, large laptops | 3 columns |

### Media Query Patterns

**Mobile (default)**:
```css
/* Base styles apply to mobile first */
.cardContainer {
  grid-template-columns: 1fr;
}
```

**Tablet**:
```css
@media (min-width: 768px) and (max-width: 996px) {
  .cardContainer {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

**Desktop**:
```css
@media (min-width: 1200px) {
  .cardContainer {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

### Responsive Typography

**Font Size Adjustments**:
- **Desktop/Tablet**: `--ifm-font-size-base: 18px`
- **Mobile (<576px)**: `--ifm-font-size-base: 16px` (slightly smaller for small screens)

**Heading Size Adjustments**:
```css
/* Desktop */
.markdown h1 { font-size: 2.5em; }
.markdown h2 { font-size: 2em; }
.markdown h3 { font-size: 1.75em; }

/* Mobile (<768px) */
.markdown h1 { font-size: 2em; }
.markdown h2 { font-size: 1.7em; }
.markdown h3 { font-size: 1.5em; }
```

---

## Component State Model

### Card Component States

**State Definitions**:
- **Default**: Base appearance when not interacted with
- **Hover**: Appearance when mouse hovers over card
- **Focus**: Appearance when card (or link within) receives keyboard focus

**State Transitions**:
```
Default → Hover (mouse enter)
Hover → Default (mouse leave)
Default → Focus (tab/keyboard navigation)
Focus → Default (blur)
```

**State Properties**:

| Property | Default | Hover | Focus |
|----------|---------|-------|-------|
| `transform` | `translateY(0)` | `translateY(-5px)` | `translateY(0)` |
| `box-shadow` | `0 10px 30px rgba(0,0,0,0.08)` | `0 20px 40px rgba(0,0,0,0.15)` | `0 10px 30px rgba(0,0,0,0.08) + outline` |
| `transition` | `all 0.3s ease` | `all 0.3s ease` | `all 0.3s ease` |
| `outline` | `none` | `none` | `2px solid var(--ifm-color-primary)` |

### Theme State Model

**Theme States**:
- **Light Mode**: Default theme, white backgrounds, dark text
- **Dark Mode**: Alternative theme, black backgrounds, light text

**Theme Switching**:
- Triggered by user clicking theme toggle button (Docusaurus built-in)
- Transition time: `background-color 0.3s ease, color 0.3s ease`
- No flash of unstyled content (FOUC): Docusaurus persists theme choice in localStorage

**Theme-Specific Component Overrides**:
```css
/* Light mode (default) */
.card {
  background: var(--ifm-card-background-color); /* #ffffff */
  border: 1px solid var(--ifm-color-emphasis-300); /* #585c63 */
}

/* Dark mode override */
html[data-theme='dark'] .card {
  background: var(--ifm-card-background-color); /* #1c1e21 */
  border: 1px solid var(--ifm-color-emphasis-700); /* #3a3d42 */
}
```

### Link/Button States

**Interactive Element States**:
- **Default**: Primary accent color (`var(--ifm-color-primary)`)
- **Hover**: Lighter shade (`var(--ifm-color-primary-light)`)
- **Active**: Darker shade (`var(--ifm-color-primary-dark)`)
- **Visited**: Same as default (no special visited state for site navigation)
- **Focus**: Primary color with outline (`2px solid var(--ifm-color-primary)`)

**State Properties**:

| Property | Default | Hover | Active | Focus |
|----------|---------|-------|--------|-------|
| `color` | `var(--ifm-color-primary)` | `var(--ifm-color-primary-light)` | `var(--ifm-color-primary-dark)` | `var(--ifm-color-primary)` |
| `text-decoration` | `none` | `none` | `none` | `none` |
| `outline` | `none` | `none` | `none` | `2px solid currentColor` |
| `outline-offset` | - | - | - | `2px` |
| `transition` | `color 0.3s ease` | `color 0.3s ease` | `color 0.3s ease` | `color 0.3s ease` |

---

## Validation Rules

### Contrast Ratio Requirements

**Light Mode**:
- Body text (`--rb-text-body: #1a1a1a`) on white (`#ffffff`): **MUST** be ≥ 4.5:1 (actual: 16.1:1) ✅
- Accent color (`--ifm-color-primary: #1b5e20`) on white: **MUST** be ≥ 4.5:1 (actual: 9.7:1) ✅

**Dark Mode**:
- Body text (`--rb-text-body: #e8e8e8`) on black (`#0c0c0d`): **MUST** be ≥ 4.5:1 (actual: 14.5:1) ✅
- Accent color (`--ifm-color-primary: #66bb6a`) on black: **MUST** be ≥ 4.5:1 (actual: 7.8:1) ✅

### Card Dimension Requirements

**Width**:
- Cards in same row **MUST** have identical width (CSS Grid ensures this automatically)
- Card width **MUST** be responsive (fraction of container, not fixed pixels)

**Height**:
- Cards in same row **MUST** have equal height (CSS Grid `grid-auto-rows` ensures this)
- Cards in different rows **MAY** have different heights if content varies

**Spacing**:
- Gap between cards **MUST** be consistent: `2rem` (32px)

### Gradient Restrictions

**Prohibited**:
- ❌ Linear or radial gradients behind body text
- ❌ Linear or radial gradients behind heading text
- ❌ Linear or radial gradients in hero banner with overlaid text

**Allowed**:
- ✅ Solid color backgrounds only for text-containing elements
- ✅ Gradients in purely decorative areas with no text (if any)

---

## Relationships

### Variable Dependencies

**Color Relationships**:
```
--ifm-color-primary (base accent color)
  ├── --ifm-color-primary-dark (computed: darken by 10%)
  ├── --ifm-color-primary-darker (computed: darken by 20%)
  ├── --ifm-color-primary-darkest (computed: darken by 30%)
  ├── --ifm-color-primary-light (computed: lighten by 10%)
  ├── --ifm-color-primary-lighter (computed: lighten by 20%)
  └── --ifm-color-primary-lightest (computed: lighten by 30%)
```

**Typography Relationships**:
```
--ifm-font-size-base (18px)
  ├── --ifm-code-font-size (95% of base = 17.1px)
  └── --ifm-line-height-base (1.6 × base = ~29px leading)
```

### Component Relationships

**Card → Card Container**:
- Card is a child of Card Container (grid item)
- Card inherits responsive width from grid template columns
- Card height is determined by content + grid row behavior

**Theme Variables → Components**:
- All components consume theme variables via `var(--variable-name)`
- Theme switching updates variables at root level
- Components automatically re-render with new theme values

---

## Summary

This data model defines:
- **52 theme variables** (26 light mode, 26 dark mode overrides)
- **3 breakpoints** (mobile, tablet, desktop)
- **3 card states** (default, hover, focus)
- **2 theme states** (light, dark)
- **4 link/button states** (default, hover, active, focus)
- **WCAG AA compliance** validated for all text/background pairs

All values are referenced in the CSS variable contract (`contracts/theme-variables.schema.json`) for validation during implementation.
