# Quickstart: Docusaurus Purple Theme Upgrade

## Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Git for version control
- Basic knowledge of React and CSS

## Setup Environment

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd BookWriting_Hackathon1
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Switch to the feature branch**:
   ```bash
   git checkout 2-docusaurus-purple-theme
   ```

## Development Server

1. **Start the development server**:
   ```bash
   npm run start
   ```

2. **Open your browser** to `http://localhost:3000`

## Key Customization Files

### CSS & Theme Variables
- `src/css/custom.css` - Main CSS overrides and purple theme variables
- `docusaurus.config.js` - Theme configuration and color modes

### Pages
- `src/pages/index.js` - Custom homepage with enhanced hero section
- `src/pages/about.js` - About page explaining book purpose

### Navigation
- `docusaurus.config.js` - Navigation configuration (navbar items, "Book" link, etc.)

## Making Customizations

### Purple Theme Changes
1. Edit CSS variables in `src/css/custom.css` for purple-based theme
2. Use professional purple gradient with appropriate contrast ratios
3. Ensure both light and dark modes look excellent

### Navigation Enhancements
1. Modify navbar configuration in `docusaurus.config.js`
2. Rename "Documentation" to "Book"
3. Remove "Tutorials" and "Community" items
4. Add "About" navigation item

### Chapter Numbering
1. Update sidebar configuration to include numbered chapters (1.1, 1.2, etc.)
2. Ensure numbering is visible in both sidebar and page titles

## Testing Changes

1. **Visual Testing**:
   - Check all pages in both light and dark modes
   - Verify purple theme consistency across all pages
   - Test navigation functionality

2. **Performance Testing**:
   - Verify page load times remain under 3 seconds
   - Check that bundle size hasn't increased significantly

3. **Accessibility Testing**:
   - Verify WCAG 2.1 AA compliance
   - Check that purple color contrast ratios meet requirements
   - Test keyboard navigation

4. **Responsive Testing**:
   - Test on mobile, tablet, and desktop
   - Verify navigation adapts cleanly to different screen sizes

## Building for Production

```bash
npm run build
```

## Deploying

```bash
npm run deploy
```

## Troubleshooting

- If build fails: Check that no custom React contexts were introduced
- If purple theme doesn't appear: Verify CSS variables are properly defined
- If navigation doesn't work: Check docusaurus.config.js configuration
- If chapter numbering is missing: Verify sidebar configuration