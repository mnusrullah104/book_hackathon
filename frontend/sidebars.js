// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'introduction',
    {
      type: 'category',
      label: '1. Module 1: Robotic Communication Systems',
      items: [
        'module-1/ros2-fundamentals',
        'module-1/python-agents-rclpy',
        'module-1/humanoid-urdf',
      ],
    },
    {
      type: 'category',
      label: '2. Module 2: Digital Twin Simulation (Gazebo & Unity)',
      items: [
        'module-2/2.1-physics-simulation-gazebo',
        'module-2/2.2-environment-unity',
        'module-2/2.3-sensor-simulation',
      ],
    },
    {
      type: 'category',
      label: '3. Module 3: The AI-Robot Brain (NVIDIA Isaac™)',
      items: [
        'isaac-robot-brain/3.1-chapter-1-isaac-sim-fundamentals',
        'isaac-robot-brain/3.2-chapter-2-isaac-ros-perception-vslam',
        'isaac-robot-brain/3.3-chapter-3-navigation-with-nav2-humanoids',
      ],
    },
    {
      type: 'category',
      label: '4. Module 4: Vision-Language-Action (VLA)',
      items: [
        'vla-integration/4.1-chapter-1-voice-to-action-pipelines',
        'vla-integration/4.2-chapter-2-cognitive-planning-with-llms',
        'vla-integration/4.3-chapter-3-capstone-autonomous-humanoid',
      ],
    },
  ],
};

module.exports = sidebars;