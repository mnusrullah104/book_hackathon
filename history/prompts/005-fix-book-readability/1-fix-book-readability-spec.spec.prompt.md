---
id: 1
title: Fix Book Readability Specification
stage: spec
date: 2025-12-21
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-fix-book-readability
branch: 005-fix-book-readability
user: User
command: /sp.specify
labels: ["readability", "contrast", "accessibility", "ui-fix", "textbook"]
links:
  spec: specs/005-fix-book-readability/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-fix-book-readability/spec.md
  - specs/005-fix-book-readability/checklists/requirements.md
tests:
  - Specification quality validation (16/16 checks passed)
---

## Prompt

/sp.specify

Redesign the textbook UI to fix poor readability and low contrast, ensuring all text is clearly visible, comfortable to read, and presented in a clean, academic, professional textbook layout.

Key problems to fix:
- Text blends into backgrounds (dark-on-dark, purple-on-black scenarios)
- Low contrast makes headings, paragraphs, and sidebar text hard to read
- Content area feels cramped or hidden
- Accent colors used inappropriately for body text

Design Principle: If any text is hard to read, the design is WRONG. Clarity over style, always.

## Response snapshot

Created comprehensive specification for fixing book UI readability issues:

**Problem Statement**: Identified 4 critical readability issues with current UI

**User Stories (6 total)**:
- US1: Read Body Text Without Strain (P1) - 4 acceptance scenarios
- US2: Navigate Sidebar Clearly (P1) - 4 acceptance scenarios
- US3: View Headings with Clear Hierarchy (P1) - 4 acceptance scenarios
- US4: Read Code Blocks Comfortably (P2) - 4 acceptance scenarios
- US5: View Hero/Header Section Clearly (P2) - 4 acceptance scenarios
- US6: Read on Mobile Without Issues (P2) - 4 acceptance scenarios

**Functional Requirements (27 total)**:
| Category | Count | Focus |
|----------|-------|-------|
| Text Contrast (Critical) | 5 | FR-001 to FR-005 |
| Headings | 4 | FR-006 to FR-009 |
| Sidebar Navigation | 4 | FR-010 to FR-013 |
| Layout | 4 | FR-014 to FR-017 |
| Code Blocks | 3 | FR-018 to FR-020 |
| Hero/Header | 3 | FR-021 to FR-023 |
| Responsiveness | 4 | FR-024 to FR-027 |

**Key Color Requirements**:
- Light mode body text: #1a1a1a to #333333 on white/light gray
- Dark mode body text: #e0e0e0 to #f5f5f5 on near-black
- Purple accent ONLY for headings/links/highlights, NEVER body text
- All text must meet WCAG AA contrast (4.5:1 body, 3:1 large)

**Success Criteria (8 total)**: All measurable and verifiable

## Outcome

- ✅ Impact: Complete specification ready for planning phase
- 🧪 Tests: Quality checklist passed (16/16 validation items)
- 📁 Files: spec.md and checklists/requirements.md created
- 🔁 Next prompts: /sp.clarify or /sp.plan
- 🧠 Reflection: This spec focuses on FIXING existing issues rather than building new features. Clear color specifications ensure no ambiguity about what "readable" means.

## Evaluation notes (flywheel)

- Failure modes observed: None - user requirements were comprehensive
- Graders run and results (PASS/FAIL): Specification quality - PASS (16/16)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to planning phase to identify specific CSS changes needed
