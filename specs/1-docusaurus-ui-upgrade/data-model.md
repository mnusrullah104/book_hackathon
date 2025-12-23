# Data Model: Docusaurus UI/UX Upgrade

## Theme Configuration Entity

**Fields**:
- `themeType`: String (light | dark) - Current active theme
- `colorScheme`: Object - Color variables for the active theme
- `typographySettings`: Object - Font sizes, line heights, spacing values
- `userPreferences`: Object - User-specific theme and accessibility preferences

**Relationships**:
- Connected to all UI components that need theme-aware styling
- Linked to localStorage for persisting user preferences

## Navigation Structure Entity

**Fields**:
- `moduleId`: String - Unique identifier for documentation module
- `moduleName`: String - Display name for the module
- `chapters`: Array of Chapter objects - Collection of chapters within the module
- `isExpanded`: Boolean - Whether the module section is expanded in sidebar
- `activeChapterId`: String - ID of currently active chapter

**Relationships**:
- Each module contains multiple chapters
- Each chapter contains multiple sections
- Linked to documentation content files via file paths

## Chapter Entity

**Fields**:
- `chapterId`: String - Unique identifier for the chapter
- `chapterTitle`: String - Display title of the chapter
- `sections`: Array of Section objects - Collection of sections within the chapter
- `moduleId`: String - Reference to parent module
- `order`: Number - Display order within the module

**Relationships**:
- Belongs to a single module
- Contains multiple sections
- Linked to specific documentation content

## Section Entity

**Fields**:
- `sectionId`: String - Unique identifier for the section
- `sectionTitle`: String - Display title of the section
- `contentPath`: String - Path to the documentation content file
- `chapterId`: String - Reference to parent chapter
- `isVisible`: Boolean - Whether the section should be displayed in navigation

**Relationships**:
- Belongs to a single chapter
- Linked to specific documentation content file

## User Preferences Entity

**Fields**:
- `userId`: String - User identifier (or anonymous ID)
- `preferredTheme`: String (light | dark) - Default theme preference
- `fontSizeMultiplier`: Number - Multiplier for base font size
- `reducedMotion`: Boolean - Whether to disable animations
- `lastVisitedPage`: String - Last page visited for quick return

**Relationships**:
- Associated with user session or localStorage
- Affects theme and accessibility settings globally

## Validation Rules

- All theme types must be either 'light' or 'dark'
- Navigation structure must maintain consistent hierarchy (Module > Chapter > Section)
- All content paths must reference valid documentation files
- Color values must meet WCAG 2.1 AA contrast requirements (minimum 4.5:1 ratio)
- User preferences must be persisted across sessions

## State Transitions

- Theme: light ↔ dark (user can toggle between themes)
- Navigation: collapsed ↔ expanded (user can expand/collapse modules)
- Accessibility: enabled/disabled (based on user preferences and system settings)