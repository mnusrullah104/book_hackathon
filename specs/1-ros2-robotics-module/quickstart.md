# Quickstart: Robotic Communication Systems Module

## Prerequisites

- Node.js (version 18 or higher)
- npm or yarn package manager
- Git for version control
- Text editor or IDE

## Installation

1. **Install Docusaurus globally** (if not already installed):
   ```bash
   npm install -g @docusaurus/core@latest
   ```

2. **Initialize Docusaurus project** in your repository:
   ```bash
   npx create-docusaurus@latest website classic
   ```

3. **Navigate to project directory**:
   ```bash
   cd website
   ```

## Project Structure Setup

1. **Create module directory**:
   ```bash
   mkdir -p docs/module-1
   ```

2. **Create the three chapter files**:
   ```bash
   touch docs/module-1/01-ros2-fundamentals.md
   touch docs/module-1/02-python-agents-rclpy.md
   touch docs/module-1/03-humanoid-urdf.md
   ```

## Configuration

1. **Update docusaurus.config.js** to include the new module in sidebar navigation:
   ```javascript
   module.exports = {
     // ... other config
     presets: [
       [
         'classic',
         /** @type {import('@docusaurus/preset-classic').Options} */
         ({
           docs: {
             sidebarPath: require.resolve('./sidebars.js'),
             // ... other options
           },
           // ... other presets
         }),
       ],
     ],
     // ... rest of config
   };
   ```

2. **Update sidebars.js** to include the module navigation:
   ```javascript
   module.exports = {
     docs: [
       {
         type: 'category',
         label: 'Module 1: Robotic Communication Systems',
         items: [
           'module-1/01-ros2-fundamentals',
           'module-1/02-python-agents-rclpy',
           'module-1/03-humanoid-urdf',
         ],
       },
     ],
   };
   ```

## Running the Development Server

1. **Start the development server**:
   ```bash
   npm start
   ```

2. **Open your browser** to http://localhost:3000 to view the documentation

## Adding Content

1. **Edit the chapter files** in `docs/module-1/` with your content
2. **Use standard Markdown syntax** for formatting
3. **Preview changes** automatically in the development server

## Building for Production

1. **Build the static site**:
   ```bash
   npm run build
   ```

2. **Serve the built site locally** (for testing):
   ```bash
   npm run serve
   ```

## Deployment

The built site can be deployed to GitHub Pages, Netlify, or any static hosting service following Docusaurus deployment guidelines.