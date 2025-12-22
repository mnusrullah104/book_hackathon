# Implementation Plan: Frontend UI Fix & Consistency

**Branch**: `007-frontend-ui-fix` | **Date**: 2025-12-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-frontend-ui-fix/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Fix critical UI issues in the Docusaurus-based book website to ensure text readability in light and dark modes, create consistent homepage cards, establish a three-color design system (white/black/dark-green), and ensure responsive layout consistency across all devices. This is a frontend-only refactoring that normalizes CSS variables, removes problematic gradients, and standardizes component styling for a professional technical documentation aesthetic.

**User-provided plan input:**
- Normalize theme colors using Docusaurus CSS variables for light and dark mode
- Remove gradients and fix text/background contrast on homepage
- Redesign homepage cards with uniform size, color, and spacing using responsive grid
- Apply consistent typography, spacing, and layout across all pages
- Test UI in light mode, dark mode, and mobile view to ensure text visibility

## Technical Context

**Language/Version**: JavaScript (ES6+), CSS3 with CSS Custom Properties
**Primary Dependencies**: Docusaurus 2.x (already installed), React 17+ (Docusaurus peer dependency)
**Storage**: N/A (static site generation, no database)
**Testing**: Manual visual testing in light/dark modes, browser DevTools for contrast ratio verification, responsive design testing at breakpoints (320px, 768px, 1024px, 1440px)
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge - modern evergreen versions)
**Project Type**: Web (frontend only, static site)
**Performance Goals**: Theme switching <300ms, no layout shift (CLS = 0), paint time <100ms for CSS changes
**Constraints**: Must use Docusaurus theme system, no breaking changes to existing markdown content, maintain existing routing and navigation structure
**Scale/Scope**: ~10 CSS files affected, 3 core pages (homepage + 2 doc pages for testing), 1 homepage component (cards), sidebar and navbar styling

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Summary

✅ **Spec-first development**: Feature has complete specification in `spec.md` with functional requirements, success criteria, and acceptance scenarios

✅ **Technical accuracy and reproducibility**: CSS changes are deterministic and reproducible; all color values defined via CSS variables for consistency

✅ **Clarity for developers and AI engineers**: Plan focuses on CSS refactoring with clear file targets and measurable outcomes (contrast ratios, dimensions)

⚠️ **AI-native architecture**: NOT APPLICABLE - This is a CSS/UI styling feature with no AI/RAG/vector DB components; constitution principle does not apply to frontend presentation layer

✅ **End-to-end transparency**: All CSS changes will be version controlled with clear diffs; theme variables provide observable system state

✅ **Modular, non-filler content**: Focuses only on essential CSS fixes; no scope creep beyond readability, consistency, and responsive design

### Constitution Gates

| Gate | Status | Notes |
|------|--------|-------|
| Formal specification exists | ✅ PASS | Complete spec.md with 15 functional requirements, 10 success criteria |
| No code without spec | ✅ PASS | Implementation follows specification |
| Reproducible setup | ✅ PASS | CSS changes are deterministic; existing Docusaurus build process unchanged |
| AI-native patterns | ⚠️ N/A | Frontend styling feature; no AI integration required |
| Transparent processes | ✅ PASS | Git-tracked CSS files; browser DevTools for verification |
| Production-quality only | ✅ PASS | Professional CSS with proper variable usage, no placeholder styles |

**Overall**: ✅ PASS (1 N/A gate is justified for non-AI frontend work)

## Project Structure

### Documentation (this feature)

```text
specs/007-frontend-ui-fix/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - CSS variable patterns, contrast guidelines
├── data-model.md        # Phase 1 output - Theme variable schema, breakpoint definitions
├── quickstart.md        # Phase 1 output - Testing checklist for visual verification
├── contracts/           # Phase 1 output - CSS variable contracts (light/dark mode)
│   └── theme-variables.schema.json
├── checklists/          # Existing quality checklist
│   └── requirements.md
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/                           # Docusaurus site root
├── src/
│   ├── css/
│   │   └── custom.css             # PRIMARY TARGET: Theme variables, global styles
│   ├── pages/
│   │   ├── index.md               # Homepage markdown content
│   │   └── index.module.css       # PRIMARY TARGET: Homepage card styling
│   ├── components/
│   │   └── (existing components)  # Review for hardcoded colors (low priority)
│   └── theme/
│       └── (Docusaurus overrides)  # Review if custom theme components exist
├── docusaurus.config.js           # Site config (may need color theme adjustments)
├── static/                        # Static assets (no changes expected)
└── docs/                          # Markdown content (no changes expected)

specs/007-frontend-ui-fix/         # Planning artifacts (this directory)
```

