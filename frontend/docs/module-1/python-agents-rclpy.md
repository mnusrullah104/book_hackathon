---
sidebar_label: '1.2 Python Agents with rclpy'
title: '1.2 Python Agents with rclpy'
description: 'Learn how to create communication nodes in Python using rclpy and bridge AI agents to robot controllers.'
---

# 1.2 Python Agents with rclpy

## Introduction to rclpy and Python Agents

Welcome to the second chapter of our robotics module, where we'll explore how to create communication nodes in Python and bridge AI agents to robot controllers. This chapter will show you how to use the rclpy library, which is the Python client library for ROS 2, to implement nodes that can interact with robotic systems and intelligent agents.

rclpy provides a Python API for ROS 2, allowing you to create nodes that can publish and subscribe to topics, provide and call services, and interact with the ROS 2 ecosystem. This is particularly powerful for integrating AI algorithms, which are often implemented in Python, with robotic systems.

## Basic Node Structure with rclpy

### Setting Up Your First Node

The foundation of any ROS 2 Python application is a node. Here's the essential structure:

```python
import rclpy
from rclpy.node import Node

class RobotControllerNode(Node):
    def __init__(self):
        super().__init__('robot_controller_node')
        self.get_logger().info('Robot Controller Node initialized')

def main(args=None):
    rclpy.init(args=args)
    robot_controller_node = RobotControllerNode()

    try:
        rclpy.spin(robot_controller_node)
    except KeyboardInterrupt:
        pass
    finally:
        robot_controller_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

This structure provides:
- Proper initialization of the ROS 2 client library
- A node class that inherits from `rclpy.node.Node`
- Proper cleanup when the node is terminated
- Error handling for graceful shutdown

## Publisher Implementation

### Creating Publishers

Publishers are used to send messages to topics in a publish-subscribe pattern. Here's a comprehensive example:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
from geometry_msgs.msg import Twist

class SensorPublisherNode(Node):
    def __init__(self):
        super().__init__('sensor_publisher')

        # Create publishers for different message types
        self.sensor_pub = self.create_publisher(String, 'sensor_data', 10)
        self.distance_pub = self.create_publisher(Float32, 'distance', 10)
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)

        # Create a timer to publish data at regular intervals
        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.i = 0

    def timer_callback(self):
        # Publish sensor data
        msg = String()
        msg.data = f'Sensor reading: {self.i}'
        self.sensor_pub.publish(msg)

        # Publish distance measurement
        dist_msg = Float32()
        dist_msg.data = 1.5 + (self.i * 0.1)  # Simulated distance
        self.distance_pub.publish(dist_msg)

        self.get_logger().info(f'Published: "{msg.data}" and distance: {dist_msg.data}')
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    sensor_publisher = SensorPublisherNode()

    try:
        rclpy.spin(sensor_publisher)
    except KeyboardInterrupt:
        pass
    finally:
        sensor_publisher.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

Key aspects of publisher implementation:
- Use `create_publisher()` to create publishers
- Specify the message type, topic name, and queue size
- Publish messages using the `publish()` method
- Consider using timers for regular data publishing

## Subscriber Implementation

### Creating Subscribers

Subscribers receive messages from topics. Here's a comprehensive example:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist

class CommandSubscriberNode(Node):
    def __init__(self):
        super().__init__('command_subscriber')

        # Create subscribers for different topics
        self.cmd_sub = self.create_subscription(
            String,
            'robot_commands',
            self.command_callback,
            10)

        self.vel_sub = self.create_subscription(
            Twist,
            'cmd_vel',
            self.velocity_callback,
            10)

        # Store the latest command
        self.last_command = None

    def command_callback(self, msg):
        self.last_command = msg.data
        self.get_logger().info(f'Received command: "{msg.data}"')

        # Process the command
        self.process_command(msg.data)

    def velocity_callback(self, msg):
        self.get_logger().info(
            f'Received velocity: linear.x={msg.linear.x}, angular.z={msg.angular.z}'
        )

    def process_command(self, command):
        # Implement command processing logic here
        if command == 'start':
            self.get_logger().info('Starting robot operations')
        elif command == 'stop':
            self.get_logger().info('Stopping robot operations')
        # Add more command processing as needed

def main(args=None):
    rclpy.init(args=args)
    command_subscriber = CommandSubscriberNode()

    try:
        rclpy.spin(command_subscriber)
    except KeyboardInterrupt:
        pass
    finally:
        command_subscriber.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

Key aspects of subscriber implementation:
- Use `create_subscription()` to create subscribers
- Specify the message type, topic name, callback function, and queue size
- The callback function receives the message as a parameter
- Process received messages in the callback function

## Service Implementation

### Creating Services

Services provide synchronous request-response communication. Here's a comprehensive example:

```python
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts, Trigger
from std_srvs.srv import Empty

class RobotServiceNode(Node):
    def __init__(self):
        super().__init__('robot_service')

        # Create different types of services
        self.add_service = self.create_service(
            AddTwoInts,
            'add_two_ints',
            self.add_two_ints_callback
        )

        self.move_service = self.create_service(
            Trigger,
            'move_robot',
            self.move_robot_callback
        )

        self.reset_service = self.create_service(
            Empty,
            'reset_robot',
            self.reset_robot_callback
        )

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'Returning: {request.a} + {request.b} = {response.sum}')
        return response

    def move_robot_callback(self, request, response):
        # Simulate robot movement
        self.get_logger().info('Moving robot to requested position')
        response.success = True
        response.message = 'Robot moved successfully'
        return response

    def reset_robot_callback(self, request, response):
        # Reset robot state
        self.get_logger().info('Resetting robot to initial state')
        # Add actual reset logic here
        return response

