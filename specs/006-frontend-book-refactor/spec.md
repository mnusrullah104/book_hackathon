# Feature Specification: Frontend Refactor & UI Fix (Book-Only Phase)

**Feature Branch**: `006-frontend-book-refactor`
**Created**: 2025-12-22
**Status**: Draft
**Input**: User description: "Move all book frontend into a dedicated folder, fix readability, layout, responsiveness, and deliver a clean, professional Docusaurus textbook UI."

## Problem Statement

The current project structure has frontend files at the root level, making it difficult to manage and scale for future backend integration. Additionally, the UI has several issues including text visibility problems, container-locked hero sections, non-responsive cards, and inconsistent theming.

**Goals**:
1. Restructure frontend into `/frontendBook` folder for independent operation
2. Fix all UI readability and responsiveness issues
3. Prepare project structure for future backend integration

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Restructure Frontend into Dedicated Folder (Priority: P1)

A developer needs to work on the book frontend independently. They should be able to navigate to `/frontendBook`, run `npm install` and `npm start`, and have the entire Docusaurus site running without any dependencies on the root directory.

**Why this priority**: This is the foundational structural change that enables all other work. Without proper folder structure, the project cannot scale to include backend components.

**Independent Test**: Navigate to `/frontendBook`, run `npm install && npm start`, and verify the site loads at localhost:3000 with all content intact.

**Acceptance Scenarios**:

1. **Given** a fresh clone of the repository, **When** a developer navigates to `/frontendBook` and runs `npm install && npm start`, **Then** the Docusaurus site launches successfully with all documentation visible
2. **Given** the new folder structure, **When** a developer looks at the root directory, **Then** they see `/frontendBook` and `/backend` folders clearly separated
3. **Given** the restructured project, **When** Docusaurus builds, **Then** all existing docs, images, and static assets are found and rendered correctly

---

### User Story 2 - Read Content with Clear Text Visibility (Priority: P1)

A reader visits the textbook site and needs to read technical content without eye strain. All text must be clearly visible against backgrounds in both light and dark modes, with no white-on-white or dark-on-dark contrast issues.

**Why this priority**: Readability is the primary purpose of a textbook. If users cannot read the content, the entire product fails.

**Independent Test**: Open any documentation page in both light and dark modes. Verify all text (body, headings, sidebar, code) is immediately readable without adjustment.

**Acceptance Scenarios**:

1. **Given** a reader opens any page in light mode, **When** they view body text, **Then** text appears in dark colors on light background with high contrast
2. **Given** a reader opens any page in dark mode, **When** they view body text, **Then** text appears in light colors on dark background with high contrast
3. **Given** the site uses Docusaurus, **When** theming is applied, **Then** all colors use --ifm-* CSS variables (no hardcoded colors)
4. **Given** any page content, **When** a reader scans text, **Then** accent colors are only used for headings, links, and buttons - never for body paragraphs

---

### User Story 3 - View Full-Width Hero Banner (Priority: P2)

A visitor lands on the homepage and sees a professional, full-width hero banner that spans the entire viewport width (not constrained to the container). The hero should make a strong first impression.

**Why this priority**: First impressions matter. A constrained hero looks unprofessional and breaks visual expectations.

**Independent Test**: Open the homepage and verify the hero banner extends edge-to-edge across the viewport at any screen size.

**Acceptance Scenarios**:

1. **Given** a visitor opens the homepage, **When** the page loads, **Then** the hero banner extends from the left edge to the right edge of the viewport
2. **Given** the hero banner, **When** viewed at any viewport width (320px to 2560px), **Then** the hero maintains full-width appearance
3. **Given** the hero text, **When** displayed, **Then** title and subtitle are clearly readable with appropriate contrast

---

### User Story 4 - Navigate on Mobile Devices (Priority: P2)

A mobile user accesses the textbook site and can easily navigate through chapters using a mobile-friendly sidebar. The layout adapts properly without horizontal scrolling or overlapping elements.

**Why this priority**: Mobile accessibility expands the audience and enables on-the-go learning.

**Independent Test**: Open the site on a mobile device (or DevTools mobile view at 375px width). Verify sidebar converts to a drawer/menu and all content reflows properly.

**Acceptance Scenarios**:

1. **Given** a mobile user visits the site, **When** they access navigation, **Then** the sidebar is accessible via a hamburger menu or drawer
2. **Given** mobile viewport (<768px), **When** viewing any page, **Then** text reflows to fit without horizontal scrolling
3. **Given** mobile layout, **When** viewing cards on homepage, **Then** cards stack vertically with appropriate spacing
4. **Given** touch interactions, **When** tapping navigation items, **Then** touch targets are at least 44x44 pixels

---

### User Story 5 - View Responsive Feature Cards (Priority: P2)

A reader viewing the homepage sees feature cards that adapt to any screen size. Cards should have fluid widths (not fixed px values), maintain readable content, and arrange appropriately for the viewport.

**Why this priority**: Fixed-width cards break on different screen sizes, creating poor UX and unprofessional appearance.

**Independent Test**: Open the homepage at various widths (320px, 768px, 1200px, 1920px). Verify cards adapt their width and arrangement at each breakpoint.

