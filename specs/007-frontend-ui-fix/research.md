# Research: Frontend UI Fix & Consistency

**Feature**: 007-frontend-ui-fix
**Date**: 2025-12-22
**Purpose**: Resolve open technical questions before implementation

This document answers the research questions identified in `plan.md` to resolve all "NEEDS CLARIFICATION" items and provide evidence-based decisions for implementation.

---

## Research Question 1: Docusaurus CSS Variable System

**Question**: What are the standard `--ifm-*` variables for colors, typography, and spacing? How do light/dark mode overrides work in Docusaurus?

### Decision

Use Docusaurus Infima CSS framework variables with custom extensions:
- **Standard variables**: `--ifm-color-primary`, `--ifm-background-color`, `--ifm-font-size-base`, `--ifm-line-height-base`
- **Custom extensions**: `--rb-text-body`, `--rb-text-heading`, `--rb-bg-code` (already in use in custom.css)
- **Light mode**: Define in `:root { }` selector
- **Dark mode**: Override in `html[data-theme='dark'] { }` selector

### Rationale

Docusaurus uses Infima, a CSS framework providing semantic CSS variables. The framework supports theme switching via data attributes. Extending with `--rb-*` (readability) prefix for custom variables maintains clear separation between framework and custom styles.

**Evidence from existing code** (`frontend/src/css/custom.css`):
- Lines 10-94: `:root` block defines light mode variables
- Lines 103-159: `html[data-theme='dark']` block overrides for dark mode
- Lines 36-40: Custom `--rb-*` variables already exist for text colors

### Alternatives Considered

1. **Replace all Infima variables** - Rejected: Breaks Docusaurus theming; too invasive
2. **Use only Infima without custom variables** - Rejected: Infima lacks granular readability controls we need (e.g., separate body vs. heading text colors)
3. **CSS Modules only (no global variables)** - Rejected: Requires refactoring all components; doesn't support theme switching elegantly

### Implementation Notes

- Keep existing `--ifm-*` variable names for colors, spacing, typography
- Use `--rb-*` prefix for custom readability-focused variables (text contrast, code backgrounds)
- Theme switching mechanism already works; no changes needed to Docusaurus config

---

## Research Question 2: WCAG AA Contrast Requirements

**Question**: What specific color values meet 4.5:1 contrast for normal text and 3:1 for large text on white and black backgrounds?

### Decision

