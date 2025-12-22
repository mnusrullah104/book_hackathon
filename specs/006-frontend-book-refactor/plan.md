# Implementation Plan: Frontend Refactor & UI Fix (Book-Only Phase)

**Branch**: `006-frontend-book-refactor` | **Date**: 2025-12-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-frontend-book-refactor/spec.md`

## Summary

Restructure the Docusaurus book frontend into a dedicated `/frontendBook` folder for independent operation, while preserving and enhancing UI readability fixes from feature 005. Create empty `/backend` placeholder for future expansion. Fix hero banner to be full-width and ensure responsive card layouts.

**Primary Changes**:
1. Move all Docusaurus files from root to `/frontendBook`
2. Create empty `/backend` folder
3. Preserve CSS readability fixes
4. Fix hero banner to span full viewport
5. Ensure responsive card grid layout

## Technical Context

**Language/Version**: JavaScript/TypeScript, CSS3, Docusaurus 3.9.2, React 18, Node.js 18+
**Primary Dependencies**: Docusaurus, Prism (syntax highlighting), Infima CSS framework
**Storage**: N/A (static site, no database)
**Testing**: Manual visual verification, npm run build, Lighthouse audits
**Target Platform**: Web (all modern browsers), responsive 320px-2560px
**Project Type**: Web (frontend-only static site moving to monorepo structure)
**Performance Goals**: Page load <3s, Lighthouse 90+
**Constraints**: Static hosting compatible (Vercel, GitHub Pages), no backend dependencies
**Scale/Scope**: Single Docusaurus site, ~20 documentation pages

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Spec-first development | PASS | Spec created at `/specs/006-frontend-book-refactor/spec.md` |
| Technical accuracy | PASS | All migration steps documented, paths verified |
| Clarity for developers | PASS | Quickstart.md provides clear development workflow |
| AI-native architecture | N/A | Frontend-only, no AI components in this feature |
| End-to-end transparency | PASS | Full migration path documented |
| Modular, non-filler | PASS | Clean separation of frontend/backend concerns |

**Gate Status**: PASS - Proceed with implementation

## Project Structure

### Documentation (this feature)

```text
specs/006-frontend-book-refactor/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Migration strategy research
├── data-model.md        # Folder structure entities
├── quickstart.md        # Development setup guide
├── checklists/
│   └── requirements.md  # Quality checklist
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (After Migration)

```text
Repository Root/
├── frontendBook/                 # Docusaurus site (MOVED FROM ROOT)
│   ├── docs/                     # Markdown documentation
│   │   ├── module-1/            # Module chapters
│   │   ├── module-2/
│   │   ├── module-3/
│   │   └── ...
│   ├── src/
│   │   ├── css/
│   │   │   └── custom.css       # Theme overrides with readability fixes
│   │   ├── pages/
│   │   │   ├── index.md         # Homepage with hero
│   │   │   └── index.module.css # Homepage styles
│   │   └── theme/               # Docusaurus theme overrides
│   ├── static/
│   │   └── img/                 # Static images
│   ├── docusaurus.config.js     # Site configuration
│   ├── sidebars.js              # Navigation structure
│   ├── package.json             # Dependencies
│   └── babel.config.js          # Babel config
│
├── backend/                      # EMPTY (reserved for future)
│   └── .gitkeep                 # Placeholder file
│
├── specs/                        # Feature specifications (UNCHANGED)
├── history/                      # Prompt records (UNCHANGED)
├── .specify/                     # Tooling (UNCHANGED)
├── .gitignore                    # Updated for new structure
└── README.md                     # Updated with new structure
```

**Structure Decision**: Custom monorepo-style layout with frontend in `/frontendBook` and placeholder `/backend` for future expansion. This differs from standard web app template because there is no backend yet - just a static site moving to enable future backend addition.

## Implementation Approach

### Phase 1: Folder Restructure (US1)

1. Create `/frontendBook` folder at root
2. Create `/backend` folder with `.gitkeep`
3. Move all Docusaurus files:
   - `docs/` → `frontendBook/docs/`
   - `src/` → `frontendBook/src/`
   - `static/` → `frontendBook/static/`
   - `docusaurus.config.js` → `frontendBook/`
   - `sidebars.js` → `frontendBook/`
   - `package.json` → `frontendBook/`
   - `package-lock.json` → `frontendBook/`
   - `babel.config.js` → `frontendBook/`
4. Update any absolute paths in config files
5. Verify `npm install && npm start` works from `/frontendBook`

### Phase 2: Preserve Readability Fixes (US2)

Ensure all CSS fixes from 005-fix-book-readability are preserved:
- High-contrast text variables (--rb-text-body, etc.)
- Heading colors (H1 purple, H2-H6 neutral)
- Sidebar navigation colors
- Code block styling
- Homepage card text colors

### Phase 3: Full-Width Hero (US3)

Fix hero banner in `frontendBook/src/pages/index.module.css`:

```css
.heroBanner {
  width: 100vw;
  margin-left: calc(-50vw + 50%);
  /* ... rest of styles */
}
```

Or remove container constraint if hero is inside Docusaurus container.

### Phase 4: Responsive Cards (US5)

Update card grid in `frontendBook/src/pages/index.module.css`:

```css
.cardContainer {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  width: 100%;
}

.card {
  width: 100%; /* No fixed pixel width */
}
```

### Phase 5: Update Root Files

1. Update `.gitignore` to handle new structure
2. Update `README.md` with new development instructions
3. Verify deployment config (if any Vercel/Netlify configs at root)

## Key Files to Modify/Move

| Current Location | New Location | Action |
|-----------------|--------------|--------|
| `/docs/` | `/frontendBook/docs/` | Move |
| `/src/` | `/frontendBook/src/` | Move |
| `/static/` | `/frontendBook/static/` | Move |
| `/docusaurus.config.js` | `/frontendBook/` | Move |
| `/sidebars.js` | `/frontendBook/` | Move |
| `/package.json` | `/frontendBook/` | Move |
| N/A | `/backend/.gitkeep` | Create |
| `/README.md` | `/README.md` | Update |
| `/.gitignore` | `/.gitignore` | Update |

## Complexity Tracking

No constitution violations to track. This is a straightforward restructure with:
- Simple file moves
- CSS-only UI fixes
- No new dependencies
- No architectural complexity

## Verification Plan

1. **Folder Structure**: `cd frontendBook && npm install && npm start`
2. **Text Visibility**: Manual check in light/dark modes
3. **Hero Width**: Visual inspection at various viewport sizes
4. **Card Responsiveness**: Test at 320px, 768px, 1200px, 1920px
5. **Mobile Sidebar**: DevTools mobile view test
6. **Production Build**: `cd frontendBook && npm run build`
7. **Lighthouse**: Run accessibility audit (target 90+)

## Next Steps

Run `/sp.tasks` to generate the implementation task list.
