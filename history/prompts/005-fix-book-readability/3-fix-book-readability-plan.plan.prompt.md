---
id: 3
title: Fix Book Readability Implementation Plan
stage: plan
date: 2025-12-21
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-fix-book-readability
branch: 005-fix-book-readability
user: User
command: /sp.plan
labels: ["readability", "contrast", "accessibility", "ui-fix", "css", "planning"]
links:
  spec: specs/005-fix-book-readability/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-fix-book-readability/plan.md
  - specs/005-fix-book-readability/research.md
  - specs/005-fix-book-readability/data-model.md
  - specs/005-fix-book-readability/quickstart.md
tests:
  - Constitution check passed (6/6 principles)
---

## Prompt

/sp.plan

Create implementation plan for the Fix & Redesign Book UI for Readability feature based on the specification at specs/005-fix-book-readability/spec.md.

## Response snapshot

Created comprehensive implementation plan with Phase 0 and Phase 1 artifacts:

**Technical Context**:
- CSS3, Docusaurus 3.9.2 with React 18
- CSS-only modifications (no JavaScript changes)
- Target: WCAG AA contrast (4.5:1 body, 3:1 large)
- Single file: `src/css/custom.css` (1,149 lines)

**Constitution Check**: All 6 principles passed

**Design Decisions**:
- DD-001: CSS-only approach (no React component changes)
- DD-002: Neutral body text colors (#1a1a1a light, #e5e5e5 dark)
- DD-003: Preserve purple for headings (with WCAG AA compliance)

**Phase 0 Research Findings**:
- Body text has no explicit color defined (uses defaults)
- Sidebar uses purple colors instead of neutrals
- Heading purples pass WCAG in light mode but need adjustment in dark mode
- Code blocks use gradient backgrounds (should be solid)

**Phase 1 Artifacts**:
- research.md: CSS analysis with specific line numbers and fixes
- data-model.md: UI entities (Theme, TextLevel, ContentArea, Sidebar, CodeBlock, HeroSection)
- quickstart.md: Step-by-step implementation guide

**Implementation Phases** (from plan):
1. Body Text Contrast Fix (P1 - Critical)
2. Sidebar Navigation Fix (P1 - Critical)
3. Heading Hierarchy Fix (P1)
4. Code Block Fix (P2)
5. Hero/Header Fix (P2)
6. Mobile/Responsive Fix (P2)

## Outcome

- ✅ Impact: Complete implementation plan ready for task generation
- 🧪 Tests: Constitution check passed (6/6 principles)
- 📁 Files: plan.md, research.md, data-model.md, quickstart.md created
- 🔁 Next prompts: /sp.tasks to generate implementation task list
- 🧠 Reflection: Research revealed specific CSS issues - purple colors used inappropriately for body/sidebar text. Fixes are surgical CSS changes, not a complete overhaul.

## Evaluation notes (flywheel)

- Failure modes observed: None - clear CSS structure to modify
- Graders run and results (PASS/FAIL): Constitution check - PASS (6/6), Technical context - COMPLETE
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to task generation with priority-ordered implementation
