---
title: Home
slug: /
---

import styles from './index.module.css';

<div className={styles.heroBanner}>
  <h1 className="hero__title">AI-Native Robotics Book</h1>
  <p className="hero__subtitle">A comprehensive guide to ROS 2, AI agents, and humanoid robotics</p>
  <div className={styles.buttons}>
    <a className="button button--secondary button--lg" href="/docs/module-1/ros2-fundamentals">
      Get Started
    </a>
    <a className="button button--outline button--lg" href="/docs/module-1/python-agents-rclpy">
      Learn More
    </a>
  </div>
</div>

<div className={styles.featuresSection}>
  <div className={styles.cardContainer}>
    <div className={styles.card}>
      <div className={styles.cardIcon}>🤖</div>
      <h3 className={styles.cardTitle}>ROS 2 Fundamentals</h3>
      <p className={styles.cardDescription}>
        Master the core concepts of Robot Operating System 2 including nodes, topics, services, and communication patterns.
      </p>
    </div>
    <div className={styles.card}>
      <div className={styles.cardIcon}>🧠</div>
      <h3 className={styles.cardTitle}>AI Agents Integration</h3>
      <p className={styles.cardDescription}>
        Learn how to create communication nodes in Python and bridge AI agents to robot controllers for intelligent behaviors.
      </p>
    </div>
    <div className={styles.card}>
      <div className={styles.cardIcon}>🦾</div>
      <h3 className={styles.cardTitle}>Humanoid Modeling</h3>
      <p className={styles.cardDescription}>
        Understand URDF for modeling humanoid robots with physical components, joints, and sensors.
      </p>
    </div>
  </div>
</div>