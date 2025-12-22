---
id: 2
title: Fix Book Readability Implementation Plan
stage: plan
date: 2025-12-22
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-fix-book-readability
branch: 005-fix-book-readability
user: User
command: /sp.plan
labels: ["readability", "css", "wcag", "accessibility", "implementation-plan"]
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
  - Constitution check PASS (6/6 principles)
---

## Prompt

/sp.plan

Execute the implementation planning workflow for the Fix & Redesign Book UI for Readability feature.

## Response snapshot

Created comprehensive implementation plan with:

**Phase 0 Research (research.md)**:
- Analyzed current CSS (1,149 lines) for readability issues
- Identified missing explicit text color definitions
- Documented WCAG AA requirements (4.5:1 body, 3:1 large text)
- Defined color palette: #1a1a1a (light), #e8e8e8 (dark)

**Phase 1 Design (data-model.md, quickstart.md)**:
- Defined CSS variable namespace (--rb-text-body, --rb-text-heading, etc.)
- Created entity definitions for Theme, Text Level, Content Area, Sidebar
- Documented development workflow and testing procedures

**Implementation Approach (7 phases)**:
1. Foundation: Add text color CSS variables
2. Body Text: Apply colors to markdown/paragraphs
3. Headings: Fix H2-H6 colors (keep H1 purple)
4. Sidebar: High-contrast navigation text
5. Code Blocks: Flat backgrounds, readable syntax
6. Hero/Header: Ensure contrast on backgrounds
7. Mobile: Verify at all breakpoints

**Key Files**: Single file modification - `src/css/custom.css`

## Outcome

- ✅ Impact: Complete implementation plan for CSS-only readability fixes
- 🧪 Tests: Constitution check PASS (6/6 principles)
- 📁 Files: plan.md, research.md, data-model.md, quickstart.md
- 🔁 Next prompts: /sp.tasks to generate implementation task list
- 🧠 Reflection: This is a focused CSS-only fix. The existing 1,149-line stylesheet needs targeted modifications rather than a complete rewrite. Key insight: body text colors were never explicitly defined, relying on browser defaults.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan created successfully
- Graders run and results (PASS/FAIL): Constitution check - PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider creating a CSS linting rule to enforce explicit text color definitions
