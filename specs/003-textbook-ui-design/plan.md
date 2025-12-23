# Implementation Plan: Textbook UI Design for Physical AI & Humanoid Robotics

**Branch**: `003-textbook-ui-design` | **Date**: 2025-12-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-textbook-ui-design/spec.md`

## Summary

Design and refine the Docusaurus-based textbook UI to provide a clean, professional, and highly readable experience for technical content about Physical AI and Humanoid Robotics. The implementation focuses on enhancing the existing purple theme with typography refinements, responsive improvements, and consistent styling for code blocks, callouts, and navigation. No new dependencies or server-side features required.

## Technical Context

**Language/Version**: JavaScript/CSS (Docusaurus 3.9.2, React 18, Node.js 18+)
**Primary Dependencies**: @docusaurus/core ^3.9.2, @docusaurus/preset-classic ^3.9.2, prism-react-renderer ^2.3.0
**Storage**: N/A (Static site, content in Markdown files)
**Testing**: Manual visual testing, browser DevTools responsive testing, Lighthouse accessibility audits
**Target Platform**: Web (all modern browsers), deployed on Vercel
**Project Type**: Web (frontend-only static site)
**Performance Goals**: Page load <3s, First Contentful Paint <1.5s, Lighthouse Performance >90
**Constraints**: WCAG AA contrast compliance, mobile-first responsive (320px-2560px), no heavy animations
**Scale/Scope**: 4 modules, 12+ chapters, single codebase

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **Spec-first development** | ✅ PASS | Formal spec created at specs/003-textbook-ui-design/spec.md with 23 functional requirements and 8 success criteria |
| **Technical accuracy and reproducibility** | ✅ PASS | All styling changes are CSS-based, fully reproducible with existing Docusaurus setup |
| **Clarity for developers** | ✅ PASS | UI focuses on readability for technical content with code examples |
| **AI-native architecture** | ⚪ N/A | This feature is UI-only; no AI/RAG components involved |
| **End-to-end transparency** | ✅ PASS | All changes are visible CSS customizations, deployable via existing Vercel pipeline |
| **Modular, non-filler content** | ✅ PASS | Enhances existing theme without adding unnecessary complexity |

**Gate Status**: PASS - No violations. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/003-textbook-ui-design/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (minimal - UI entities only)
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
src/
├── css/
│   └── custom.css           # Primary stylesheet (existing, ~1149 lines)
├── theme/
│   ├── DocSidebar/
│   │   └── index.js         # Custom sidebar component (existing)
│   ├── MDXComponents/
│   │   ├── index.js         # MDX component overrides (existing)
│   │   └── CodeBlock.js     # Custom code block (existing)
│   └── Root.js              # Theme provider wrapper (existing)
├── components/
│   └── ThemeToggle.js       # Theme toggle component (existing)
├── contexts/
│   └── ThemeContext.js      # Theme state management (existing)
└── pages/
    ├── index.md             # Landing page
    └── about.js             # About page

docs/                        # Book content (Markdown files)
├── introduction.md
├── module-1/                # Module 1 chapters
├── module-2/                # Module 2 chapters
├── isaac-robot-brain/       # Module 3 chapters
└── vla-integration/         # Module 4 chapters

docusaurus.config.js         # Docusaurus configuration
sidebars.js                  # Sidebar navigation structure
```

**Structure Decision**: Existing web/frontend-only structure. All UI enhancements will be made to `src/css/custom.css` and potentially `src/theme/` components. No new directories required.

## Complexity Tracking

> No Constitution Check violations to justify.

| Aspect | Complexity Level | Rationale |
|--------|------------------|-----------|
| Theme Customization | Low | Enhancing existing CSS, not replacing |
| Responsive Design | Medium | Must handle 320px-2560px range |
| Accessibility | Medium | WCAG AA compliance verification needed |
| Component Changes | Low | Minor refinements to existing components |

## Design Decisions

### DD-001: Retain Existing Purple Theme

**Decision**: Retain and refine the existing purple theme rather than replacing it.

**Rationale**: The existing theme has 1,149 lines of well-structured CSS with comprehensive dark/light mode support, responsive breakpoints, and professional styling. Replacing it would require significant rework with minimal incremental value for the hackathon timeline.

**Alternatives Rejected**:
- Gray/blue neutral academic theme: High effort, delays delivery
- Complete redesign: Unnecessary given existing quality

### DD-002: CSS-Only Enhancements

**Decision**: All visual refinements will be CSS-only modifications to custom.css.

**Rationale**: Minimizes risk, maintains compatibility with Docusaurus updates, and ensures reproducibility. No new React components or JavaScript required.

### DD-003: Mobile-First Verification

**Decision**: Verify and enhance existing responsive breakpoints rather than redesigning.

**Rationale**: The existing theme already includes mobile breakpoints. Focus on verification and minor adjustments.

## Implementation Approach

### Phase 0: Research (Completed in this plan)

The technical context is fully understood:
- Docusaurus 3.9.2 with React 18
- Existing purple theme with comprehensive CSS variables
- Dark/light mode already implemented
- Sidebar navigation already configured
- Vercel deployment working

### Phase 1: Design Refinements

Focus areas based on spec requirements:

1. **Typography Refinements** (FR-015 to FR-017)
   - Verify heading hierarchy styling
   - Ensure 65-80 character line width
   - Optimize line-height for extended reading

2. **Code Block Enhancements** (FR-018 to FR-020)
   - Verify Prism syntax highlighting for Python, ROS, YAML
   - Ensure horizontal scrolling for long lines
   - Maintain contrast in both themes

3. **Callout/Admonition Styling** (FR-021)
   - Review existing admonition styles
   - Ensure visual distinction without disruption

4. **Responsive Verification** (FR-006 to FR-009)
   - Test breakpoints at 320px, 768px, 1024px, 1440px, 2560px
   - Verify touch target sizing
   - Confirm sidebar collapse behavior

5. **Accessibility Audit** (FR-014, SC-003, SC-005)
   - Run Lighthouse accessibility audit
   - Verify WCAG AA contrast ratios
   - Test keyboard navigation

### Implementation Files

| File | Changes |
|------|---------|
| `src/css/custom.css` | Typography, spacing, contrast refinements |
| `src/theme/DocSidebar/index.js` | Verify/enhance mobile collapse |
| `docusaurus.config.js` | No changes expected |

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| CSS changes break existing styling | Medium | Test each change in both themes before committing |
| Responsive breakpoints insufficient | Low | Existing breakpoints are comprehensive; verify only |
| Accessibility gaps | Medium | Run Lighthouse early; address issues incrementally |

## Success Verification

All success criteria from spec.md will be verified:

- SC-001: Navigation within 3 clicks - Manual verification
- SC-002: Layout 320px-2560px - Browser DevTools responsive mode
- SC-003: WCAG AA contrast - Lighthouse audit
- SC-004: Page load <3s - Lighthouse performance
- SC-005: Keyboard accessibility - Manual testing
- SC-006: Reading comfort - Self-assessment (hackathon context)
- SC-007: Judge navigation - Structured walkthrough
- SC-008: Mobile reading - Device testing

## Next Steps

1. Run `/sp.tasks` to generate the implementation task list
2. Execute tasks in priority order (P1 stories first)
3. Verify each success criterion after implementation
4. Create PR for review
