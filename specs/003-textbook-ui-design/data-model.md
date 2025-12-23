# Data Model: Textbook UI Design

**Feature**: 003-textbook-ui-design
**Date**: 2025-12-21
**Phase**: 1 (Design)

## Overview

This feature is UI-only with no backend data persistence. The "data model" describes the conceptual entities rendered by the UI and their relationships as defined in Markdown content and Docusaurus configuration.

## UI Entities

### Module

A major section of the textbook containing related chapters.

| Attribute | Type | Source | Description |
|-----------|------|--------|-------------|
| id | string | sidebars.js | Unique identifier (e.g., "module-1") |
| label | string | sidebars.js | Display name (e.g., "Module 1: Robotic Communication Systems") |
| position | number | sidebars.js | Order in sidebar (1-4) |
| chapters | Chapter[] | sidebars.js | Child chapters |
| isExpanded | boolean | UI state | Whether module is expanded in sidebar |

**Example** (from sidebars.js):
```javascript
{
  type: 'category',
  label: '1. Module 1: Robotic Communication Systems',
  items: ['module-1/ros2-fundamentals', ...]
}
```

---

### Chapter

An individual content unit within a module.

| Attribute | Type | Source | Description |
|-----------|------|--------|-------------|
| id | string | File path | Unique identifier (e.g., "module-1/ros2-fundamentals") |
| title | string | Frontmatter | Display title |
| sidebarLabel | string | Frontmatter | Sidebar display name |
| moduleId | string | Directory | Parent module reference |
| content | MDX | .md file | Chapter content |
| isActive | boolean | UI state | Whether currently viewing |

**Example** (from docs/module-1/ros2-fundamentals.md):
```markdown
---
sidebar_label: 'ROS 2 Fundamentals'
title: 'Chapter 1: ROS 2 Fundamentals'
---

[Chapter content...]
```

---

### Theme

The visual appearance setting affecting colors throughout the UI.

| Attribute | Type | Source | Description |
|-----------|------|--------|-------------|
| mode | "light" \| "dark" | localStorage | Current theme mode |
| systemPreference | boolean | docusaurus.config.js | Whether to respect OS preference |
| persistKey | string | Docusaurus | localStorage key for persistence |

**Configuration** (from docusaurus.config.js):
```javascript
colorMode: {
  defaultMode: 'light',
  disableSwitch: false,
  respectPrefersColorScheme: true,
}
```

---

## Entity Relationships

```text
┌─────────────────────────────────────────────────────┐
│                    Sidebar                          │
│  ┌───────────────────────────────────────────────┐  │
│  │ Module 1                          [expanded]  │  │
│  │   ├── Chapter 1.1                [active]     │  │
│  │   ├── Chapter 1.2                             │  │
│  │   └── Chapter 1.3                             │  │
│  ├───────────────────────────────────────────────┤  │
│  │ Module 2                         [collapsed]  │  │
│  ├───────────────────────────────────────────────┤  │
│  │ Module 3                         [collapsed]  │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘

Relationships:
- Module 1:N Chapter (parent-child)
- Chapter N:1 Module (belongs to)
- Theme 1:1 UI (global setting)
```

## UI State Model

### Sidebar State

| State | Type | Initial | Transitions |
|-------|------|---------|-------------|
| expandedModules | Set<string> | Current module | User click expands/collapses |
| activeChapter | string | From URL | Navigation changes active |
| isMobileOpen | boolean | false | Hamburger toggle |

### Theme State

| State | Type | Initial | Transitions |
|-------|------|---------|-------------|
| mode | "light" \| "dark" | System preference or localStorage | Toggle click |

## CSS Custom Properties (Design Tokens)

The UI styling is controlled by CSS custom properties defined in `src/css/custom.css`:

### Typography Tokens

```css
--ifm-font-size-base: 18px;
--ifm-line-height-base: 1.6;
--ifm-heading-line-height: 1.3;
```

### Color Tokens

```css
/* Light theme */
--ifm-color-primary: #8a2be2;
--ifm-background-color: #ffffff;

/* Dark theme */
--ifm-color-primary: #9a46e8;
--ifm-background-color: #1b1b1d;
```

### Spacing Tokens

```css
--ifm-spacing-xs: 0.5rem;
--ifm-spacing-sm: 0.75rem;
--ifm-spacing-md: 1rem;
--ifm-spacing-lg: 1.5rem;
--ifm-spacing-xl: 2rem;
```

## No Database/API

This feature has:
- ❌ No database tables
- ❌ No API endpoints
- ❌ No backend services
- ✅ Static file-based content (Markdown)
- ✅ Client-side state only (theme, sidebar)
