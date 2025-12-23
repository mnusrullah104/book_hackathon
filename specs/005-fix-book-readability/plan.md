# Implementation Plan: Fix & Redesign Book UI for Readability

**Branch**: `005-fix-book-readability` | **Date**: 2025-12-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-fix-book-readability/spec.md`

## Summary

Fix critical readability issues in the textbook UI by implementing high-contrast text colors, fixing sidebar navigation visibility, and ensuring WCAG AA compliance across all themes. This is a CSS-only change to `src/css/custom.css`.

**Core Problem**: Text blends into backgrounds due to missing explicit text color definitions and inappropriate use of purple accent colors for body content.

**Solution**: Add explicit high-contrast text color variables and apply them consistently across body text, headings (H2-H6), sidebar navigation, and code blocks.

## Technical Context

**Language/Version**: CSS3, Docusaurus 3.9.2, React 18, Node.js 18+
**Primary Dependencies**: Docusaurus, Prism (syntax highlighting), Infima CSS framework
**Storage**: N/A (CSS-only, no data persistence)
**Testing**: Manual visual verification, Lighthouse accessibility audit, WCAG contrast checker
**Target Platform**: Web (all modern browsers), responsive 320px-2560px
**Project Type**: Web (static site)
**Performance Goals**: Page load <3s, no layout shift from CSS changes
**Constraints**: WCAG AA contrast (4.5:1 body text, 3:1 large text), preserve purple brand identity
**Scale/Scope**: Single CSS file (~1,200 lines), affects all pages

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Spec-first development | ✅ PASS | Spec created at `/specs/005-fix-book-readability/spec.md` |
| Technical accuracy | ✅ PASS | WCAG AA standards documented with specific contrast ratios |
| Clarity for developers | ✅ PASS | CSS variable naming clear and documented |
| AI-native architecture | ✅ N/A | Frontend CSS, no AI components |
| End-to-end transparency | ✅ PASS | All changes in single file with clear documentation |
| Modular, non-filler content | ✅ PASS | Only necessary CSS changes, no decorative additions |

**Gate Status**: PASS - Proceed with implementation

## Project Structure

### Documentation (this feature)

```text
specs/005-fix-book-readability/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: WCAG research, color analysis
├── data-model.md        # Phase 1: CSS variable structure
├── quickstart.md        # Phase 1: Development setup
├── checklists/
│   └── requirements.md  # Requirements tracking (45 items)
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
src/
├── css/
│   └── custom.css       # PRIMARY FILE - All changes here (1,149 lines)
├── pages/               # Homepage (hero section)
└── theme/               # Docusaurus theme overrides (no changes needed)

docs/                    # Markdown content (no changes needed)
```

**Structure Decision**: This is a frontend-only static site using Docusaurus. All styling changes are isolated to `src/css/custom.css`. No structural changes needed.

## Implementation Approach

### Phase 1: Foundation - Text Color Variables (Critical)

Add explicit text color CSS variables to `:root` and `html[data-theme='dark']`:

```css
/* Add to :root (lines ~35-50) */
--rb-text-body: #1a1a1a;
--rb-text-heading: #2d2d2d;
--rb-text-muted: #4a4a4a;

/* Add to html[data-theme='dark'] (lines ~96-145) */
--rb-text-body: #e8e8e8;
--rb-text-heading: #f0f0f0;
--rb-text-muted: #b0b0b0;
```

### Phase 2: Apply Body Text Colors

Override Docusaurus defaults to use explicit text colors:

```css
/* Body text */
.markdown, .main-wrapper p {
  color: var(--rb-text-body);
}
```

### Phase 3: Fix Heading Colors (H2-H6)

Keep H1 purple for brand identity, fix H2-H6 for readability:

```css
/* Lines 1071-1127: Change heading colors */
.markdown h2, .markdown h3, .markdown h4, .markdown h5, .markdown h6 {
  color: var(--rb-text-heading);
}
/* Keep H1 purple but ensure contrast */
.markdown h1 {
  color: var(--ifm-color-primary); /* Already defined with good contrast */
}
```

### Phase 4: Fix Sidebar Navigation

Replace purple text colors with high-contrast neutral:

```css
/* Lines 511-576: Sidebar styling */
.menu__link {
  color: var(--rb-text-body);
}
.menu__link--active {
  color: var(--ifm-color-primary); /* Keep purple for active only */
}
```

### Phase 5: Fix Code Blocks

Remove gradient backgrounds, use flat high-contrast colors:

```css
/* Lines 247-313: Code blocks */
.prism-code {
  background: var(--rb-bg-code);
  color: var(--rb-text-body);
}
```

### Phase 6: Hero/Header (if applicable)

Ensure hero text has sufficient contrast:

```css
/* Hero section */
.hero__title, .hero__subtitle {
  color: #ffffff; /* On purple/dark backgrounds */
  text-shadow: none; /* Remove any shadows that reduce clarity */
}
```

### Phase 7: Mobile Verification

Test at all breakpoints (320px, 576px, 768px, 996px) to ensure:
- Text remains readable
- Touch targets are adequate (44x44px minimum)
- No horizontal scrolling for text

## Key Files to Modify

| File | Lines | Changes |
|------|-------|---------|
| `src/css/custom.css` | 35-50 | Add light mode text variables |
| `src/css/custom.css` | 96-145 | Add dark mode text variables |
| `src/css/custom.css` | 429-447 | Apply body text colors |
| `src/css/custom.css` | 511-576 | Fix sidebar text colors |
| `src/css/custom.css` | 1050-1127 | Fix heading colors (H2-H6) |
| `src/css/custom.css` | 247-313 | Fix code block backgrounds |

## Complexity Tracking

No violations to track. This is a straightforward CSS-only change with:
- Single file modification
- No new dependencies
- No architectural changes
- Backward compatible (existing classes preserved)

## Verification Plan

1. **Lighthouse Audit**: Run accessibility audit, expect 90+ score
2. **Contrast Checker**: Verify all text meets WCAG AA (4.5:1 body, 3:1 headings)
3. **Manual Testing**:
   - Light mode readability
   - Dark mode readability
   - Mobile (320px, 576px, 768px)
   - Sidebar navigation clarity
   - Code block syntax highlighting
4. **Cross-Browser**: Chrome, Firefox, Safari (if available)

## Next Steps

Run `/sp.tasks` to generate the implementation task list.
