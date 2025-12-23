---
sidebar_label: '1.3 Humanoid Modeling with URDF'
title: '1.3 Humanoid Modeling with URDF'
description: 'Learn how to model humanoid robots using URDF (Unified Robot Description Format) to define physical components, joints, and sensors.'
---

# 1.3 Humanoid Modeling with URDF

## Introduction to Robot Description Formats

Welcome to the third chapter of our robotics module, where we'll explore robot description formats, specifically URDF (Unified Robot Description Format), which is used to model humanoid robots with physical components, joints, and sensors. URDF is a fundamental component of ROS-based robotic systems, allowing you to define the physical structure of robots for simulation, visualization, and control.

Understanding URDF is crucial for creating humanoid robots as it defines how different parts of the robot are connected, how they move relative to each other, and how they interact with the environment. This chapter will teach you how to read and modify URDF files to customize robot properties like joint limits or sensor positions.

## URDF Basics: Links and Joints

### What is URDF?

URDF (Unified Robot Description Format) is an XML-based format used to describe robot models in ROS. It defines the physical structure of robots by specifying:

- **Links**: Rigid bodies that make up the robot's structure
- **Joints**: Kinematic relationships between links
- **Visual properties**: How the robot appears in simulation
- **Collision properties**: How the robot interacts with physics simulation
- **Inertial properties**: Mass and inertia characteristics for physics simulation

### Link Properties: Visual, Collision, and Inertial

Links represent the rigid bodies of a robot. Each link must define three key properties:

#### Visual Properties
Visual properties define how the robot appears in simulation and visualization tools:

```xml
<link name="base_link">
  <visual>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <cylinder length="0.6" radius="0.2"/>
    </geometry>
    <material name="blue">
      <color rgba="0 0 0.8 1"/>
    </material>
  </visual>
</link>
```

#### Collision Properties
Collision properties define how the robot interacts with physics simulation:

```xml
<link name="base_link">
  <collision>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <cylinder length="0.6" radius="0.2"/>
    </geometry>
  </collision>
</link>
```

#### Inertial Properties
Inertial properties define the mass and inertia characteristics for physics simulation:

```xml
<link name="base_link">
  <inertial>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <mass value="10"/>
    <inertia ixx="1.0" ixy="0.0" ixz="0.0" iyy="1.0" iyz="0.0" izz="1.0"/>
  </inertial>
</link>
```

## Joint Types and Their Applications

### Joint Properties and Types

Joints connect links and define their kinematic relationships. Common joint types include:

#### Revolute Joint
A joint that rotates around a single axis with defined limits:

```xml
<joint name="hip_joint" type="revolute">
  <parent link="torso"/>
  <child link="thigh"/>
  <origin xyz="0 0 -0.5" rpy="0 0 0"/>
  <axis xyz="0 1 0"/>
  <limit lower="-1.57" upper="1.57" effort="100" velocity="1"/>
</joint>
```

#### Continuous Joint
A joint that can rotate continuously around an axis:

```xml
<joint name="wheel_joint" type="continuous">
  <parent link="chassis"/>
  <child link="wheel"/>
  <origin xyz="0.2 0 -0.1" rpy="0 0 0"/>
  <axis xyz="0 1 0"/>
</joint>
```

#### Prismatic Joint
A joint that slides along an axis:

```xml
<joint name="slider_joint" type="prismatic">
  <parent link="base"/>
  <child link="slider"/>
  <origin xyz="0 0 0.1" rpy="0 0 0"/>
  <axis xyz="0 0 1"/>
  <limit lower="0" upper="0.5" effort="100" velocity="1"/>
</joint>
```

#### Fixed Joint
A joint with no movement (used to connect rigidly attached components):

```xml
<joint name="fixed_joint" type="fixed">
  <parent link="parent_link"/>
  <child link="child_link"/>
  <origin xyz="0 0 0.1" rpy="0 0 0"/>
</joint>
```

## Humanoid Robot Structure Modeling

### Complete Humanoid Robot Example

Here's a more complete example of a humanoid robot structure:

