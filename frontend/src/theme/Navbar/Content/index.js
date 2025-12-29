/**
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React, { useState, useEffect } from 'react';
import clsx from 'clsx';
import {
  useThemeConfig,
  ErrorCauseBoundary,
  ThemeClassNames,
} from '@docusaurus/theme-common';
import {
  splitNavbarItems,
  useNavbarMobileSidebar,
} from '@docusaurus/theme-common/internal';
import NavbarItem from '@theme/NavbarItem';
import NavbarColorModeToggle from '@theme/Navbar/ColorModeToggle';
import SearchBar from '@theme/SearchBar';
import NavbarMobileSidebarToggle from '@theme/Navbar/MobileSidebar/Toggle';
import NavbarLogo from '@theme/Navbar/Logo';
import NavbarSearch from '@theme/Navbar/Search';
import BrowserOnly from '@docusaurus/BrowserOnly';

function useNavbarItems() {
  return useThemeConfig().navbar.items;
}

function NavbarItems({ items }) {
  return (
    <>
      {items.map((item, i) => (
        <ErrorCauseBoundary
          key={i}
          onError={(error) =>
            new Error(
              `A theme navbar item failed to render.
Please double-check the following navbar item (themeConfig.navbar.items) of your Docusaurus config:
${JSON.stringify(item, null, 2)}`,
              { cause: error },
            )
          }>
          <NavbarItem {...item} />
        </ErrorCauseBoundary>
      ))}
    </>
  );
}

function NavbarContentLayout({ left, right }) {
  return (
    <div className="navbar__inner">
      <div
        className={clsx(
          ThemeClassNames.layout.navbar.containerLeft,
          'navbar__items',
        )}>
        {left}
      </div>
      <div
        className={clsx(
          ThemeClassNames.layout.navbar.containerRight,
          'navbar__items navbar__items--right',
        )}>
        {right}
      </div>
    </div>
  );
}

// Custom Chat Navbar Item - Only visible on Book pages
function ChatNavbarItem() {
  const [isBookPage, setIsBookPage] = useState(false);

  useEffect(() => {
    const checkPath = () => {
      const path = window.location.pathname;
      // Show AI Chat only on docs/book pages (paths starting with /docs)
      setIsBookPage(path.startsWith('/docs') || path === '/book');
    };

    checkPath();
    window.addEventListener('locationchange', checkPath);
    return () => window.removeEventListener('locationchange', checkPath);
  }, []);

  if (!isBookPage) return null;

  return (
    <NavbarItem
      to="/chat"
      label="AI Chat"
      position="left"
      className="navbar-chat-link"
      prepend
    />
  );
}

// Auth button wrapper with BrowserOnly for SSR
function AuthButtonWrapper() {
  return (
    <BrowserOnly fallback={<div className="navbar-auth-button loading"><span className="auth-loader"></span></div>}>
      {() => {
        const AuthButton = require('@site/src/components/navbar/AuthButton').default;
        return <AuthButton />;
      }}
    </BrowserOnly>
  );
}

export default function NavbarContent() {
  const mobileSidebar = useNavbarMobileSidebar();
  const items = useNavbarItems();
  const [leftItems, rightItems] = splitNavbarItems(items);
  const searchBarItem = items.find((item) => item.type === 'search');

  return (
    <NavbarContentLayout
      left={
        <>
          <NavbarLogo />
          <NavbarItems items={leftItems} />
          {/* AI Chat - Only visible on Book pages */}
          <ChatNavbarItem />
        </>
      }
      right={
        <>
          <NavbarItems items={rightItems} />
          <AuthButtonWrapper />
          <NavbarColorModeToggle />
          {!mobileSidebar.disabled && <NavbarMobileSidebarToggle />}
          {!searchBarItem && (
            <NavbarSearch>
              <SearchBar />
            </NavbarSearch>
          )}
        </>
      }
    />
  );
}
