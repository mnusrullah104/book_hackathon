---
id: 1
title: Fix Book Readability Specification
stage: spec
date: 2025-12-22
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-fix-book-readability
branch: 005-fix-book-readability
user: User
command: /sp.specify
labels: ["readability", "ui-design", "contrast", "accessibility", "wcag"]
links:
  spec: specs/005-fix-book-readability/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-fix-book-readability/spec.md
  - specs/005-fix-book-readability/checklists/requirements.md
tests:
  - Specification quality validation (10/10 criteria passed)
---

## Prompt

/sp.specify Fix & Redesign Book UI for Physical AI & Humanoid Robotics (Readability First)

User requested a complete redesign of the textbook UI to fix critical readability issues:
- Text blending into backgrounds (dark-on-dark, purple-on-black)
- Low contrast making text hard to read
- Accent colors used inappropriately for body text
- Design principle: "If any text is hard to read, the design is WRONG. Always prioritize clarity over style."

## Response snapshot

Created comprehensive specification with:
- 6 User Stories (P1: body text, sidebar, headings; P2: code blocks, hero, mobile)
- 27 Functional Requirements covering text contrast, headings, sidebar, layout, code blocks, hero/header, responsiveness
- 8 Success Criteria (WCAG AA compliance, readability, mobile support)
- 6 Explicit Exclusions (no fancy effects, no marketing page, no dashboards)
- Specific color requirements: body text #1a1a1a-#333333 (light), #e0e0e0-#f5f5f5 (dark)

Key focus areas:
1. **Text Contrast (Critical)**: Enforce WCAG AA ratios, remove purple from body text
2. **Sidebar Navigation**: High contrast, clear active states, no opacity issues
3. **Heading Hierarchy**: Clear visual distinction, accent colors only with proper contrast
4. **Code Blocks**: Readable syntax highlighting in both themes
5. **Mobile**: Responsive design with minimum 16px text

## Outcome

- ✅ Impact: Complete specification for fixing readability issues across the textbook UI
- 🧪 Tests: 10/10 specification quality criteria passed
- 📁 Files: spec.md (222 lines), requirements checklist (45 items)
- 🔁 Next prompts: /sp.clarify for refinement, then /sp.plan for implementation planning
- 🧠 Reflection: This feature directly addresses the gap between spec-003 (UI design verification) and actual readability problems. Previous feature verified existing code met its requirements, but those requirements didn't adequately address contrast issues.

## Evaluation notes (flywheel)

- Failure modes observed: None - specification created successfully
- Graders run and results (PASS/FAIL): Spec quality validation - PASS (10/10 criteria)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider adding specific contrast ratio targets per element type