def main(args=None):
    rclpy.init(args=args)
    robot_service = RobotServiceNode()

    try:
        rclpy.spin(robot_service)
    except KeyboardInterrupt:
        pass
    finally:
        robot_service.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

Key aspects of service implementation:
- Use `create_service()` to create services
- Specify the service type, service name, and callback function
- The callback receives both request and response objects
- Return the response object after processing

## AI Agent Integration Pattern

### Bridging AI Agents to Robot Controllers

One of the most powerful applications of ROS 2 with Python is bridging AI agents to robot controllers. Here's a comprehensive example:

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from std_msgs.msg import String
import numpy as np

class SimpleAIAgent:
    """A simple AI agent that makes decisions based on sensor input"""

    def __init__(self):
        self.state = "IDLE"

    def get_action(self, sensor_data):
        """Process sensor data and return appropriate action"""
        if sensor_data is None or len(sensor_data) == 0:
            return {"linear_velocity": 0.0, "angular_velocity": 0.0}

        # Find minimum distance in front of robot (forward 45 degrees each side)
        front_distances = sensor_data[len(sensor_data)//2-22:len(sensor_data)//2+23]
        min_distance = min(front_distances) if front_distances else float('inf')

        # Simple obstacle avoidance algorithm
        if min_distance < 1.0:  # Obstacle too close
            return {"linear_velocity": 0.0, "angular_velocity": 0.5}  # Turn right
        else:
            return {"linear_velocity": 0.5, "angular_velocity": 0.0}  # Move forward

class AIBridgeNode(Node):
    def __init__(self):
        super().__init__('ai_bridge_node')

        # Subscribers for sensor data
        self.laser_subscription = self.create_subscription(
            LaserScan,
            'laser_scan',
            self.laser_callback,
            10)

        # Publishers for robot commands
        self.cmd_publisher = self.create_publisher(Twist, 'cmd_vel', 10)

        # Publisher for AI status
        self.status_publisher = self.create_publisher(String, 'ai_status', 10)

        # Initialize AI agent
        self.ai_agent = SimpleAIAgent()

        # Store latest sensor data
        self.latest_sensor_data = None

        # Timer for AI decision making
        self.ai_timer = self.create_timer(0.1, self.ai_decision_callback)

    def laser_callback(self, msg):
        """Process laser scan data"""
        # Convert laser scan ranges to a list, ignoring invalid values
        self.latest_sensor_data = [
            distance if not (np.isnan(distance) or np.isinf(distance))
            else float('inf') for distance in msg.ranges
        ]

        self.get_logger().debug(f'Received laser scan with {len(msg.ranges)} points')

    def ai_decision_callback(self):
        """Make AI decisions based on sensor data"""
        if self.latest_sensor_data is None:
            return

        # Get action from AI agent
        action = self.ai_agent.get_action(self.latest_sensor_data)

        # Create and publish robot command
        cmd_msg = Twist()
        cmd_msg.linear.x = action["linear_velocity"]
        cmd_msg.angular.z = action["angular_velocity"]

        self.cmd_publisher.publish(cmd_msg)

        # Publish AI status
        status_msg = String()
        status_msg.data = f'AI: v={action["linear_velocity"]:.2f}, w={action["angular_velocity"]:.2f}'
        self.status_publisher.publish(status_msg)

        self.get_logger().info(f'AI Command: linear={cmd_msg.linear.x:.2f}, angular={cmd_msg.angular.z:.2f}')

def main(args=None):
    rclpy.init(args=args)
    ai_bridge_node = AIBridgeNode()

    try:
        rclpy.spin(ai_bridge_node)
    except KeyboardInterrupt:
        pass
    finally:
        ai_bridge_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

This example demonstrates:
- Integration of an AI agent with ROS 2
- Processing of sensor data for AI decision making
- Publishing of robot commands based on AI decisions
- Proper separation of concerns between ROS 2 communication and AI logic

## Best Practices and Summary

### Best Practices for Python ROS 2 Development

1. **Error Handling**: Always implement proper error handling in your nodes
```python
def safe_publisher(self, data):
    try:
        msg = self.create_message(data)
        self.publisher.publish(msg)
    except Exception as e:
        self.get_logger().error(f'Error publishing message: {e}')
```

2. **Resource Management**: Properly manage resources and clean up when the node is destroyed
```python
def destroy_node(self):
    # Clean up timers and other resources
    if hasattr(self, 'timer') and self.timer:
        self.timer.destroy()
    super().destroy_node()
```

3. **Parameter Configuration**: Use ROS 2 parameters for configurable behavior
```python
self.declare_parameter('publish_rate', 10)
rate = self.get_parameter('publish_rate').value
```

### Summary and Learning Objectives

After completing this chapter, you should understand:
- How to create ROS 2 nodes in Python using rclpy
- How to implement publishers, subscribers, and services
- How to bridge AI agents to robot controllers
- Best practices for Python-based ROS 2 development
- How to structure code for maintainable robotic applications

These skills form the foundation for creating intelligent robotic systems that can integrate AI algorithms with physical robot control, enabling sophisticated autonomous behaviors.