// @ts-check
// `@ts-check` enables tsdoc standard typing for JS doc comments

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'AI-Native Robotics Book',
  tagline: 'A comprehensive guide to ROS 2, AI agents, and humanoid robotics',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://book-hackathon-blond.vercel.app',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For Vercel deployment, use '/'
  baseUrl: '/',

  // GitHub pages deployment config.
  organizationName: 'mnusrullah104', // Usually your GitHub org/user name.
  projectName: 'book_hackathon', // Usually your repo name.

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // Edit this page links point to your repository
          editUrl:
            'https://github.com/mnusrullah104/BookWriting_Hackathon1/tree/main/frontend/',
        },
        blog: false, // Optional: disable the blog plugin
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      colorMode: {
        defaultMode: 'dark',
        disableSwitch: false,
        respectPrefersColorScheme: false,
      },
      navbar: {
        title: 'AI-Native Robotics Book',
        logo: {
          alt: 'AI-Native Robotics Book Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Book',
          },
          {
            to: '/about',
            label: 'About',
            position: 'left',
          },
          {
            to: '/chat',
            label: '💬 AI Chat',
            position: 'left',
            className: 'navbar-chat-link',
          },
          {
            href: 'https://github.com/mnusrullah104/BookWriting_Hackathon1',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Module 1: Robotic Communication Systems',
                to: '/docs/module-1/ros2-fundamentals',
              },
            ],
          },
          {
            title: 'Resources',
            items: [
              {
                label: 'About This Book',
                to: '/about',
              },
              {
                label: 'ROS 2 Documentation',
                href: 'https://docs.ros.org/en/rolling/',
              },
            ],
          },
          {
            title: 'Connect',
            items: [
              {
                label: 'GitHub Repository',
                href: 'https://github.com/mnusrullah104/BookWriting_Hackathon1',
              },
              {
                label: 'Report Issues',
                href: 'https://github.com/mnusrullah104/BookWriting_Hackathon1/issues',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} AI-Native Robotics Book. Built with Docusaurus.`,
      },
      prism: {
        theme: require('prism-react-renderer').themes.github,
        darkTheme: require('prism-react-renderer').themes.dracula,
      },
    }),
};

module.exports = config;