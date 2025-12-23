# Research: Frontend Refactor & UI Fix (Book-Only Phase)

**Feature**: 006-frontend-book-refactor
**Date**: 2025-12-22
**Purpose**: Resolve technical decisions and best practices for folder restructure and UI fixes

## Research Tasks

### 1. Folder Restructure Strategy

**Decision**: Move all Docusaurus files to /frontendBook, create empty /backend placeholder

**Rationale**: 
- Clean separation enables future backend addition without refactoring
- Industry standard for monorepo with frontend/backend separation
- Docusaurus remains self-contained and runnable independently

**Alternatives Considered**:
- Keep at root with backend subfolder: Rejected - mixes concerns, harder to extract later
- Nx/Turborepo monorepo: Rejected - overkill for current scope
- Git submodules: Rejected - adds complexity without benefit

### 2. Files to Move to /frontendBook

**Decision**: Move the following from root to /frontendBook:

| From Root | To /frontendBook |
|-----------|------------------|
| docs/ | frontendBook/docs/ |
| src/ | frontendBook/src/ |
| static/ | frontendBook/static/ |
| docusaurus.config.js | frontendBook/docusaurus.config.js |
| sidebars.js | frontendBook/sidebars.js |
| package.json | frontendBook/package.json |
| package-lock.json | frontendBook/package-lock.json |
| babel.config.js | frontendBook/babel.config.js |
| tsconfig.json | frontendBook/tsconfig.json (if exists) |

**Files to Keep at Root**:
- .gitignore (update to include both folders)
- README.md (update with new structure)
- .specify/ (tooling)
- history/ (prompt records)
- specs/ (feature specifications)

### 3. Text Visibility Approach

**Decision**: Build on existing 005-fix-book-readability changes, ensure they are applied in new location

**Rationale**: 
- Feature 005 already implemented high-contrast CSS variables
- Variables (--rb-text-body, etc.) should be preserved during migration
- No additional text fixes needed if 005 changes are included

**Key CSS Variables to Preserve**:
- --rb-text-body: #1a1a1a (light) / #e8e8e8 (dark)
- --rb-text-heading: #2d2d2d (light) / #f0f0f0 (dark)
- --rb-sidebar-text: #333333 (light) / #d0d0d0 (dark)
- --rb-bg-code: #f5f5f5 (light) / #1e1e1e (dark)

### 4. Full-Width Hero Strategy

**Decision**: Remove container constraint from hero banner using CSS

**Rationale**:
- Current hero is inside .container with max-width
- Full-width requires width: 100vw and margin adjustments
- Alternative: Move hero outside container in MDX/component

**Implementation Options**:
1. CSS override with negative margins (simpler)
2. Custom hero component outside container (cleaner but more work)

**Selected**: Option 1 for minimal changes

### 5. Responsive Cards Strategy

**Decision**: Use CSS Grid with fr units instead of fixed widths

**Rationale**:
- Current cards may have fixed pixel widths
- Grid with auto-fit/minmax provides fluid responsiveness
- fr units scale proportionally

**Implementation**:
```css
.cardContainer {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
}
```

### 6. Mobile Sidebar Strategy

**Decision**: Use Docusaurus default mobile behavior (hamburger menu)

**Rationale**:
- Docusaurus already handles mobile sidebar collapse
- Just need to verify it works after migration
- No custom implementation needed

## Key Research Conclusions

1. **Folder Structure**: Simple move operation, no complex tooling needed
2. **Text Visibility**: Already fixed in 005, just preserve CSS during migration
3. **Hero**: CSS-only fix with negative margins or vw units
4. **Cards**: CSS Grid with fr/minmax for responsiveness
5. **Mobile**: Docusaurus default behavior sufficient

## Implementation Sequence

1. Create /frontendBook and /backend folders
2. Move all Docusaurus files to /frontendBook
3. Update paths in docusaurus.config.js (if needed)
4. Verify CSS changes from 005 are included
5. Fix hero to be full-width
6. Verify card responsiveness (may already work)
7. Test mobile sidebar functionality
8. Update root README with new structure
