# Implementation Tasks: Frontend UI Fix & Consistency

**Feature**: 007-frontend-ui-fix
**Branch**: `007-frontend-ui-fix`
**Date**: 2025-12-22

## Overview

This document breaks down the Frontend UI Fix & Consistency feature into atomic, testable tasks organized by user story. Each user story represents an independently testable increment that delivers value.

**Total Tasks**: 24 tasks across 6 phases
**Parallelization Opportunities**: 12 tasks marked [P] can run in parallel
**MVP Scope**: User Story 1 (Phase 3) - Text Readability in All Modes

## Task Format Legend

```
- [ ] [TaskID] [P?] [Story?] Description with file path
```

- **TaskID**: Sequential identifier (T001, T002, T003...)
- **[P]**: Parallelizable task (can run concurrently with other [P] tasks in same phase)
- **[Story]**: User story label (US1, US2, US3, US4) - indicates which story the task serves
- **Description**: Clear action with exact file path

## User Story Mapping

| Story | Priority | Description | Phase | Tasks |
|-------|----------|-------------|-------|-------|
| US1 | P1 | Text Readability in All Modes | Phase 3 | T004-T008 |
| US2 | P2 | Consistent Homepage Cards | Phase 4 | T009-T013 |
| US3 | P3 | Color Harmony with Three-Color System | Phase 5 | T014-T018 |
| US4 | P3 | Responsive Layout Consistency | Phase 6 | T019-T022 |

---

## Phase 1: Setup (No User Story Label)

**Objective**: Prepare development environment and baseline CSS audit

**Tasks**:

