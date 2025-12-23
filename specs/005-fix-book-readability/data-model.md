# Data Model: Fix & Redesign Book UI for Readability

**Feature**: 005-fix-book-readability
**Date**: 2025-12-22
**Purpose**: Define UI entities and CSS variable structure

## Key Entities

This feature is CSS-only and doesn't involve data storage. The "entities" are CSS variable namespaces and styling targets.

### 1. Theme

**Description**: Color mode affecting all UI elements

| Attribute | Light Mode Value | Dark Mode Value |
|-----------|-----------------|-----------------|
| Background | `#ffffff` | `#121212` |
| Surface | `#f8f8f8` | `#1e1e1e` |
| Body Text | `#1a1a1a` | `#e8e8e8` |
| Muted Text | `#4a4a4a` | `#b0b0b0` |
| Border | `#e0e0e0` | `#333333` |

### 2. Text Level

**Description**: Typography hierarchy with specific contrast requirements

| Level | Light Mode Color | Dark Mode Color | Font Size | Weight | Contrast Req |
|-------|-----------------|-----------------|-----------|--------|--------------|
| Body | `#1a1a1a` | `#e8e8e8` | 18px | 400 | 4.5:1 |
| H1 | `#8a2be2` (purple) | `#b366ff` | 2.5em | 700 | 3:1 |
| H2 | `#2d2d2d` | `#f0f0f0` | 2em | 600 | 3:1 |
| H3 | `#333333` | `#e8e8e8` | 1.75em | 600 | 3:1 |
| H4 | `#404040` | `#d8d8d8` | 1.5em | 500 | 3:1 |
| Code | `#1a1a1a` | `#e0e0e0` | 95% | 400 | 4.5:1 |
| Nav | `#333333` | `#d0d0d0` | 1rem | 500 | 4.5:1 |

### 3. Content Area

**Description**: Main reading region constraints

| Attribute | Value | Rationale |
|-----------|-------|-----------|
| Max Width | 75ch | Optimal reading line length |
| Padding Horizontal | 2rem | Breathing room |
| Padding Vertical | 1.5rem | Section separation |
| Line Height | 1.6 | Comfortable reading |

### 4. Sidebar

**Description**: Navigation panel styling

| Attribute | Light Mode | Dark Mode |
|-----------|------------|-----------|
| Background | `#f8f8f8` | `#1a1a1a` |
| Text | `#333333` | `#d0d0d0` |
| Active Text | `#8a2be2` | `#b366ff` |
| Active Background | `rgba(138,43,226,0.1)` | `rgba(138,43,226,0.15)` |
| Hover Background | `rgba(0,0,0,0.05)` | `rgba(255,255,255,0.05)` |
| Border | `#e0e0e0` | `#333333` |

### 5. Code Block

**Description**: Code display styling

| Attribute | Light Mode | Dark Mode |
|-----------|------------|-----------|
| Background | `#f5f5f5` | `#1e1e1e` |
| Text | `#1a1a1a` | `#e0e0e0` |
| Border | `#e0e0e0` | `#333333` |
| Keyword | `#0066cc` | `#6699ff` |
| String | `#008800` | `#66cc66` |
| Comment | `#666666` | `#999999` |

### 6. Hero/Header

**Description**: Homepage and section header styling

| Attribute | Value |
|-----------|-------|
| Background | Solid color (no gradients with text) |
| Title Color | `#ffffff` (on purple bg) or `#1a1a1a` (on light bg) |
| Subtitle Color | `rgba(255,255,255,0.9)` or `#4a4a4a` |
| Button Text | High contrast against button background |

## CSS Variable Namespace

```
:root {
  /* Body text */
  --rb-text-body: #1a1a1a;
  --rb-text-heading: #2d2d2d;
  --rb-text-muted: #4a4a4a;
  
  /* Backgrounds */
  --rb-bg-primary: #ffffff;
  --rb-bg-secondary: #f8f8f8;
  --rb-bg-code: #f5f5f5;
  
  /* Sidebar */
  --rb-sidebar-text: #333333;
  --rb-sidebar-active: #8a2be2;
  --rb-sidebar-bg: #f8f8f8;
  
  /* Borders */
  --rb-border-color: #e0e0e0;
}

html[data-theme='dark'] {
  --rb-text-body: #e8e8e8;
  --rb-text-heading: #f0f0f0;
  --rb-text-muted: #b0b0b0;
  
  --rb-bg-primary: #121212;
  --rb-bg-secondary: #1e1e1e;
  --rb-bg-code: #1e1e1e;
  
  --rb-sidebar-text: #d0d0d0;
  --rb-sidebar-active: #b366ff;
  --rb-sidebar-bg: #1a1a1a;
  
  --rb-border-color: #333333;
}
```

## Relationships

```
Theme (light/dark)
  └── affects all entities below
  
Content Area
  ├── Body Text (uses --rb-text-body)
  ├── Headings (H1 special, H2-H6 use --rb-text-heading)
  └── Code Blocks (uses --rb-bg-code, --rb-text-body)

Sidebar
  ├── Navigation Items (uses --rb-sidebar-text)
  └── Active State (uses --rb-sidebar-active)

Hero/Header
  └── Standalone styling (high contrast combinations)
```