**Structure Decision**: This is a frontend-only refactoring within the existing Docusaurus project structure. The primary changes target CSS files in `frontend/src/css/` and `frontend/src/pages/`. No new directories or components are needed; we're modifying existing stylesheets to fix readability and consistency issues.

**Key Files for Implementation**:
1. `frontend/src/css/custom.css` - Contains all theme variables (`:root`, `html[data-theme='dark']`), typography rules, and global component styles
2. `frontend/src/pages/index.module.css` - Homepage card styles that need consistency fixes
3. `frontend/docusaurus.config.js` - May contain theme configuration that needs alignment with new color system

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

N/A - No constitution violations. The AI-native architecture principle is marked N/A because this feature is purely frontend presentation layer styling and does not involve AI/RAG/vector DB integration, which is the focus of that constitutional principle. All other principles are satisfied.

## Phase 0: Research

### Research Questions

1. **Docusaurus CSS Variable System**: What are the standard `--ifm-*` variables for colors, typography, and spacing? How do light/dark mode overrides work in Docusaurus?

2. **WCAG AA Contrast Requirements**: What specific color values meet 4.5:1 contrast for normal text and 3:1 for large text on white and black backgrounds?

3. **Dark Green Color Selection**: What hex value for "dark green" provides professional technical documentation aesthetic while meeting WCAG AA contrast on both light and dark backgrounds?

4. **CSS Grid Best Practices**: What responsive grid patterns work best for equal-height cards across breakpoints (desktop 3-col, tablet 2-col, mobile 1-col)?

5. **Gradient Removal Strategy**: How to identify all gradient backgrounds in existing CSS and replace them with solid colors while maintaining visual hierarchy?

### Research Output Location

See `research.md` for detailed findings, decisions, rationale, and alternatives considered for each research question above.

## Phase 1: Design & Contracts

### Data Model

See `data-model.md` for:
- **Theme Variable Schema**: Complete list of CSS custom properties for light mode, dark mode, and responsive breakpoints
- **Breakpoint Definitions**: Mobile (<768px), Tablet (768px-996px), Desktop (≥1200px)
- **Component State Model**: Card states (default, hover, focus), theme states (light, dark)

### API Contracts

