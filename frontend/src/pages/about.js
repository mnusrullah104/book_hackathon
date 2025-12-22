import React from 'react';
import clsx from 'clsx';
import Layout from '@theme/Layout';
import styles from './about.module.css';

function AboutPage() {
  return (
    <Layout
      title="About"
      description="About the AI-Native Robotics Book">
      <main className={clsx('container', styles.aboutPage)}>
        <div className="row">
          <div className="col">
            <div className="margin-vert--lg">
              <h1 className={styles.aboutTitle}>About This Book</h1>

              <div className="chapter-intro">
                <div className="chapter-number">Foreword</div>
                <h2 className="chapter-title">AI-Native Robotics: The Future is Now</h2>
                <p className="chapter-description">
                  Welcome to the comprehensive guide on AI-Native Robotics, where artificial intelligence meets
                  the cutting edge of robotic systems. This book explores the convergence of AI agents,
                  ROS 2 communication systems, and humanoid robotics in the modern era.
                </p>
              </div>

              <section className={clsx('margin-vert--lg', styles.aboutSection)}>
                <h2>Purpose of This Book</h2>
                <p>
                  The AI-Native Robotics Book is designed to bridge the gap between traditional robotics
                  and the new era of AI-driven robotic systems. As robotics technology evolves, the integration
                  of artificial intelligence has become essential for creating more autonomous, adaptable,
                  and intelligent machines.
                </p>
                <p>
                  This book provides a comprehensive exploration of how modern AI agents can be integrated
                  with ROS 2 systems, how digital twin technologies enhance robotic development, and how
                  these technologies come together in humanoid robotics applications.
                </p>
              </section>

              <section className={clsx('margin-vert--lg', styles.aboutSection)}>
                <h2>Author Background</h2>
                <p>
                  This book is the result of extensive research and development in the field of AI-native
                  robotics. The content combines theoretical foundations with practical implementation
                  examples, providing readers with both the knowledge and tools needed to develop
                  next-generation robotic systems.
                </p>
                <p>
                  The author has years of experience in robotics, AI development, and ROS 2 systems,
                  bringing real-world insights to complex theoretical concepts.
                </p>
              </section>

              <section className={clsx('margin-vert--lg', styles.aboutSection)}>
                <h2>Hackathon Context</h2>
                <p>
                  This book was developed as part of a specialized hackathon focused on advancing
                  AI-native robotics technologies. The hackathon brought together experts from
                  various fields to explore the intersection of AI, robotics, and emerging technologies.
                </p>
                <p>
                  The content reflects the collaborative spirit and innovative approaches that
                  emerged from this intensive development period, showcasing cutting-edge techniques
                  and practical implementations.
                </p>
              </section>

              <section className={clsx('margin-vert--lg', styles.aboutSection)}>
                <h2>Target Audience</h2>
                <p>
                  This book is designed for:
                </p>
                <ul>
                  <li>Robotics engineers looking to integrate AI technologies</li>
                  <li>AI researchers interested in robotic applications</li>
                  <li>Software developers working on autonomous systems</li>
                  <li>Academic researchers in robotics and AI</li>
                  <li>Students studying advanced robotics concepts</li>
                </ul>
              </section>

              <section className={clsx('margin-vert--lg', styles.aboutSection)}>
                <h2>How to Use This Book</h2>
                <p>
                  This book is structured as a comprehensive guide that can be approached in multiple ways:
                </p>
                <ul>
                  <li><strong>Sequential Reading:</strong> Follow the chapters in order for a complete understanding</li>
                  <li><strong>Modular Approach:</strong> Each chapter is designed to be self-contained</li>
                  <li><strong>Hands-on Practice:</strong> All examples include practical implementation code</li>
                  <li><strong>Reference Guide:</strong> Use as a reference for specific topics and techniques</li>
                </ul>
              </section>
            </div>
          </div>
        </div>
      </main>
    </Layout>
  );
}

export default AboutPage;