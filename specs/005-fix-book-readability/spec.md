# Feature Specification: Fix & Redesign Book UI for Readability

**Feature Branch**: `005-fix-book-readability`
**Created**: 2025-12-21
**Status**: Draft
**Input**: User description: "Redesign the textbook UI to fix poor readability and low contrast, ensuring all text is clearly visible, comfortable to read, and presented in a clean, academic, professional textbook layout."

## Problem Statement

The current textbook UI has critical readability issues:
- Text blends into backgrounds (dark-on-dark, purple-on-black scenarios)
- Low contrast makes headings, paragraphs, and sidebar text hard to read
- Content area feels cramped or hidden
- Accent colors used inappropriately for body text

**Design Principle**: If any text is hard to read, the design is WRONG. Clarity over style, always.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read Body Text Without Strain (Priority: P1)

A reader opens any chapter and immediately sees clear, high-contrast text against the background. They can read paragraphs comfortably without squinting or adjusting screen brightness. Text never blends into the background in either light or dark mode.

**Why this priority**: This is the most critical fix. If body text isn't readable, the entire book fails its purpose. Every other feature is useless without this.

**Independent Test**: Open any chapter in both light and dark mode. All paragraph text should be instantly readable without any adjustment. No text should blend into backgrounds.

**Acceptance Scenarios**:

