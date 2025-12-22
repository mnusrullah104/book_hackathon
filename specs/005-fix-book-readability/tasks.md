# Tasks: Fix & Redesign Book UI for Readability

**Input**: Design documents from `/specs/005-fix-book-readability/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md
**Branch**: `005-fix-book-readability`

**Tests**: Not explicitly requested - focusing on manual verification per success criteria.

**Organization**: Tasks grouped by user story to enable independent implementation and verification.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different CSS sections, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6)
- Include exact line ranges in descriptions where applicable

## Path Conventions

- **Project Type**: Web (frontend-only static site)
- **Primary Stylesheet**: `src/css/custom.css`
- **Configuration**: `docusaurus.config.js`

---

## Phase 1: Setup (Verification & Baseline)

**Purpose**: Establish baseline and prepare for CSS modifications

- [x] T001 Run development server and verify current UI renders (`npm start`)
- [x] T002 [P] Run Lighthouse accessibility audit to establish baseline contrast scores
- [x] T003 [P] Screenshot current state in light mode (body text, sidebar, headings)
- [x] T004 [P] Screenshot current state in dark mode (body text, sidebar, headings)
- [x] T005 Document current text color values (or lack thereof) in src/css/custom.css

**Checkpoint**: Baseline established - ready for CSS modifications

---

## Phase 2: Foundational (CSS Variables)

**Purpose**: Add high-contrast text color CSS variables that ALL user stories depend on

**CRITICAL**: These variables must be defined before any user story tasks can use them

- [x] T006 Add light mode text color variables to :root in src/css/custom.css (lines ~35-50): --rb-text-body: #1a1a1a, --rb-text-heading: #2d2d2d, --rb-text-muted: #4a4a4a, --rb-bg-code: #f5f5f5, --rb-sidebar-text: #333333

- [x] T007 Add dark mode text color variables to html[data-theme='dark'] in src/css/custom.css (lines ~96-145): --rb-text-body: #e8e8e8, --rb-text-heading: #f0f0f0, --rb-text-muted: #b0b0b0, --rb-bg-code: #1e1e1e, --rb-sidebar-text: #d0d0d0

- [x] T008 Verify new variables are accessible (check DevTools Elements > Computed)

**Checkpoint**: Foundation CSS variables defined - user story work can begin

---

## Phase 3: User Story 1 - Read Body Text Without Strain (Priority: P1) MVP

**Goal**: Ensure body paragraph text is clearly readable with high contrast in both themes

**Independent Test**: Open any chapter, read paragraphs for 5+ minutes without eye strain. Text should be dark gray on white (light) or light gray on near-black (dark).

### Implementation for User Story 1

- [x] T009 [US1] Add body text color rule for .markdown in src/css/custom.css (after line 1047): color: var(--rb-text-body)

- [x] T010 [P] [US1] Add body text color rule for .main-wrapper p in src/css/custom.css (around line 430): color: var(--rb-text-body)

- [x] T011 [P] [US1] Remove any purple color from body text classes in src/css/custom.css

- [x] T012 [US1] Verify body text contrast in light mode using Chrome DevTools (expect 16.1:1 ratio)

- [x] T013 [US1] Verify body text contrast in dark mode using Chrome DevTools (expect 14.5:1 ratio)

- [x] T014 [US1] Test body text readability by reading a full chapter in both themes

**Checkpoint**: Body text is readable - User Story 1 complete and testable

---

## Phase 4: User Story 2 - Navigate Sidebar Clearly (Priority: P1)

**Goal**: Sidebar navigation text is clearly visible; active state is distinguishable

**Independent Test**: Open sidebar in both themes. All module/chapter names should be immediately readable. Active item should be obviously highlighted.

### Implementation for User Story 2

- [x] T015 [US2] Override sidebar text color for .menu__link in src/css/custom.css (around lines 511-576): color: var(--rb-sidebar-text)

- [x] T016 [P] [US2] Fix collapsible title color for .menu__list-item-collapsible-title in src/css/custom.css (lines 536-543): color: var(--rb-sidebar-text)

- [x] T017 [P] [US2] Keep active state purple for .menu__link--active in src/css/custom.css (lines 560-565): color: var(--ifm-color-primary), font-weight: 600

- [x] T018 [US2] Remove any opacity-based text styling from sidebar in src/css/custom.css

- [x] T019 [US2] Verify sidebar text contrast in light mode (expect 12.6:1 ratio)

- [x] T020 [US2] Verify sidebar text contrast in dark mode (expect 13.3:1 ratio)

- [x] T021 [US2] Test sidebar navigation by expanding all modules and verifying readability

**Checkpoint**: Sidebar navigation is clear - User Story 2 complete and testable

---

## Phase 5: User Story 3 - View Headings with Clear Hierarchy (Priority: P1)

**Goal**: H1 stays purple for branding; H2-H6 use high-contrast neutral colors

**Independent Test**: Open a chapter with multiple heading levels. Each level should be visually distinct and readable. H1 purple, H2-H6 dark gray/near-black.

### Implementation for User Story 3

- [x] T022 [US3] Keep H1 purple but verify contrast in src/css/custom.css (lines 1050-1069): color: var(--ifm-color-primary)

- [x] T023 [US3] Change H2 color to high-contrast neutral in src/css/custom.css (lines 1071-1091): color: var(--rb-text-heading)

- [x] T024 [P] [US3] Change H3 color to high-contrast neutral in src/css/custom.css (lines 1093-1100): color: var(--rb-text-heading)

- [x] T025 [P] [US3] Change H4 color to high-contrast neutral in src/css/custom.css (lines 1102-1109): color: var(--rb-text-heading)

- [x] T026 [P] [US3] Change H5 and H6 colors in src/css/custom.css (lines 1111-1127): color: var(--rb-text-heading)

- [x] T027 [US3] Verify H1 contrast against background (purple on white: 6.5:1 - passes AA for large text)

- [x] T028 [US3] Verify H2-H6 contrast in both themes (expect 14.0:1+ ratio)

- [x] T029 [US3] Test heading hierarchy by navigating through multiple chapters

**Checkpoint**: Headings are readable with clear hierarchy - User Story 3 complete and testable

---

## Phase 6: User Story 4 - Read Code Blocks Comfortably (Priority: P2)

**Goal**: Code blocks have flat backgrounds with readable syntax highlighting

**Independent Test**: Open a chapter with code examples. Code should be clearly readable with visible syntax colors in both themes.

### Implementation for User Story 4

- [x] T030 [US4] Replace gradient background with flat color in .prism-code in src/css/custom.css (lines 247-258): background: var(--rb-bg-code), border: 1px solid var(--ifm-color-emphasis-300)

- [x] T031 [P] [US4] Fix language-specific code blocks to use flat backgrounds in src/css/custom.css (lines 279-313)

- [x] T032 [P] [US4] Ensure code text uses readable color in .prism-code: color: var(--rb-text-body)

- [x] T033 [US4] Fix inline code styling in src/css/custom.css (lines 479-494): color: var(--rb-text-body), background-color: var(--rb-bg-code)

- [x] T034 [US4] Verify syntax highlighting colors maintain readability in both themes

- [x] T035 [US4] Test code blocks with Python, YAML, and Bash examples

**Checkpoint**: Code blocks are readable - User Story 4 complete and testable

---

## Phase 7: User Story 5 - View Hero/Header Section Clearly (Priority: P2)

**Goal**: Hero section text is readable on any background

**Independent Test**: Visit homepage. Title, subtitle, and buttons should all be immediately readable.

### Implementation for User Story 5

- [x] T036 [US5] Ensure hero title has high contrast in src/pages/index.js or src/css/custom.css: color: #ffffff, text-shadow: none

- [x] T037 [P] [US5] Ensure hero subtitle has high contrast: color: rgba(255, 255, 255, 0.95)

- [x] T038 [P] [US5] Verify button text contrast in src/css/custom.css (lines 578-610)

- [x] T039 [US5] Remove any gradient backgrounds behind text in hero section

- [x] T040 [US5] Test hero section in both light and dark themes

**Checkpoint**: Hero/Header is readable - User Story 5 complete and testable

---

## Phase 8: User Story 6 - Read on Mobile Without Issues (Priority: P2)

**Goal**: All readability fixes apply on mobile; text reflows properly

**Independent Test**: Open any chapter on mobile (or DevTools mobile view). All text should be readable at 320px width.

### Implementation for User Story 6

- [x] T041 [US6] Verify 16px minimum font size on mobile in src/css/custom.css (lines 704-716)

- [x] T042 [P] [US6] Ensure all new color variables apply in mobile breakpoints

- [x] T043 [P] [US6] Verify sidebar drawer uses readable text colors on mobile (lines 814-848)

- [x] T044 [US6] Test at 320px viewport width - verify no horizontal scrolling for text

- [x] T045 [US6] Test at 576px viewport width - verify proper reflow

- [x] T046 [US6] Test at 768px viewport width - verify sidebar transition

- [x] T047 [US6] Verify touch targets are at least 44x44px for navigation items

**Checkpoint**: Mobile readability works - User Story 6 complete and testable

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and cleanup

- [x] T048 Run Lighthouse accessibility audit - target 90+ score
- [x] T049 [P] Verify WCAG AA compliance with contrast checker tool
- [x] T050 [P] Remove any unused CSS related to old purple text colors
- [x] T051 Clean up any duplicate or conflicting CSS rules
- [x] T052 Run production build (`npm run build`) and verify no errors
- [x] T053 Test complete user flow: navigate chapters, read content, view code blocks
- [x] T054 Screenshot final state in light mode for comparison
- [x] T055 Screenshot final state in dark mode for comparison

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories 1-3 (P1)**: All depend on Foundational, can run in parallel with each other
- **User Stories 4-6 (P2)**: All depend on Foundational, can run in parallel with each other
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

All user stories are independent after Phase 2 (Foundational) is complete:

- **US1 (Body Text)**: No dependencies on other stories
- **US2 (Sidebar)**: No dependencies on other stories
- **US3 (Headings)**: No dependencies on other stories
- **US4 (Code Blocks)**: No dependencies on other stories
- **US5 (Hero)**: No dependencies on other stories
- **US6 (Mobile)**: Should be done last to verify all other fixes work on mobile

### Parallel Opportunities

After Phase 2 completes:

P1 Stories (can run in parallel):
- US1: Body Text (T009-T014)
- US2: Sidebar (T015-T021)
- US3: Headings (T022-T029)

P2 Stories (can run in parallel):
- US4: Code Blocks (T030-T035)
- US5: Hero (T036-T040)
- US6: Mobile (T041-T047) - verify after others

---

## Implementation Strategy

### MVP First (User Stories 1-3)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T008) - CRITICAL
3. Complete Phase 3: US1 Body Text (T009-T014)
4. STOP and VALIDATE: Can you read body text comfortably?
5. Complete Phase 4: US2 Sidebar (T015-T021)
6. Complete Phase 5: US3 Headings (T022-T029)
7. MVP COMPLETE: Core readability fixed

### Full Implementation

Continue with P2 stories:

8. Complete Phase 6: US4 Code Blocks (T030-T035)
9. Complete Phase 7: US5 Hero (T036-T040)
10. Complete Phase 8: US6 Mobile (T041-T047)
11. Complete Phase 9: Polish (T048-T055)

---

## Summary

| Phase | Tasks | Story | Priority |
|-------|-------|-------|----------|
| Setup | T001-T005 | - | - |
| Foundational | T006-T008 | - | BLOCKER |
| Body Text | T009-T014 | US1 | P1 |
| Sidebar | T015-T021 | US2 | P1 |
| Headings | T022-T029 | US3 | P1 |
| Code Blocks | T030-T035 | US4 | P2 |
| Hero | T036-T040 | US5 | P2 |
| Mobile | T041-T047 | US6 | P2 |
| Polish | T048-T055 | - | Final |

**Total Tasks**: 55
**Parallel Opportunities**: 18 tasks marked [P]
**MVP Scope**: Phases 1-5 (T001-T029, 29 tasks)

---

## Notes

- All changes are in a single file: `src/css/custom.css`
- Commit after each phase checkpoint
- Test in BOTH light and dark modes after each user story
- Use Chrome DevTools contrast checker for verification
- WCAG AA requires 4.5:1 for body text, 3:1 for large text (headings)
