import React, { useState, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import DocSidebar from '@theme-original/DocSidebar';

const CustomDocSidebar = (props) => {
  const { theme } = useTheme();
  const [expandedItems, setExpandedItems] = useState({});
  const { sidebar } = props;

  // Initialize expanded state based on current page
  useEffect(() => {
    const initialExpanded = {};
    const findActiveItems = (items, activePath) => {
      items.forEach(item => {
        if (item.type === 'category') {
          if (item.items.some(subItem => subItem.permalink === activePath)) {
            initialExpanded[item.label] = true;
            findActiveItems(item.items, activePath);
          } else if (item.items.some(subItem =>
            subItem.type === 'category' &&
            subItem.items.some(subSubItem => subSubItem.permalink === activePath)
          )) {
            initialExpanded[item.label] = true;
          }
        }
      });
    };

    if (props.activePath) {
      findActiveItems(sidebar, props.activePath);
      setExpandedItems(initialExpanded);
    }
  }, [sidebar, props.activePath]);

  const toggleExpanded = (itemLabel) => {
    setExpandedItems(prev => ({
      ...prev,
      [itemLabel]: !prev[itemLabel]
    }));
  };

  // Custom rendering logic for collapsible items
  const renderCustomSidebarItem = (item, level = 0) => {
    if (item.type === 'category') {
      const isExpanded = expandedItems[item.label] ?? item.collapsible;
      const isCurrent = props.activePath && item.items.some(i => i.permalink === props.activePath);

      return (
        <div
          key={item.label}
          className={`menu__list-item ${isCurrent ? 'menu__list-item--active' : ''}`}
          style={{ paddingLeft: level > 0 ? `${level * 1.2}rem` : '0' }}
        >
          <div
            className={`menu__list-item-collapsible ${isExpanded ? 'menu__list-item-collapsible--expanded' : ''}`}
            onClick={() => item.collapsible && toggleExpanded(item.label)}
            onKeyDown={(e) => {
              if (item.collapsible && (e.key === 'Enter' || e.key === ' ')) {
                e.preventDefault();
                toggleExpanded(item.label);
              }
            }}
            tabIndex={0}
            role="button"
            aria-expanded={isExpanded}
            aria-controls={`sidebar-category-${item.label.replace(/\s+/g, '-').toLowerCase()}`}
            style={{ cursor: item.collapsible ? 'pointer' : 'default' }}
          >
            <div className="menu__list-item-collapsible-content">
              <span className="menu__list-item-collapsible-title">{item.label}</span>
              {item.collapsible && (
                <span className={`menu__list-item-collapsible-arrow ${isExpanded ? 'menu__list-item-collapsible-arrow--expanded' : ''}`}>
                  {isExpanded ? '▼' : '▶'}
                </span>
              )}
            </div>
          </div>

          {isExpanded && (
            <ul id={`sidebar-category-${item.label.replace(/\s+/g, '-').toLowerCase()}`} className="menu__list">
              {item.items.map(subItem => renderCustomSidebarItem(subItem, level + 1))}
            </ul>
          )}
        </div>
      );
    } else {
      const isCurrent = props.activePath === item.permalink;
      return (
        <li key={item.href || item.permalink} className={`menu__list-item ${isCurrent ? 'menu__list-item--active' : ''}`}>
          <a
            className={`menu__link ${isCurrent ? 'menu__link--active' : ''}`}
            href={item.href || item.permalink}
            target={item.href ? '_blank' : undefined}
            rel={item.href ? 'noopener noreferrer' : undefined}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                window.location.href = item.href || item.permalink;
              }
            }}
            tabIndex={0}
          >
            {item.label}
          </a>
        </li>
      );
    }
  };

  return (
    <div className={`custom-doc-sidebar custom-doc-sidebar--${theme}`}>
      <DocSidebar {...props} />
    </div>
  );
};

export default CustomDocSidebar;