1. **Given** a reader opens a chapter in light mode, **When** they view paragraph text, **Then** text appears in dark gray/near-black (#1a1a1a to #333333) on white/light gray background
2. **Given** a reader opens a chapter in dark mode, **When** they view paragraph text, **Then** text appears in light gray/off-white (#e0e0e0 to #f5f5f5) on near-black background
3. **Given** any page in the book, **When** a reader scans for text, **Then** no text uses purple or accent colors for body paragraphs
4. **Given** a reader with normal vision, **When** they read any paragraph, **Then** they can read comfortably for 30+ minutes without eye strain

---

### User Story 2 - Navigate Sidebar Clearly (Priority: P1)

A reader can clearly see and read all sidebar navigation items. The current chapter is obviously highlighted. Module and chapter labels are readable without hovering or squinting. No low-opacity or faded text.

**Why this priority**: Navigation is essential for a textbook. If readers can't find content, they can't learn.

**Independent Test**: Open the sidebar in both themes. Every navigation item should be clearly readable. Active state should be obviously different from inactive.

**Acceptance Scenarios**:

1. **Given** a reader views the sidebar in light mode, **When** they look at module and chapter names, **Then** text is clearly readable with high contrast against the sidebar background
2. **Given** a reader views the sidebar in dark mode, **When** they look at navigation items, **Then** text is light-colored on dark background with no transparency/opacity issues
3. **Given** a reader is on a specific chapter, **When** they look at the sidebar, **Then** the active chapter is clearly highlighted and distinguishable from other items
4. **Given** a reader needs to navigate, **When** they scan the sidebar, **Then** no text appears faded, ghosted, or difficult to read

---

### User Story 3 - View Headings with Clear Hierarchy (Priority: P1)

A reader can instantly identify heading levels through size and weight. Headings are readable without eye strain. Accent colors (purple) may be used sparingly for headings but must maintain high contrast.

**Why this priority**: Headings provide structure for learning. Unclear headings make content hard to follow.

**Independent Test**: Open any chapter with multiple heading levels. Each level (H1, H2, H3, H4) should be visually distinct and readable.

**Acceptance Scenarios**:

1. **Given** a reader views a chapter, **When** they see an H1 heading, **Then** it is large, bold, and clearly readable (accent color allowed if contrast is sufficient)
2. **Given** a reader scans the page, **When** they look at H2/H3/H4 headings, **Then** each level is visually distinct through size/weight, all readable
3. **Given** any heading in dark mode, **When** using accent colors, **Then** the color maintains at least WCAG AA contrast ratio against the background
4. **Given** a page with multiple sections, **When** a reader skims, **Then** they can quickly identify section boundaries via heading hierarchy

---

### User Story 4 - Read Code Blocks Comfortably (Priority: P2)

A reader can view code examples with proper syntax highlighting. Code blocks have clear boundaries. Text within code blocks is readable in both themes. No dark code on dark backgrounds.

**Why this priority**: Code examples are essential for a technical robotics textbook. They must be readable.

**Independent Test**: Open a chapter with code blocks in both themes. All code should be readable with clear syntax highlighting.

**Acceptance Scenarios**:

1. **Given** a code block in light mode, **When** displayed, **Then** it has a clearly distinguishable background and readable text
2. **Given** a code block in dark mode, **When** displayed, **Then** code text is light-colored on a dark (but distinct) background
3. **Given** code with syntax highlighting, **When** viewed, **Then** keywords, strings, and comments are distinguishable but all readable
4. **Given** a long code block, **When** a reader needs to scroll, **Then** horizontal scrolling works without affecting page layout

---

### User Story 5 - View Hero/Header Section Clearly (Priority: P2)

A reader visiting the homepage or section headers sees large, readable titles. No text is placed on busy gradients. Buttons have clear labels with high contrast.

**Why this priority**: First impressions matter for hackathon judges. The header must look professional.

**Independent Test**: Visit the homepage. Title, subtitle, and buttons should all be immediately readable.

**Acceptance Scenarios**:

1. **Given** a reader visits the homepage, **When** they view the hero section, **Then** the title is large and readable on a simple background
2. **Given** a hero section with buttons, **When** displayed, **Then** button text has strong contrast against button background
3. **Given** any header area, **When** viewed, **Then** no text is placed on complex gradients or images that reduce readability
4. **Given** the homepage in dark mode, **When** viewed, **Then** all hero text remains readable with appropriate contrast

---

### User Story 6 - Read on Mobile Without Issues (Priority: P2)

A reader on a mobile device can read all content clearly. Text reflows properly. Sidebar converts to a clean drawer/menu. No horizontal scrolling required for text.

**Why this priority**: Mobile reading expands accessibility. Judges may review on tablets.

**Independent Test**: Open the book on a phone (or DevTools mobile view). All text should be readable, navigation accessible.

**Acceptance Scenarios**:

1. **Given** a reader on mobile, **When** viewing any chapter, **Then** text reflows to fit screen width without horizontal scrolling
2. **Given** mobile view, **When** accessing navigation, **Then** sidebar is replaced by a clean, readable menu/drawer
3. **Given** a small screen, **When** reading paragraphs, **Then** font size remains readable (minimum 16px equivalent)
4. **Given** mobile dark mode, **When** viewing content, **Then** all contrast requirements still apply

---

### Edge Cases

- What happens when a chapter has no code blocks?
  - Layout remains clean and consistent; no empty code-block styling artifacts
- What happens when headings are very long?
  - Text wraps cleanly without breaking layout or becoming unreadable
- What happens on very small screens (<320px)?
  - Content remains readable with potential simplification; no broken layouts
- What happens with extremely long paragraphs?
  - Proper line height and width constraints maintain readability
- What happens when users have custom font sizes in their browser?
  - Layout scales proportionally; text remains readable

## Requirements *(mandatory)*

### Functional Requirements

#### Text Contrast (Critical)

- **FR-001**: Body text in light mode MUST use dark gray (#1a1a1a to #333333) on white/light gray background
- **FR-002**: Body text in dark mode MUST use light gray/off-white (#e0e0e0 to #f5f5f5) on near-black background (#121212 to #1a1a1a)
- **FR-003**: All text MUST meet WCAG AA contrast ratio (4.5:1 for body text, 3:1 for large text)
- **FR-004**: Accent colors (purple) MUST NOT be used for body paragraph text
- **FR-005**: No text MUST ever appear with reduced opacity that compromises readability

#### Headings

- **FR-006**: H1 headings MUST be clearly larger and bolder than body text
- **FR-007**: H2, H3, H4 headings MUST have distinct visual hierarchy through size and/or weight
- **FR-008**: Headings MAY use accent colors only if WCAG AA contrast is maintained
- **FR-009**: All heading text MUST be immediately readable without adjustment

#### Sidebar Navigation

- **FR-010**: Sidebar text MUST have high contrast in both light and dark modes
- **FR-011**: Active/current chapter MUST be clearly highlighted with obvious visual distinction
- **FR-012**: No sidebar text MUST use low opacity or transparency that reduces readability
- **FR-013**: Module and chapter labels MUST be readable without hover states

#### Layout

- **FR-014**: Content area MUST be centered with proper max-width for comfortable reading (65-80 characters)
- **FR-015**: Sidebar MUST be visually separated from main content area
- **FR-016**: Sufficient whitespace/negative space MUST exist around content blocks
- **FR-017**: No text MUST be placed on gradients or images that reduce readability

#### Code Blocks

- **FR-018**: Code blocks MUST have clearly distinguishable backgrounds from surrounding content
- **FR-019**: Code text MUST be readable in both light and dark modes
- **FR-020**: Syntax highlighting MUST maintain readability for all token types

#### Hero/Header

- **FR-021**: Hero section MUST use simple, flat backgrounds (no complex gradients behind text)
- **FR-022**: Hero title and subtitle MUST be clearly readable
- **FR-023**: Buttons MUST have high-contrast text against their backgrounds

#### Responsiveness

- **FR-024**: Text MUST reflow cleanly on small screens without horizontal scrolling
- **FR-025**: Sidebar MUST convert to accessible drawer/menu on mobile
- **FR-026**: Minimum body text size MUST be 16px on mobile devices
- **FR-027**: All contrast requirements MUST apply equally on mobile

### Explicit Exclusions (Non-Requirements)

- **NR-001**: No fancy visual effects or animations
- **NR-002**: No marketing-style landing page
- **NR-003**: No dashboard UI elements
- **NR-004**: No chatbot or interactive tools
- **NR-005**: No dark gradients behind text
- **NR-006**: No decorative elements that compromise readability

### Key Entities

- **Theme**: Light or dark color mode affecting all UI elements
- **Text Level**: Body, heading (H1-H6), navigation, code
- **Content Area**: Main reading region with max-width constraint
- **Sidebar**: Navigation panel with module/chapter hierarchy

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every line of text is readable at first glance without any adjustment
- **SC-002**: All text passes WCAG AA contrast ratio (verifiable via Lighthouse or contrast checker)
- **SC-003**: Users can read comfortably for 30+ minutes without eye strain
- **SC-004**: UI presents as a serious, professional technical textbook
- **SC-005**: No text blends into background in either light or dark mode
- **SC-006**: Hackathon judges can evaluate all content without readability complaints
- **SC-007**: Sidebar navigation is immediately usable without confusion
- **SC-008**: Mobile users can read all content without zooming or horizontal scrolling

## Assumptions

- The existing Docusaurus structure will be maintained
- Content will remain in Markdown (.md) files
- Purple accent color can remain for highlights, links, and headings (with proper contrast)
- Complete CSS overhaul is acceptable to achieve readability goals
- Current purple theme elements that cause readability issues will be removed or modified
