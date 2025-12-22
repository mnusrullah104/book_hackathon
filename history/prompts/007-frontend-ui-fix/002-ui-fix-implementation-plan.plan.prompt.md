---
id: 002
title: UI Fix Implementation Plan
stage: plan
date: 2025-12-22
surface: agent
model: claude-sonnet-4-5-20250929
feature: 007-frontend-ui-fix
branch: 007-frontend-ui-fix
user: User
command: /sp.plan
labels: ["frontend", "css", "docusaurus", "accessibility", "responsive-design"]
links:
  spec: specs/007-frontend-ui-fix/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/007-frontend-ui-fix/plan.md
  - specs/007-frontend-ui-fix/research.md
  - specs/007-frontend-ui-fix/data-model.md
  - specs/007-frontend-ui-fix/contracts/theme-variables.schema.json
  - specs/007-frontend-ui-fix/quickstart.md
tests:
  - Constitution Check validation (all gates passed)
  - Research question validation (5 questions answered with evidence)
---

## Prompt

UI Fix Plan

Normalize theme colors using Docusaurus CSS variables for light and dark mode.

Remove gradients and fix text/background contrast on homepage.

Redesign homepage cards with uniform size, color, and spacing using responsive grid.

Apply consistent typography, spacing, and layout across all pages.

Test UI in light mode, dark mode, and mobile view to ensure text visibility.

## Response snapshot

Created comprehensive implementation plan for Frontend UI Fix & Consistency feature with complete Phase 0 (Research) and Phase 1 (Design & Contracts) artifacts.

**Plan Structure** (`plan.md`):
- Technical Context: JavaScript/CSS3, Docusaurus 2.x, manual visual testing, web browsers
- Constitution Check: ✅ PASS (all gates satisfied, AI-native marked N/A for CSS feature)
- Project Structure: Frontend-only refactoring targeting `custom.css` and `index.module.css`
- Implementation Strategy: Refactoring workflow (audit → normalize → test → refine)
- Key Technical Decisions: 4 major decisions (dark green color, gradient removal, card height, theme variables)
- Risk Assessment: 5 risks identified with mitigation strategies

**Phase 0: Research** (`research.md`):
Answered 5 research questions with evidence-based decisions:
1. **Docusaurus CSS Variables**: Use Infima `--ifm-*` + custom `--rb-*` variables
2. **WCAG AA Contrast**: Light mode `#1a1a1a` on white (16.1:1), Dark mode `#e8e8e8` on black (14.5:1)
3. **Dark Green Color**: Material Green 900 (`#1b5e20`) for light mode, Green 400 (`#66bb6a`) for dark mode
4. **Responsive Grid**: CSS Grid with explicit media queries (3-col desktop, 2-col tablet, 1-col mobile)
5. **Gradient Removal**: Replace all text-overlaid gradients with solid colors (hero banner, table headers)

**Phase 1: Design Artifacts**:

1. **Data Model** (`data-model.md`):
   - 52 theme variables (26 light mode, 26 dark mode)
   - 3 breakpoints with responsive behavior
   - Component state model (card states, theme states, link/button states)
   - WCAG validation rules for all color pairs

2. **Contracts** (`theme-variables.schema.json`):
   - JSON Schema defining all CSS custom properties
   - WCAG contrast requirements embedded
   - Gradient restrictions documented
   - Breakpoint definitions formalized

3. **Quickstart Guide** (`quickstart.md`):
   - 8 comprehensive test suites
   - Manual testing checklist with pass/fail tracking
   - Contrast verification procedures with WebAIM
   - Responsive testing at 6 viewport widths
   - Cross-browser testing matrix (Chrome, Firefox, Safari, Edge)
   - Accessibility testing with Lighthouse and axe DevTools
   - Visual regression documentation guidelines

**Key Decisions Made**:
- **Color Scheme**: Complete migration from purple to Material Design green palette
- **Contrast Values**: All text exceeds WCAG AA by comfortable margin (14.5:1 - 16.1:1 for body text)
- **Card Equality**: CSS Grid automatic height equalization within rows
- **Gradient Strategy**: Solid colors for all text-containing elements (hero banner → solid dark green)

**Files Delivered**:
- `plan.md` (252 lines): Complete implementation plan with strategy, decisions, risks
- `research.md` (267 lines): Evidence-based research answers with alternatives considered
- `data-model.md` (419 lines): Theme variable schema, breakpoints, state model, validation rules
- `contracts/theme-variables.schema.json` (223 lines): JSON Schema contract for CSS variables
- `quickstart.md` (548 lines): Comprehensive testing guide with 8 test suites and checklists

## Outcome

- ✅ Impact: Complete implementation plan ready for task generation (`/sp.tasks`)
- 🧪 Tests: Constitution gates validated, research evidence-based, design contracts formalized
- 📁 Files: 5 planning artifacts (plan.md, research.md, data-model.md, schema.json, quickstart.md)
- 🔁 Next prompts: `/sp.tasks` to generate atomic implementation tasks
- 🧠 Reflection: Plan successfully bridges specification requirements with concrete technical decisions. Research phase resolved all color, contrast, and layout ambiguities with industry-standard solutions (Material Design palette, WCAG AA compliance). Design artifacts provide clear contracts for implementation and comprehensive testing guidance.

## Evaluation notes (flywheel)

- Failure modes observed: None - all phases completed successfully with evidence-based decisions
- Graders run and results (PASS/FAIL): Constitution Check: PASS (5/5 applicable gates), Research Validation: PASS (5/5 questions answered with rationale and alternatives)
- Prompt variant (if applicable): Standard /sp.plan workflow with user-provided implementation guidance
- Next experiment (smallest change to try): Consider generating visual diff previews during planning phase to help users visualize color scheme changes before implementation