**Acceptance Scenarios**:

1. **Given** homepage cards, **When** viewport is wide (>1200px), **Then** cards display in a multi-column grid
2. **Given** homepage cards, **When** viewport is medium (768px-1200px), **Then** cards display in 2 columns
3. **Given** homepage cards, **When** viewport is narrow (<768px), **Then** cards stack in a single column
4. **Given** any viewport width, **When** cards are displayed, **Then** card widths are percentage/fr-based (no fixed pixel widths)

---

### User Story 6 - Comfortable Reading Width and Spacing (Priority: P3)

A reader viewing documentation chapters sees content with optimal reading width (65-80 characters per line) and comfortable spacing between elements. Long reading sessions should not cause eye strain.

**Why this priority**: Reading comfort directly impacts learning effectiveness and time on site.

**Independent Test**: Open a documentation page with paragraphs of text. Verify line width is comfortable (around 75 characters) and spacing between elements is consistent.

**Acceptance Scenarios**:

1. **Given** a documentation page, **When** content is displayed, **Then** paragraph text has max-width of approximately 75 characters
2. **Given** content spacing, **When** viewing headings and paragraphs, **Then** appropriate vertical spacing separates sections
3. **Given** long paragraphs, **When** reading continuously, **Then** line height provides comfortable reading (1.5-1.7)

---

### Edge Cases

- What happens when a developer tries to run npm start from the root directory?
  - Clear error message or documentation explaining the new structure
- What happens when images are referenced with old paths after restructure?
  - All paths updated during migration; build fails with clear error if any missed
- What happens on extremely narrow screens (<320px)?
  - Content remains readable with potential simplification; no broken layouts
- What happens when a user has custom font sizes in their browser?
  - Layout scales proportionally using relative units (rem/em)
- What happens when JavaScript is disabled?
  - Core content remains accessible; navigation may be limited but readable

## Requirements *(mandatory)*

### Functional Requirements

#### Folder Structure

- **FR-001**: Project MUST contain /frontendBook folder at root level with complete Docusaurus setup
- **FR-002**: Project MUST contain /backend folder at root level (empty, reserved for future)
- **FR-003**: /frontendBook MUST contain: docs/, src/, static/, docusaurus.config.js, sidebars.js, package.json
- **FR-004**: Frontend MUST be runnable independently from /frontendBook using standard npm commands
- **FR-005**: All existing documentation content MUST be migrated to /frontendBook/docs/

#### Text Visibility

- **FR-006**: Body text MUST use dark colors on light backgrounds in light mode
- **FR-007**: Body text MUST use light colors on dark backgrounds in dark mode
- **FR-008**: All text colors MUST be defined using Docusaurus --ifm-* CSS variables
- **FR-009**: No CSS MUST contain hardcoded color values for text
- **FR-010**: Accent colors MUST only be used for headings, links, and buttons (not body text)

#### Layout & Responsiveness

- **FR-011**: Hero banner MUST extend full viewport width (not container-locked)
- **FR-012**: Feature cards MUST use fluid widths (percentage or fr units)
- **FR-013**: Cards MUST NOT have fixed pixel widths
- **FR-014**: Content area MUST have max-width constraint for reading comfort (65-80 characters)
- **FR-015**: All layout elements MUST use relative units (rem, em, %, vw, vh)

#### Mobile & Responsiveness

- **FR-016**: Sidebar MUST convert to mobile-friendly drawer/menu on screens <768px
- **FR-017**: All content MUST reflow without horizontal scrolling on mobile
- **FR-018**: Touch targets MUST be minimum 44x44 pixels
- **FR-019**: Layout MUST be functional at viewport widths from 320px to 2560px

#### Design Constraints

- **FR-020**: UI MUST follow content-first, textbook-style design
- **FR-021**: Long-form text areas MUST use plain backgrounds (no gradients behind text)
- **FR-022**: Design MUST be minimal and professional
- **FR-023**: All content MUST remain in Markdown (.md) format

### Explicit Exclusions (Non-Requirements)

- **NR-001**: No chatbot or interactive AI features
- **NR-002**: No user authentication or authorization
- **NR-003**: No backend API or server functionality
- **NR-004**: No database integration
- **NR-005**: No fancy animations or effects

## Assumptions

- Existing Docusaurus configuration can be migrated without major restructuring
- All current documentation content is in Markdown format
- The purple accent color will be retained for branding consistency
- Node.js 18+ will be the runtime environment
- The project will continue to be deployed to static hosting (Vercel, GitHub Pages, etc.)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Frontend runs successfully from /frontendBook with npm install && npm start
- **SC-002**: All text is clearly readable at first glance in both light and dark modes
- **SC-003**: Hero banner spans full viewport width on all screen sizes
- **SC-004**: Feature cards adapt properly from single-column (mobile) to multi-column (desktop)
- **SC-005**: Site is fully functional on devices from 320px to 2560px viewport width
- **SC-006**: No hardcoded color values exist in CSS (all use CSS variables)
- **SC-007**: Lighthouse accessibility score is 90+
- **SC-008**: Production build completes without errors from /frontendBook