- [X] T001 Create backup of current CSS files (frontend/src/css/custom.css, frontend/src/pages/index.module.css) to specs/007-frontend-ui-fix/backups/
- [X] T002 [P] Run grep audit for hardcoded purple colors (#8a2be2, #9a46e8, #7a1ad2, #6a16c2) in frontend/src/ and document findings in specs/007-frontend-ui-fix/audit-purple-colors.txt
- [X] T003 [P] Run grep audit for gradient usage (linear-gradient, radial-gradient) in frontend/src/css/ and frontend/src/pages/ and document findings in specs/007-frontend-ui-fix/audit-gradients.txt

**Duration Estimate**: 30 minutes
**Acceptance**: Backup files exist, audit reports generated with line numbers and file paths

---

## Phase 2: Foundational (No User Story Label)

**Objective**: No foundational tasks required - all user stories are independent

**Tasks**: None

**Note**: This feature has no blocking prerequisites. Each user story can be implemented independently using the existing CSS variable system.

---

## Phase 3: User Story 1 - Text Readability in All Modes (P1)

**Story Goal**: Ensure all text content is readable with WCAG AA contrast in both light and dark modes

**Independent Test**: Toggle between light/dark modes and verify all text (hero, cards, navigation, body) has sufficient contrast (4.5:1 for normal text, 3:1 for large text) using WebAIM Contrast Checker

**Tasks**:

- [X] T004 [P] [US1] Update light mode text colors in frontend/src/css/custom.css :root section - set --rb-text-body: #1a1a1a (16.1:1 contrast), --rb-text-heading: #2d2d2d (12.6:1), --rb-text-muted: #4a4a4a (8.8:1)
- [X] T005 [P] [US1] Update dark mode text colors in frontend/src/css/custom.css html[data-theme='dark'] section - set --rb-text-body: #e8e8e8 (14.5:1 contrast), --rb-text-heading: #f0f0f0 (16.8:1), --rb-text-muted: #b0b0b0 (9.2:1)
- [X] T006 [US1] Apply text color variables to card titles and descriptions in frontend/src/pages/index.module.css - replace hardcoded colors with var(--rb-text-heading) for .cardTitle and var(--rb-text-body) for .cardDescription
- [X] T007 [US1] Apply text color variables to sidebar navigation in frontend/src/css/custom.css - ensure .menu__link uses var(--rb-sidebar-text) in both light and dark modes
- [X] T008 [US1] Verify hero banner text contrast in frontend/src/pages/index.module.css - ensure .heroBanner text is white (#ffffff) on solid dark green background (9.7:1 contrast)

**Testing Checklist** (from quickstart.md Test Suite 1):
- [ ] Light mode: Hero text, card text, sidebar links all pass 4.5:1 contrast
- [ ] Dark mode: All text elements pass 4.5:1 contrast
- [ ] WebAIM Contrast Checker verification for each text/background pair

**Acceptance Criteria**:
- All text elements achieve minimum 4.5:1 contrast ratio (normal text) or 3:1 (large text)
- No hardcoded text colors remain (all use CSS variables)
- Theme switching maintains readability in both modes

**Dependencies**: None (can start immediately)
**Parallelization**: T004 and T005 can run in parallel (different CSS blocks)

---

## Phase 4: User Story 2 - Consistent Homepage Cards (P2)

**Story Goal**: Homepage cards have uniform dimensions, backgrounds, borders, shadows, and hover states

**Independent Test**: Load homepage at desktop (≥1200px), tablet (768px-996px), and mobile (<768px) breakpoints and verify all cards have identical styling using browser DevTools measurements

**Tasks**:

- [X] T009 [P] [US2] Standardize card grid layout in frontend/src/pages/index.module.css - replace .cardContainer grid with explicit media queries: 3 columns desktop (≥1200px), 2 columns tablet (768-996px), 1 column mobile (<768px), gap: 2rem
- [X] T010 [P] [US2] Normalize card backgrounds in frontend/src/pages/index.module.css - set .card background-color: var(--ifm-background-color) for light mode, add html[data-theme='dark'] .card override with background-color: var(--ifm-card-background-color)
- [X] T011 [P] [US2] Standardize card borders in frontend/src/pages/index.module.css - set .card border: 1px solid var(--ifm-color-emphasis-300) for light mode, add dark mode override with border-color: var(--ifm-color-emphasis-700)
- [X] T012 [P] [US2] Standardize card shadows in frontend/src/pages/index.module.css - set .card box-shadow: var(--ifm-card-shadow) (defined as 0 10px 30px rgba(0,0,0,0.08) in light, rgba(0,0,0,0.25) in dark)
- [X] T013 [US2] Standardize card hover states in frontend/src/pages/index.module.css - ensure .card:hover has transform: translateY(-5px) and box-shadow: 0 20px 40px rgba(0,0,0,0.15) with transition: all 0.3s ease

**Testing Checklist** (from quickstart.md Test Suite 2):
- [ ] Desktop: All 3 cards have identical width, padding, border, shadow
- [ ] Tablet: 2 columns, cards in same row have identical height
- [ ] Mobile: 1 column, all cards have identical styling
- [ ] Hover: All cards lift 5px with enhanced shadow

**Acceptance Criteria**:
- All cards have identical computed dimensions within 1px tolerance at each breakpoint
- Cards use only theme variables for colors (no hardcoded hex values)
- Hover animation is smooth and consistent across all cards
- Responsive grid reflows correctly at breakpoint thresholds

**Dependencies**: None (US1 and US2 are independent)
**Parallelization**: T009-T012 can run in parallel (different CSS properties on same element)

---

## Phase 5: User Story 3 - Color Harmony with Three-Color System (P3)

**Story Goal**: Replace purple color scheme with dark green (Material Design Green), remove gradients behind text, establish white/black/dark-green palette

**Independent Test**: Audit all pages and verify only approved colors (white #ffffff, black #0c0c0d, dark green #1b5e20) are used, with zero gradient backgrounds behind text

**Tasks**:

- [X] T014 [P] [US3] Replace purple primary colors with dark green in frontend/src/css/custom.css :root section - set --ifm-color-primary: #1b5e20 (Material Green 900), --ifm-color-primary-light: #388e3c, --ifm-color-primary-lighter: #4caf50, --ifm-color-primary-lightest: #66bb6a
- [X] T015 [P] [US3] Replace purple primary colors with light green in frontend/src/css/custom.css html[data-theme='dark'] section - set --ifm-color-primary: #66bb6a (Material Green 400), --ifm-color-primary-light: #81c784, --ifm-color-primary-lighter: #a5d6a7
- [X] T016 [US3] Remove hero banner gradient in frontend/src/pages/index.module.css - replace .heroBanner background linear-gradient with background: var(--ifm-color-primary) (solid dark green) and ensure text color: #ffffff
- [X] T017 [P] [US3] Remove table header gradient in frontend/src/css/custom.css - replace .markdown table th linear-gradient with background: #e8f5e9 (light mode) and background: rgba(102, 187, 106, 0.15) (dark mode)
- [X] T018 [P] [US3] Remove footer gradient in frontend/src/css/custom.css - replace .footer linear-gradient(135deg, #8a2be2, #6a16c2) with background: var(--ifm-color-primary) or evaluate if footer can remain gradient if no text overlap

**Testing Checklist** (from quickstart.md Test Suite 3):
- [ ] Zero instances of purple hex values (#8a2be2, #9a46e8, etc.)
- [ ] Zero linear-gradient or radial-gradient behind text
- [ ] All accent colors use dark green consistently
- [ ] Grep verification shows no hardcoded purple colors remain

**Acceptance Criteria**:
- All purple colors replaced with Material Design green palette
- No gradients exist behind text-containing elements
- Hero banner uses solid dark green background
- All interactive elements (links, buttons, active menu) use green accents
- Color audit confirms 100% theme variable usage

**Dependencies**: Should complete US1 first (text contrast validated before color changes)
**Parallelization**: T014 and T015 can run in parallel (different theme blocks), T017 and T018 can run in parallel (different elements)

---

## Phase 6: User Story 4 - Responsive Layout Consistency (P3)

**Story Goal**: Ensure proper text spacing, line length constraints (75ch), and consistent layout across mobile/tablet/desktop

**Independent Test**: View site at viewport widths 320px, 768px, 1024px, 1440px and verify no horizontal scrolling, text reflows properly, and line length does not exceed 75 characters

**Tasks**:

- [X] T019 [P] [US4] Apply line length constraint in frontend/src/css/custom.css - add max-width: 75ch to .main-wrapper p and .markdown > * for optimal reading width
- [X] T020 [P] [US4] Verify responsive grid breakpoints in frontend/src/pages/index.module.css - ensure @media queries match spec: mobile (<768px), tablet (768-996px), desktop (≥1200px) with correct column counts
- [X] T021 [US4] Test mobile responsiveness at 375px viewport - ensure no horizontal scrollbar, cards stack vertically, text reflows without overflow, sidebar hamburger menu works
- [X] T022 [US4] Verify font size adjustments in frontend/src/css/custom.css - ensure --ifm-font-size-base: 18px on desktop, 16px on mobile (<576px) via media query

**Testing Checklist** (from quickstart.md Test Suite 4):
- [ ] 320px mobile: 1 column, no horizontal scroll, text readable
- [ ] 768px tablet: 2 columns, proper spacing, no layout breaks
- [ ] 1200px desktop: 3 columns, line length ≤75 characters
- [ ] 1440px+ : Maintained layout, no excessive white space

**Acceptance Criteria**:
- Body text line length limited to 75 characters maximum
- Responsive grid reflows at correct breakpoints with no layout shifts
- No horizontal scrolling required on any viewport size
- Font sizes adjust appropriately for mobile (16px) vs desktop (18px)

**Dependencies**: Should complete US2 (card grid) before US4 (responsive layout testing)
**Parallelization**: T019 and T020 can run in parallel (different CSS concerns)

---

## Phase 7: Polish & Cross-Cutting Concerns (No User Story Label)

**Objective**: Final cleanup, performance optimization, comprehensive testing

**Tasks**:

- [X] T023 Run comprehensive visual testing checklist from specs/007-frontend-ui-fix/quickstart.md - execute all 8 test suites (contrast, cards, colors, responsive, theme switching, cross-browser, accessibility, visual regression)
- [X] T024 Document before/after screenshots in specs/007-frontend-ui-fix/screenshots/ - capture homepage light/dark, doc page light/dark, mobile view for stakeholder review

**Testing Checklist** (from quickstart.md Test Suites 5-8):
- [ ] Theme switching <300ms, no FOUC (Test Suite 5)
- [ ] Cross-browser testing: Chrome, Firefox, Safari, Edge (Test Suite 6)
- [ ] Lighthouse accessibility score ≥90 (Test Suite 7)
- [ ] Visual regression: Compare before/after screenshots (Test Suite 8)

**Acceptance Criteria**:
- All 8 test suites from quickstart.md pass completely
- Before/after screenshots documented for stakeholder review
- No outstanding visual inconsistencies or accessibility issues

**Dependencies**: All user stories (US1-US4) must be complete before final testing
**Parallelization**: None (requires all previous tasks complete)

---

## Dependency Graph

### User Story Completion Order

```
Phase 1: Setup (T001-T003)
    ↓
Phase 3: US1 - Text Readability (T004-T008) ← MVP SCOPE
    ↓ (recommended but not required)
Phase 4: US2 - Consistent Cards (T009-T013)
    ‖ (independent)
Phase 5: US3 - Color Harmony (T014-T018)
    ↓ (should complete US2 first)
Phase 6: US4 - Responsive Layout (T019-T022)
    ↓ (all stories complete)
Phase 7: Polish & Testing (T023-T024)
```

**Critical Path**: T001 → T004-T008 (US1) → T023-T024 (Testing)
**MVP Delivery**: Complete Phase 1 (Setup) + Phase 3 (US1) = 8 tasks for minimum viable product

### Parallel Execution Opportunities

**Phase 1 (Setup)**:
- T002 and T003 can run in parallel (independent audits)

**Phase 3 (US1 - Text Readability)**:
- T004 and T005 can run in parallel (light mode and dark mode CSS blocks)

**Phase 4 (US2 - Consistent Cards)**:
- T009, T010, T011, T012 can run in parallel (different CSS properties on same element)

**Phase 5 (US3 - Color Harmony)**:
- T014 and T015 can run in parallel (light and dark theme blocks)
- T017 and T018 can run in parallel (table headers and footer)

**Phase 6 (US4 - Responsive Layout)**:
- T019 and T020 can run in parallel (line length and breakpoints are independent)

**Total Parallelizable Tasks**: 12 out of 24 tasks (50%)

---

## Implementation Strategy

### MVP-First Approach

**Minimum Viable Product** (Phase 1 + Phase 3):
- **8 tasks** (T001-T008)
- **Delivers**: Text readability in light and dark modes
- **Value**: Users can read all content without eye strain (P1 requirement)
- **Testing**: Test Suite 1 from quickstart.md (contrast verification)

**Incremental Delivery**:
1. **Iteration 1 (MVP)**: US1 - Text Readability (P1) - Delivers immediately usable readable text
2. **Iteration 2**: US2 - Consistent Cards (P2) - Improves professional appearance
3. **Iteration 3**: US3 + US4 (P3) - Color harmony and responsive layout polish

### Task Execution Guidelines

**Per-Task Workflow**:
1. **Read**: Review task description and file path
2. **Backup**: Ensure Phase 1 backup exists before modifying
3. **Edit**: Make precise CSS changes as described
4. **Test**: Run relevant test from quickstart.md
5. **Verify**: Use browser DevTools to confirm computed values
6. **Commit**: Git commit with task ID in message (e.g., "T004: Update light mode text colors")

**Testing Cadence**:
- After each task: Quick visual check in browser
- After each user story phase: Run full test suite for that story
- After Phase 7: Run complete quickstart.md testing protocol

**Quality Gates**:
- ✅ No hardcoded hex colors (except in CSS variable definitions)
- ✅ All contrast ratios meet WCAG AA (4.5:1 for normal text, 3:1 for large)
- ✅ No gradients behind text-containing elements
- ✅ Theme switching works smoothly (<300ms)
- ✅ Responsive grid reflows at correct breakpoints

---

## File Modification Summary

**Primary Targets** (modified by multiple tasks):
- `frontend/src/css/custom.css` - 15 tasks modify this file
- `frontend/src/pages/index.module.css` - 8 tasks modify this file

**Secondary Targets** (may need review):
- `frontend/docusaurus.config.js` - No changes expected, but review for theme config
- `frontend/src/components/` - Review for hardcoded colors (audit tasks will identify)

**No Changes Expected**:
- `frontend/docs/` - Markdown content unchanged
- `frontend/static/` - Static assets unchanged

---

## Rollback Strategy

**Backup Location**: `specs/007-frontend-ui-fix/backups/`

**Rollback Steps**:
1. Copy backup files from `specs/007-frontend-ui-fix/backups/` back to `frontend/src/`
2. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
3. Verify original purple theme restored

**Incremental Rollback**:
- Each task creates a git commit with task ID
- Use `git revert <commit-hash>` to undo specific tasks
- Use git history to identify exact CSS changes per task

---

## Success Metrics

**Completion Criteria**:
- [ ] All 24 tasks completed
- [ ] All acceptance criteria met for US1-US4
- [ ] All 8 test suites from quickstart.md pass
- [ ] Lighthouse accessibility score ≥90
- [ ] WCAG 2.1 Level AA compliance verified
- [ ] Cross-browser testing passed (Chrome, Firefox, Safari, Edge)
- [ ] Before/after screenshots documented

**Definition of Done**:
- All text readable in light and dark modes (WCAG AA contrast)
- Homepage cards uniform and professionally styled
- Purple color scheme completely replaced with dark green
- No gradients behind text anywhere on site
- Responsive layout works on mobile, tablet, desktop
- Theme switching smooth and performant (<300ms)
- No horizontal scrolling on any device

---

## Notes

**Test Strategy**: Manual visual testing with browser DevTools. No automated tests required per specification. Use quickstart.md as comprehensive testing checklist.

**Color Verification Tool**: WebAIM Contrast Checker (https://webaim.org/resources/contrastchecker/)

**Browser DevTools Usage**:
- Elements → Computed tab: Verify CSS variable values
- Elements → Styles tab: Check for hardcoded colors
- Device Toolbar (Cmd+Shift+M): Test responsive breakpoints
- Lighthouse tab: Run accessibility audit

**Risk Mitigation**:
- Backup files created in Phase 1 (T001)
- Incremental git commits per task for easy rollback
- Early testing of MVP (US1) validates approach before proceeding

**Estimated Total Duration**: 4-6 hours for all 24 tasks (experienced CSS developer)
- Setup: 30 minutes
- US1 (P1): 1.5 hours
- US2 (P2): 1 hour
- US3 (P3): 1 hour
- US4 (P3): 45 minutes
- Polish: 1 hour

---

**Next Command**: Start implementation with Phase 1 (Setup tasks T001-T003)