```xml
<?xml version="1.0"?>
<robot name="humanoid_robot">

  <!-- Torso -->
  <link name="torso">
    <visual>
      <geometry>
        <box size="0.3 0.2 0.5"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.3 0.2 0.5"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="10"/>
      <inertia ixx="1.0" ixy="0.0" ixz="0.0" iyy="1.0" iyz="0.0" izz="1.0"/>
    </inertial>
  </link>

  <!-- Head -->
  <link name="head">
    <visual>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
      <material name="skin">
        <color rgba="1 0.8 0.6 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="2"/>
      <inertia ixx="0.02" ixy="0.0" ixz="0.0" iyy="0.02" iyz="0.0" izz="0.02"/>
    </inertial>
  </link>

  <!-- Neck joint -->
  <joint name="neck_joint" type="revolute">
    <parent link="torso"/>
    <child link="head"/>
    <origin xyz="0 0 0.25" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-0.5" upper="0.5" effort="10" velocity="1"/>
  </joint>

  <!-- Left Arm -->
  <link name="left_shoulder">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.2"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.05" length="0.2"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01"/>
    </inertial>
  </link>

  <!-- Left Shoulder Joint -->
  <joint name="left_shoulder_joint" type="revolute">
    <parent link="torso"/>
    <child link="left_shoulder"/>
    <origin xyz="0.15 0 0.1" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="50" velocity="2"/>
  </joint>

  <!-- Left Elbow Joint -->
  <joint name="left_elbow_joint" type="revolute">
    <parent link="left_shoulder"/>
    <child link="left_forearm"/>
    <origin xyz="0 0 -0.2" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="50" velocity="2"/>
  </joint>

  <link name="left_forearm">
    <visual>
      <geometry>
        <cylinder radius="0.04" length="0.3"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.04" length="0.3"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.8"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01"/>
    </inertial>
  </link>

</robot>
```

## Sensors in URDF

### Adding Sensors to Robot Models

Sensors can be defined in URDF to specify their location and properties:

```xml
<!-- Camera Link -->
<link name="camera_link">
  <visual>
    <geometry>
      <box size="0.05 0.05 0.05"/>
    </geometry>
    <material name="black">
      <color rgba="0 0 0 1"/>
    </material>
  </visual>
  <collision>
    <geometry>
      <box size="0.05 0.05 0.05"/>
    </geometry>
  </collision>
  <inertial>
    <mass value="0.1"/>
    <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.001"/>
  </inertial>
</link>

<!-- Camera Mount Joint -->
<joint name="camera_joint" type="fixed">
  <parent link="head"/>
  <child link="camera_link"/>
  <origin xyz="0.05 0 0" rpy="0 0 0"/>
</joint>

<!-- Gazebo Sensor Definition -->
<gazebo reference="camera_link">
  <sensor type="camera" name="head_camera">
    <update_rate>30.0</update_rate>
    <camera name="head_camera">
      <horizontal_fov>1.3962634</horizontal_fov>
      <image>
        <width>800</width>
        <height>600</height>
        <format>R8G8B8</format>
      </image>
      <clip>
        <near>0.02</near>
        <far>300</far>
      </clip>
    </camera>
    <always_on>true</always_on>
    <visualize>true</visualize>
  </sensor>
</gazebo>
```

## Best Practices and Validation

### URDF Best Practices

1. **Naming Conventions**: Use descriptive and consistent names for links and joints
   - Use underscores for multi-word names: `left_arm_link`
   - Use prefixes to group related components: `left_shoulder_joint`, `right_shoulder_joint`

2. **Physical Accuracy**: Ensure inertial properties are physically realistic
   - Mass values should reflect the actual weight of components
   - Inertia tensors should match the geometry and mass distribution

3. **Joint Limits**: Set appropriate limits based on physical constraints
   - Don't set limits too wide or too narrow
   - Consider the actual mechanical limitations of the robot

4. **Validation**: Always validate your URDF files
   - Use the `check_urdf` command to validate the structure
   - Test in simulation to verify proper kinematics

### URDF Validation

You can validate your URDF files using ROS tools:

```bash
# Check URDF syntax and structure
check_urdf /path/to/robot.urdf

# Visualize the robot model
urdf_to_graphiz /path/to/robot.urdf
```

## Summary and Learning Objectives

After completing this chapter, you should understand:
- How to read and interpret URDF files that describe robot models
- How to modify URDF files to change robot properties like joint limits or sensor positions
- The fundamental components of URDF: links, joints, and their properties
- How to structure a humanoid robot model with proper kinematic relationships
- How to add sensors to robot models in URDF

These skills are essential for working with humanoid robots in ROS-based systems, allowing you to customize existing robot models or create new ones for simulation and control applications.