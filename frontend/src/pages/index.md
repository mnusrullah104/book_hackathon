---
title: Home
slug: /
---

import styles from './index.module.css';

<div className={styles.heroBanner}>
  <div className={styles.heroContent}>
    <div className={styles.heroBadge}>
      <span className={styles.badgeIcon}>✨</span>
      <span>AI-Powered Learning</span>
    </div>
    <h1 className={styles.heroTitle}>
      Physical AI & Humanoid Robotics
    </h1>
    <p className={styles.heroSubtitle}>
      Master intelligent robot systems with ROS 2, Isaac Sim, and AI agents. Build real-world humanoid robots with cutting-edge AI and simulation technologies.
    </p>
    <div className={styles.heroButtons}>
      <a href="/docs/module-1/ros2-fundamentals" className={styles.btnPrimary}>
        <span className={styles.btnIcon}>🚀</span>
        <span>Start Learning</span>
      </a>
      <a href="/about" className={styles.btnSecondary}>
        <span className={styles.btnIcon}>📖</span>
        <span>Explore Content</span>
      </a>
    </div>
  </div>
</div>

<div className={styles.cardsSection}>
  <div className={styles.cardsGrid}>
    <div className={styles.card}>
      <div className={styles.cardIcon}>🤖</div>
      <h3 className={styles.cardTitle}>ROS 2 Fundamentals</h3>
      <p className={styles.cardDesc}>Master robot communication, nodes, topics, and Python agents for intelligent behavior.</p>
      <a href="/docs/module-1/ros2-fundamentals" className={styles.cardLink}>Learn More →</a>
    </div>

    <div className={styles.card}>
      <div className={styles.cardIcon}>🎮</div>
      <h3 className={styles.cardTitle}>Simulation & Testing</h3>
      <p className={styles.cardDesc}>Build digital twins with Gazebo and Unity for rapid prototyping and validation.</p>
      <a href="/docs/module-2/2.1-physics-simulation-gazebo" className={styles.cardLink}>Learn More →</a>
    </div>

    <div className={styles.card}>
      <div className={styles.cardIcon}>👁️</div>
      <h3 className={styles.cardTitle}>Computer Vision</h3>
      <p className={styles.cardDesc}>Implement Isaac Sim perception, Visual SLAM, and autonomous navigation systems.</p>
      <a href="/docs/isaac-robot-brain/3.1-chapter-1-isaac-sim-fundamentals" className={styles.cardLink}>Learn More →</a>
    </div>

    <div className={styles.card}>
      <div className={styles.cardIcon}>🧠</div>
      <h3 className={styles.cardTitle}>AI Integration</h3>
      <p className={styles.cardDesc}>Connect LLMs and VLA models for voice commands and cognitive planning capabilities.</p>
      <a href="/docs/vla-integration/4.1-chapter-1-voice-to-action-pipelines" className={styles.cardLink}>Learn More →</a>
    </div>
  </div>
</div>