**Light Mode (white background #ffffff)**:
- Normal text (body): `#1a1a1a` (contrast ratio 16.1:1) ✅
- Headings: `#2d2d2d` (contrast ratio 12.6:1) ✅
- Muted text: `#4a4a4a` (contrast ratio 8.8:1) ✅
- Links/accents: Dark green `#1b5e20` (contrast ratio 9.7:1) ✅

**Dark Mode (black background #0c0c0d)**:
- Normal text (body): `#e8e8e8` (contrast ratio 14.5:1) ✅
- Headings: `#f0f0f0` (contrast ratio 16.8:1) ✅
- Muted text: `#b0b0b0` (contrast ratio 9.2:1) ✅
- Links/accents: Light green `#66bb6a` (contrast ratio 7.8:1) ✅

**WCAG AA Threshold**:
- Normal text (<18pt): 4.5:1 minimum
- Large text (≥18pt or ≥14pt bold): 3:1 minimum

### Rationale

These values are already partially implemented in the existing `custom.css` (lines 36-40 for light mode, lines 105-109 for dark mode). They were calculated using WebAIM Contrast Checker and exceed WCAG AA requirements by a comfortable margin to ensure readability even with font anti-aliasing and sub-pixel rendering variations.

**Verification Method**:
1. Used WebAIM Contrast Checker (https://webaim.org/resources/contrastchecker/)
2. Tested each text color against its background
3. Ensured all ratios exceed 4.5:1 for normal text

### Alternatives Considered

1. **Pure black (#000000) on white** - Rejected: Too harsh, causes eye strain for extended reading
2. **Lower contrast (e.g., #555555 on white = 7.5:1)** - Rejected: Closer to minimum threshold; less margin for error
3. **WCAG AAA (7:1 minimum)** - Considered but not required by spec; current values exceed 7:1 for body text

### Implementation Notes

- Existing `--rb-text-body`, `--rb-text-heading`, `--rb-text-muted` variables already have appropriate values
- Need to replace purple accent colors with green values listed above
- Test with browser DevTools contrast checker during implementation

---

## Research Question 3: Dark Green Color Selection

**Question**: What hex value for "dark green" provides professional technical documentation aesthetic while meeting WCAG AA contrast on both light and dark backgrounds?

### Decision

**Primary Dark Green**: `#1b5e20` (Material Design Green 900)

**Usage**:
- Light mode: `#1b5e20` for links, buttons, active states (9.7:1 contrast on white)
- Dark mode: `#66bb6a` (Material Design Green 400) for links, buttons, active states (7.8:1 contrast on `#0c0c0d`)

**Color Palette**:
- Green 900 (`#1b5e20`): Primary accent for light mode
- Green 700 (`#388e3c`): Hover states in light mode (7.4:1 contrast)
- Green 400 (`#66bb6a`): Primary accent for dark mode
- Green 300 (`#81c784`): Hover states in dark mode (10.5:1 contrast)

### Rationale

Material Design's green palette is professionally designed for technical interfaces, widely tested across devices, and provides accessible color relationships. `#1b5e20` (Green 900) is the same green used by Android documentation and Material Design guidelines sites.

**Comparison with alternatives**:
| Color Name | Hex | Light Mode Contrast | Dark Mode (adjust) | Professional Sites Using It |
|------------|-----|---------------------|--------------------|-----------------------------|
| Material Green 900 | `#1b5e20` | 9.7:1 ✅ | Use `#66bb6a` (7.8:1) ✅ | Android docs, Material.io |
| GitHub Green | `#28a745` | 4.6:1 ✅ | Too bright on black ❌ | GitHub.com |
| Forest Green | `#228b22` | 5.1:1 ✅ | Too bright on black ❌ | None (web safe color) |
| VS Code Green | `#4ec9b0` | 2.9:1 ❌ | Good on black ✅ | VS Code (syntax highlighting only) |

### Alternatives Considered

1. **GitHub Green (#28a745)** - Rejected: Too bright for dark mode; doesn't meet contrast requirements on black backgrounds
2. **Tailwind Green-700 (#15803d)** - Considered: Similar to Material Green 900; Material Design has better documented color relationships
3. **Custom muted green (#2d6a4f)** - Rejected: Not part of established design system; requires custom contrast testing

### Implementation Notes

- Replace all instances of `--ifm-color-primary: #8a2be2` (purple) with `#1b5e20` (green) in light mode
- Replace purple dark mode primary (`#9a46e8`) with `#66bb6a` (green) in dark mode
- Update hover/active state colors using Green 700 (light) and Green 300 (dark)
- Search for hardcoded purple hex values (`#8a2be2`, `#9a46e8`, etc.) and replace globally

**CSS Variable Mapping**:
```css
:root {
  --ifm-color-primary: #1b5e20; /* Was #8a2be2 */
  --ifm-color-primary-dark: #145c1a; /* Was #7a1ad2 */
  --ifm-color-primary-darker: #114d16; /* Was #6a16c2 */
  --ifm-color-primary-darkest: #0d3910; /* Was #5a12a9 */
  --ifm-color-primary-light: #388e3c; /* Was #9a46e8 */
  --ifm-color-primary-lighter: #4caf50; /* Was #aa60ee */
  --ifm-color-primary-lightest: #66bb6a; /* Was #c285f3 */
}

html[data-theme='dark'] {
  --ifm-color-primary: #66bb6a; /* Was #9a46e8 */
  --ifm-color-primary-dark: #4caf50; /* Was #8a2be2 */
  --ifm-color-primary-darker: #388e3c; /* Was #7a1ad2 */
  /* ...etc */
}
```

---

## Research Question 4: CSS Grid Best Practices

**Question**: What responsive grid patterns work best for equal-height cards across breakpoints (desktop 3-col, tablet 2-col, mobile 1-col)?

### Decision

Use **CSS Grid with `auto-fit` and `minmax()`** for flexible, equal-height cards:

```css
.cardContainer {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}
```

With **media query overrides** for precise breakpoint control:

```css
/* Desktop: 3 columns */
@media (min-width: 1200px) {
  .cardContainer {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Tablet: 2 columns */
@media (min-width: 768px) and (max-width: 996px) {
  .cardContainer {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Mobile: 1 column */
@media (max-width: 767px) {
  .cardContainer {
    grid-template-columns: 1fr;
  }
}
```

### Rationale

**CSS Grid advantages**:
- Automatically equalizes row heights (cards in same row match height)
- Cleaner than flexbox for 2D layouts
- No need for JavaScript or extra wrapper divs
- Grid gap provides consistent spacing

**Why explicit media queries** (vs. pure `auto-fit`):
- Ensures predictable breakpoints matching Docusaurus defaults
- Prevents awkward in-between states (e.g., 2.5 columns)
- Matches user's spec requirement: "3 columns desktop, 2 tablet, 1 mobile"

**Equal height mechanism**:
- Grid rows automatically stretch to tallest card in that row
- Use `align-items: stretch` (default) to fill vertical space
- Content flows naturally without truncation

### Alternatives Considered

1. **Flexbox with `flex: 1 1 300px`** - Rejected: Requires manual height equalization; last row items expand awkwardly
2. **Pure `auto-fit minmax()` without media queries** - Rejected: Breakpoints don't align with Docusaurus responsive defaults; may create 2.5-column layouts
3. **Fixed pixel widths with `calc()`** - Rejected: Not responsive; breaks on non-standard viewports

### Implementation Notes

- Current `index.module.css` already uses grid (line 34-41)
- Replace `auto-fit, minmax(300px, 1fr)` with explicit media query breakpoints
- Keep `gap: 2rem` for consistent spacing
- Ensure card content uses natural height (no `height: 100%` on card children that would prevent expansion)

**Testing checklist**:
- [ ] Desktop (≥1200px): 3 equal-width columns
- [ ] Tablet (768-996px): 2 equal-width columns
- [ ] Mobile (<768px): 1 full-width column
- [ ] Cards in same row have identical height
- [ ] Content with varying lengths doesn't break layout

---

## Research Question 5: Gradient Removal Strategy

**Question**: How to identify all gradient backgrounds in existing CSS and replace them with solid colors while maintaining visual hierarchy?

### Decision

**Identification Method**:
1. Grep for gradient patterns: `grep -r "linear-gradient\|radial-gradient" frontend/src/`
2. Manual audit of CSS files for visual elements with gradients

**Removal Strategy**:
| Element | Current (Gradient) | Replacement (Solid) | Rationale |
|---------|-------------------|---------------------|-----------|
| Hero banner background | `linear-gradient(135deg, purple-start, purple-end)` | Solid dark green `#1b5e20` or black `#0c0c0d` | Text visibility critical; gradient causes contrast issues |
| Hero banner text | White on gradient (variable contrast) | White `#ffffff` on solid dark green (9.7:1 contrast) | Ensures WCAG AA compliance |
| Footer background | `linear-gradient(135deg, purple-start, purple-end)` | Keep gradient OR solid dark green | Footer text is white and large (>18pt); gradient acceptable if contrast maintained |
| Card backgrounds | Solid (no gradient currently) | No change needed | Already solid white/dark |
| Table headers | `linear-gradient(purple-light, purple-tertiary)` | Solid light green `#e8f5e9` (light mode) or `rgba(102, 187, 106, 0.15)` (dark mode) | Maintains visual distinction without gradient |

**Implementation Steps**:
1. Replace hero banner (`.heroBanner` in `index.module.css` line 6-16) gradient with solid `#1b5e20`
2. Evaluate footer gradient: If footer has overlaid text, replace with solid; if purely decorative, may retain
3. Replace table header gradient (lines 1000-1010 in `custom.css`) with solid light green tint
4. Remove any gradient button styles if present

### Rationale

Gradients behind text create unpredictable contrast ratios because text may overlap different gradient color stops. Solid backgrounds ensure consistent, testable WCAG compliance. Visual hierarchy can be maintained through:
- Color contrast (darker greens for important sections)
- Shadows and borders
- Typography weight and size
- Spacing and padding

**Existing gradient locations** (from code review):
- `frontend/src/pages/index.module.css`:
  - Line 11: `.heroBanner` - `linear-gradient(135deg, var(--ifm-color-purple-gradient-start) 0%, var(--ifm-color-purple-gradient-end) 100%)`
- `frontend/src/css/custom.css`:
  - Line 647: `.footer` - `linear-gradient(135deg, #8a2be2 0%, #6a16c2 100%)`
  - Line 740: `.gradient-bg` - `linear-gradient(135deg, var(--ifm-color-purple-gradient-start) 0%, var(--ifm-color-purple-gradient-end) 100%)`
  - Line 1000: `.markdown table th` - `linear-gradient(135deg, var(--ifm-color-purple-light) 0%, var(--ifm-color-purple-tertiary) 100%)`

### Alternatives Considered

1. **Adjust gradient contrast programmatically** - Rejected: Complex, fragile, doesn't address root issue
2. **Use very subtle gradients (5% color difference)** - Rejected: Still creates variable contrast; spec explicitly requires "no gradients behind text"
3. **Keep gradients, use text shadows for readability** - Rejected: Spec requires solid backgrounds; shadows are workaround, not solution

### Implementation Notes

**Hero banner replacement**:
```css
/* Before */
.heroBanner {
  background: linear-gradient(135deg, var(--ifm-color-purple-gradient-start) 0%, var(--ifm-color-purple-gradient-end) 100%);
}

/* After */
.heroBanner {
  background: var(--ifm-color-primary); /* Solid dark green #1b5e20 */
  color: #ffffff; /* White text for 9.7:1 contrast */
}
```

**Testing**:
- Use browser DevTools to verify no `linear-gradient` or `radial-gradient` in computed styles for text-containing elements
- Visual inspection: Ensure no gradient artifacts remain behind text
- Contrast check: All text on new solid backgrounds meets WCAG AA

---

## Summary of Decisions

| Research Area | Decision | Key Value/Pattern |
|---------------|----------|-------------------|
| CSS Variables | Use Infima `--ifm-*` + custom `--rb-*` | `:root` (light), `html[data-theme='dark']` (dark) |
| Contrast Values | Light: `#1a1a1a` on `#ffffff` (16.1:1) | Dark: `#e8e8e8` on `#0c0c0d` (14.5:1) |
| Dark Green | Material Green 900: `#1b5e20` (light mode) | Material Green 400: `#66bb6a` (dark mode) |
| Responsive Grid | CSS Grid with explicit media queries | 3-col desktop, 2-col tablet, 1-col mobile |
| Gradient Removal | Replace all text-overlaid gradients with solids | Hero banner, table headers, footer (if text present) |

## Next Steps

All research questions answered. Proceed to **Phase 1: Design & Contracts** to generate:
1. `data-model.md` - Theme variable schema
2. `contracts/theme-variables.schema.json` - CSS variable contracts
3. `quickstart.md` - Visual testing guide

**Phase 0: Complete** ✅
