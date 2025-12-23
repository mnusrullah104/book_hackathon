import React from 'react';
import Layout from '@theme/Layout';
import styles from './about.module.css';

function AboutPage() {
  return (
    <Layout
      title="About"
      description="Learn about Physical AI & Humanoid Robotics Book">
      <main className={styles.aboutPage}>
        <div className={styles.aboutHero}>
          <div className={styles.aboutBadge}>
            <span className={styles.badgeIcon}>📚</span>
            <span>About The Book</span>
          </div>
          <h1 className={styles.aboutTitle}>
            Master the Future of Robotics
          </h1>
          <p className={styles.aboutSubtitle}>
            A comprehensive guide to building intelligent humanoid robots with ROS 2, AI agents, and cutting-edge simulation technologies.
          </p>
        </div>

        <div className={styles.aboutContent}>
          <div className={styles.featuresGrid}>
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>🎯</div>
              <h3 className={styles.featureTitle}>Practical & Hands-On</h3>
              <p className={styles.featureDesc}>
                Learn by building real projects with step-by-step tutorials and production-ready code examples.
              </p>
            </div>

            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>🚀</div>
              <h3 className={styles.featureTitle}>Industry-Relevant</h3>
              <p className={styles.featureDesc}>
                Master technologies used by leading robotics companies and research institutions worldwide.
              </p>
            </div>

            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>💡</div>
              <h3 className={styles.featureTitle}>AI-First Approach</h3>
              <p className={styles.featureDesc}>
                Integrate LLMs, vision models, and AI agents to create truly intelligent robotic systems.
              </p>
            </div>

            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>🎓</div>
              <h3 className={styles.featureTitle}>Complete Curriculum</h3>
              <p className={styles.featureDesc}>
                From ROS 2 fundamentals to advanced AI integration - everything you need in one place.
              </p>
            </div>
          </div>

          <div className={styles.ctaSection}>
            <h2 className={styles.ctaTitle}>Ready to Start Learning?</h2>
            <p className={styles.ctaSubtitle}>
              Join thousands of developers building the next generation of intelligent robots.
            </p>
            <div className={styles.ctaButtons}>
              <a href="/docs/module-1/ros2-fundamentals" className={styles.ctaButton}>
                <span className={styles.btnIcon}>🚀</span>
                <span>Start Learning Now</span>
              </a>
            </div>
          </div>
        </div>
      </main>
    </Layout>
  );
}

export default AboutPage;