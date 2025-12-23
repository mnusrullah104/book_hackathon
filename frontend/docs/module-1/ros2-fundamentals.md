---
sidebar_label: '1.1 ROS 2 Fundamentals'
title: '1.1 ROS 2 Fundamentals'
description: 'Understanding the core concepts of Robot Operating System 2 (ROS 2) including nodes, topics, services, and communication patterns.'
---

# 1.1 ROS 2 Fundamentals

## Introduction to ROS 2

Welcome to the foundational chapter on Robot Operating System 2 (ROS 2). This chapter will introduce you to the core concepts that underpin modern robotics development and communication systems. ROS 2 is a flexible framework for writing robot software that provides services designed for a heterogeneous computer cluster, including hardware abstraction, device drivers, libraries, visualizers, message-passing, package management, and more.

ROS 2 is the evolution of the original ROS framework, addressing key limitations such as real-time support, security, and improved communication protocols. It's designed to support complex robotics applications in research, industrial automation, and commercial robotics.

## Core Concepts: Nodes, Topics, and Services

### Nodes

A node is an executable that uses ROS 2 to communicate with other nodes. Nodes are the fundamental building blocks of a ROS 2 system. Each node can perform specific functions such as sensor data processing, actuator control, or data fusion. Nodes are designed to be modular and reusable, allowing developers to create complex systems by combining simple, specialized nodes.

In a typical robotic system, you might have nodes for:
- Sensor data acquisition (camera, LIDAR, IMU)
- Control algorithms (path planning, motion control)
- Data processing (object detection, mapping)
- User interfaces (visualization, command interfaces)

### Topics and Publish/Subscribe Communication

Topics are named buses over which nodes exchange messages. The publish/subscribe communication pattern allows for asynchronous, decoupled communication between nodes. Publishers send messages to a topic, and subscribers receive messages from a topic. This pattern enables loose coupling between nodes, as publishers don't need to know which nodes are subscribed to their topics, and subscribers don't need to know which nodes are publishing to their topics.

Key characteristics of topic-based communication:
- **Asynchronous**: Publishers and subscribers don't need to be active simultaneously
- **Many-to-many**: Multiple publishers can publish to the same topic, and multiple subscribers can subscribe to the same topic
- **Anonymous**: Publishers and subscribers are unaware of each other's existence
- **Data-driven**: Communication is triggered by data availability rather than explicit requests

### Services

Services provide a request/response communication pattern that is synchronous and point-to-point. A service client sends a request to a service server and waits for a response. This pattern is appropriate for operations that have a clear input/output relationship and where the client needs to wait for the result before proceeding.

Service communication is characterized by:
- **Synchronous**: The client waits for the response before continuing
- **Point-to-point**: Communication occurs between a specific client and server
- **Request-response**: Clear input/output relationship
- **Stateless**: Each service call is independent of others

## Communication Patterns: Publish/Subscribe vs Request/Response

Understanding when to use publish/subscribe versus service calls is crucial for effective ROS 2 system design.

### Publish/Subscribe (Topics) Use Cases

Use publish/subscribe communication when:
- You have continuous data streams (sensor data, robot state)
- Multiple nodes need the same information simultaneously
- You want decoupled, asynchronous communication
- The publisher doesn't need to know who receives the data
- You're implementing broadcast-style communication

Example: A camera node publishing image data to a topic that multiple perception nodes can subscribe to for different processing tasks (object detection, depth estimation, etc.).

### Service Calls Use Cases

Use service communication when:
- You need a specific response to a specific request
- The operation has a clear start and end
- You need to ensure the request was processed before continuing
- You're implementing RPC-style functionality
- You need synchronous behavior

Example: A navigation node requesting a path planning service to compute a route from a start to a goal location, then waiting for the computed path before proceeding.

## Practical Example: Simple Communication Architecture

Let's consider a simple robot system to illustrate these concepts in practice:

Imagine a mobile robot with a camera and a simple object detection system. The architecture might include:

1. **Camera Driver Node**: Publishes raw image data to the `/camera/image_raw` topic
2. **Object Detection Node**: Subscribes to `/camera/image_raw`, processes the image, and publishes detection results to `/object_detections` topic
3. **Navigation Node**: Subscribes to `/object_detections` to avoid obstacles during navigation
4. **Control Node**: Provides a service `/move_to_goal` that accepts coordinates and moves the robot to the specified location

This architecture demonstrates both communication patterns:
- Continuous sensor data flows through topics
- Goal requests use service calls for synchronous, specific responses

## Summary and Learning Objectives

After completing this chapter, you should understand:
- The fundamental concepts of nodes, topics, and services in ROS 2
- The differences between publish/subscribe and request/response communication patterns
- When to use each communication pattern based on the requirements of your robotic system
- How to design a simple communication architecture using these concepts

These foundational concepts form the basis for more complex robotic systems and will be essential as you progress through the subsequent chapters in this module.