See `contracts/theme-variables.schema.json` for:
- **CSS Variable Contract**: Defines all theme variables with allowed values, WCAG contrast requirements, and usage guidelines
- **Color Palette Contract**: White (#ffffff), Black (#0c0c0d or #121212), Dark Green (research-determined hex value)
- **Typography Contract**: Font sizes, line heights, line length constraints (75ch max)

### Quickstart Guide

See `quickstart.md` for:
- **Visual Testing Checklist**: Step-by-step manual testing guide for light mode, dark mode, and responsive breakpoints
- **Contrast Verification**: Using WebAIM Contrast Checker and browser DevTools to verify WCAG AA compliance
- **Card Consistency Checks**: Measuring card dimensions, backgrounds, borders, and shadows in DevTools
- **Responsive Testing**: Viewport sizes and expected layout behaviors at each breakpoint

## Implementation Strategy

### Approach

This is a **refactoring and standardization** effort, not new feature development. The strategy follows a systematic CSS audit → normalize → test workflow:

1. **Audit Phase**: Identify all color values, gradients, and inconsistent styles in current CSS
2. **Normalize Phase**: Replace hardcoded colors with theme variables, remove gradients, standardize card styling
3. **Test Phase**: Verify contrast ratios, visual consistency, and responsive behavior
4. **Refinement Phase**: Adjust color values if contrast requirements not met, fine-tune spacing/sizing

### Key Technical Decisions

**Decision 1: Dark Green Color Selection**
- **Context**: User requirement specifies "dark green" but current implementation uses purple (#8a2be2)
- **Decision**: [TO BE DETERMINED IN RESEARCH] - Select a dark green hex value (e.g., #2d6a4f, #1b4332, #006d32) that meets WCAG AA on both white and black backgrounds
- **Rationale**: Professional technical documentation sites (GitHub, GitLab docs, VS Code docs) use muted greens that convey reliability without being garish
- **Impact**: All interactive elements (links, buttons, active menu items) will use this green; requires comprehensive CSS update

**Decision 2: Gradient Removal Scope**
- **Context**: Spec requires "no gradients behind text" but existing CSS has purple gradients in hero banner, footer, tables
- **Decision**: Remove gradients from hero banner and any areas with overlaid text; evaluate footer gradients case-by-case (footer may retain subtle gradient if no text overlap)
- **Rationale**: Gradients behind text create unpredictable contrast; hero banner gradient causes reported visibility issues
- **Impact**: Hero banner becomes solid background (dark green or black); text uses high-contrast colors

**Decision 3: Card Height Strategy**
- **Context**: Spec requires "identical dimensions" but card content varies in length
- **Decision**: Use CSS Grid with `grid-auto-rows: 1fr` for equal height within rows; allow vertical expansion if content differs significantly across rows
- **Rationale**: Enforcing absolute identical height across all cards may truncate content; equal height per row provides visual consistency
- **Impact**: Cards in same row match height; different rows may vary if content length differs significantly

**Decision 4: Theme Variable Migration**
- **Context**: Some components may have hardcoded colors (e.g., `color: #8a2be2`)
- **Decision**: Create comprehensive theme variable set in `:root`, then find/replace all hardcoded colors with `var(--theme-variable-name)`
- **Rationale**: Ensures theme switching works correctly; makes future color adjustments trivial
- **Impact**: One-time refactoring effort; improves maintainability

### Testing Strategy

**Visual Regression Testing**:
- Manual comparison of before/after screenshots at each breakpoint
- Focus on homepage cards, doc page readability, sidebar navigation

**Contrast Verification**:
- Use WebAIM Contrast Checker for all text/background pairs
- Target: 4.5:1 minimum for normal text, 3:1 for large text (WCAG AA)

**Responsive Testing**:
- Test at 320px (small mobile), 768px (tablet), 1024px (desktop), 1440px (large desktop)
- Verify card grid reflows correctly: 1-col mobile, 2-col tablet, 3-col desktop

**Cross-Browser Testing**:
- Chrome (primary), Firefox, Safari, Edge
- Verify CSS custom property support and theme switching

**Manual Testing Checklist** (detailed in `quickstart.md`):
- [ ] Light mode: All text readable with high contrast
- [ ] Dark mode: All text readable with high contrast
- [ ] Homepage cards: Identical size, background, border, shadow
- [ ] Card hover states: Consistent animation across all cards
- [ ] Responsive grid: Correct column count at each breakpoint
- [ ] Theme switching: <300ms transition, no FOUC
- [ ] Line length: Body text ≤75 characters wide
- [ ] Sidebar: Consistent styling with homepage

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Dark green doesn't meet WCAG AA contrast on black background | Medium | High | Test multiple green shades in research; use contrast calculator before implementing |
| Gradient removal makes hero banner visually flat | Medium | Low | Use subtle shadow/border effects; ensure typography is strong enough to carry visual interest |
| Card content varies too much for equal height | Low | Medium | Use `min-height` instead of fixed height; allow vertical expansion |
| Hardcoded colors exist in React components (JSX) | Medium | Medium | Grep for hex colors in `.js` and `.jsx` files; refactor to use CSS variables via className |
| Theme switching causes FOUC | Low | Medium | Ensure Docusaurus theme persistence is enabled; test theme toggle thoroughly |

### Open Questions for Research Phase

1. What specific dark green hex value meets WCAG AA on both `#ffffff` and `#0c0c0d`?
2. Are there any Docusaurus-specific CSS variable naming conventions we should follow?
3. What's the best CSS Grid pattern for equal-height cards that gracefully handles content variance?
4. Are there any third-party Docusaurus plugins that might conflict with custom CSS variables?
5. What browser DevTools workflow is most efficient for verifying contrast ratios during development?

These questions will be answered in `research.md` (Phase 0 output).

## Next Steps

After this plan is complete:

1. **Phase 0**: Generate `research.md` by answering research questions with decisions, rationale, and alternatives
2. **Phase 1**: Generate `data-model.md` (theme variable schema), `contracts/` (CSS variable contracts), `quickstart.md` (testing guide)
3. **Phase 2**: Run `/sp.tasks` to break down implementation into atomic, testable tasks
4. **Implementation**: Execute tasks following TDD workflow (red-green-refactor)
5. **Validation**: Complete manual testing checklist from `quickstart.md`

**Command to proceed**: `/sp.tasks` (after this plan is reviewed and approved)
