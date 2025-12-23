# Research: Textbook UI Design for Physical AI & Humanoid Robotics

**Feature**: 003-textbook-ui-design
**Date**: 2025-12-21
**Phase**: 0 (Research)

## Executive Summary

This research phase confirms that the existing Docusaurus implementation provides a solid foundation for the textbook UI. No major unknowns or blockers were identified. The implementation will focus on refinement rather than replacement.

## Research Topics

### 1. Existing Theme Analysis

**Question**: What is the current state of the purple theme implementation?

**Findings**:
- **CSS Variables**: 50+ custom CSS variables defined in `src/css/custom.css`
- **Color System**: Comprehensive purple palette with primary (#8a2be2), secondary, tertiary, and accent variants
- **Dark Mode**: Full dark theme implementation with appropriate lighter purple tones
- **Typography**: 18px base font size, 1.6 line height already configured
- **Spacing**: Complete spacing scale (xs to 3xl) implemented

**Decision**: Retain existing theme; make targeted refinements only.

**Rationale**: The existing implementation exceeds typical Docusaurus theming and would require significant effort to replace.

**Alternatives Considered**:
- Complete theme replacement: Rejected due to time constraints
- Neutral academic palette: Rejected as existing purple is professional and well-implemented

---

### 2. Docusaurus Best Practices for Textbook UI

**Question**: What are best practices for book-like reading experiences in Docusaurus?

**Findings**:
- **Line Width**: Optimal reading width is 65-80 characters (current: 75ch max-width ✅)
- **Line Height**: 1.5-1.7 recommended for body text (current: 1.6 ✅)
- **Font Size**: 16-18px for body text (current: 18px ✅)
- **Heading Hierarchy**: Clear visual distinction between H1-H4 (needs verification)
- **Code Blocks**: Horizontal scroll for overflow (already implemented ✅)
- **Admonitions**: Docusaurus built-in admonitions with custom styling (already implemented ✅)

**Decision**: Current typography settings are aligned with best practices. Verify heading hierarchy styling.

**Rationale**: No major typography changes needed; the existing configuration follows industry standards.

---

### 3. Responsive Design Requirements

**Question**: How should the UI behave across screen sizes (320px to 2560px)?

**Findings**:
- **Existing Breakpoints** (from custom.css):
  - Mobile: < 768px (sidebar collapses to hamburger menu)
  - Tablet: 768px - 1024px
  - Desktop: > 1024px
  - Large: > 1440px
- **Sidebar Behavior**: Custom DocSidebar component with collapse functionality
- **Content Scaling**: Container max-width of 1200px with responsive padding

**Decision**: Verify existing breakpoints cover the full 320px-2560px range; add edge case handling if needed.

**Rationale**: Existing responsive implementation is comprehensive; verification is sufficient.

---

### 4. Accessibility Compliance

**Question**: What accessibility requirements must be met (WCAG AA)?

**Findings**:
- **Contrast Ratios**: WCAG AA requires 4.5:1 for normal text, 3:1 for large text
- **Current Primary Color**: #8a2be2 on white background meets AA for large text only
- **Focus States**: Docusaurus default focus states present
- **Keyboard Navigation**: Tab navigation works for sidebar and links

**Decision**: Audit contrast ratios for all text elements in both themes; adjust if needed.

**Rationale**: Accessibility is a hard requirement (FR-014, SC-003); proactive verification needed.

**Potential Issues**:
- Light purple text on white backgrounds may fail contrast
- Dark mode contrast needs verification

---

### 5. Code Block Styling

**Question**: How should code blocks be styled for technical content (Python, ROS, YAML)?

**Findings**:
- **Prism Languages**: Configured with GitHub (light) and Dracula (dark) themes
- **Supported Languages**: Python, YAML, JavaScript, Bash, and more via Prism
- **Custom Styling**: Purple-themed code blocks with gradients already implemented
- **Copy Button**: Custom CodeBlock component with copy functionality

**Decision**: Verify syntax highlighting for ROS-specific code patterns; no major changes expected.

**Rationale**: Code block implementation is already comprehensive with copy functionality.

---

### 6. Sidebar Navigation Structure

**Question**: Does the current sidebar support the Module → Chapter hierarchy?

**Findings**:
- **Configuration**: sidebars.js uses category types for modules
- **Current Structure**:
  - 4 modules as collapsible categories
  - 12+ chapters as items within categories
  - Introduction as standalone item
- **Visual Styling**: Custom DocSidebar component with expand/collapse

**Decision**: No changes to sidebar structure; verify visual clarity of hierarchy.

**Rationale**: Sidebar already implements the required Module → Chapter pattern.

---

## Technology Decisions Summary

| Area | Decision | Confidence |
|------|----------|------------|
| Theme | Retain purple, refine | High |
| Typography | Verify, minor adjustments | High |
| Responsiveness | Verify breakpoints | High |
| Accessibility | Audit and fix | Medium |
| Code Blocks | Verify Prism languages | High |
| Navigation | No changes needed | High |

## Unknowns Resolved

All NEEDS CLARIFICATION items from Technical Context have been resolved:

| Item | Resolution |
|------|------------|
| Testing approach | Manual visual testing + Lighthouse audits |
| Performance targets | <3s load time, Lighthouse >90 |
| Responsive constraints | 320px-2560px width range |

## Remaining Risks

1. **Contrast Compliance**: Some text elements may fail WCAG AA; will require CSS adjustments
2. **Mobile Edge Cases**: Very small screens (<320px) may have layout issues

## Next Phase

Proceed to Phase 1 (Design) to create:
- data-model.md (UI entities)
- quickstart.md (development setup)
