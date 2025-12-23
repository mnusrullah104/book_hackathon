# Data Model: Frontend Refactor & UI Fix (Book-Only Phase)

**Feature**: 006-frontend-book-refactor
**Date**: 2025-12-22
**Purpose**: Define folder structure entities and CSS styling targets

## Key Entities

This feature is primarily a structural refactor with CSS fixes. The "entities" are folder structures and styling targets.

### 1. Folder Structure

**Description**: New monorepo-style folder organization

| Entity | Location | Contents |
|--------|----------|----------|
| frontendBook | /frontendBook | Complete Docusaurus site |
| backend | /backend | Empty placeholder for future |
| specs | /specs | Feature specifications (unchanged) |
| history | /history | Prompt records (unchanged) |

### 2. FrontendBook Contents

**Description**: Complete Docusaurus installation

| Path | Purpose |
|------|---------|
| frontendBook/docs/ | Markdown documentation content |
| frontendBook/src/ | React components, CSS, pages |
| frontendBook/static/ | Static assets (images, fonts) |
| frontendBook/docusaurus.config.js | Site configuration |
| frontendBook/sidebars.js | Navigation structure |
| frontendBook/package.json | Dependencies and scripts |

### 3. CSS Theme Entities

**Description**: Styling variables and targets

| Entity | Light Mode | Dark Mode | Purpose |
|--------|------------|-----------|---------|
| --rb-text-body | #1a1a1a | #e8e8e8 | Body text color |
| --rb-text-heading | #2d2d2d | #f0f0f0 | Heading color |
| --rb-sidebar-text | #333333 | #d0d0d0 | Sidebar navigation |
| --rb-bg-code | #f5f5f5 | #1e1e1e | Code block background |
| --ifm-color-primary | #8a2be2 | #9a46e8 | Purple accent |

### 4. Layout Components

**Description**: Key UI components affected by this feature

| Component | Current Issue | Target State |
|-----------|---------------|--------------|
| Hero Banner | Container-locked | Full viewport width |
| Feature Cards | Fixed pixel width | Fluid fr/percentage |
| Content Area | Variable width | 75ch max-width |
| Sidebar | Works on desktop | Mobile drawer verified |

## Relationships

```
Repository Root
├── frontendBook/           # Docusaurus site (MOVED FROM ROOT)
│   ├── docs/               # Content
│   ├── src/                # Components
│   │   ├── css/custom.css  # Theme overrides
│   │   └── pages/          # Custom pages (index.md, etc.)
│   └── static/             # Assets
├── backend/                # EMPTY (future use)
├── specs/                  # Feature specs (UNCHANGED)
├── history/                # Prompt records (UNCHANGED)
└── .specify/               # Tooling (UNCHANGED)
```

## Migration Mapping

| Before (Root) | After (frontendBook/) |
|---------------|----------------------|
| /docs | /frontendBook/docs |
| /src | /frontendBook/src |
| /static | /frontendBook/static |
| /docusaurus.config.js | /frontendBook/docusaurus.config.js |
| /sidebars.js | /frontendBook/sidebars.js |
| /package.json | /frontendBook/package.json |
| /node_modules | /frontendBook/node_modules |

## No Database Required

This feature is frontend-only static site. No database, API, or backend entities are needed.
