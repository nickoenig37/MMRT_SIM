#!/usr/bin/env python3
"""
Swerve Simulation Bridge Node

This node bridges between the drive controller's SwerveModulesList messages
and Gazebo's joint position/velocity controllers for swerve drive simulation.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from sensor_msgs.msg import JointState
from custom_interfaces.msg import SwerveModulesList
import math


class SwerveSimBridge(Node):
    """
    Converts SwerveModulesList commands to individual joint commands for Gazebo.
    
    Subscribes to:
        /drive/modules_command (SwerveModulesList) - Swerve module commands from drive controller
        
    Publishes to:
        /fl_steer_position_controller/commands (Float64MultiArray) - FL steering angle
        /fr_steer_position_controller/commands (Float64MultiArray) - FR steering angle
        /bl_steer_position_controller/commands (Float64MultiArray) - BL steering angle
        /br_steer_position_controller/commands (Float64MultiArray) - BR steering angle
        /fl_drive_velocity_controller/commands (Float64MultiArray) - FL wheel velocity
        /fr_drive_velocity_controller/commands (Float64MultiArray) - FR wheel velocity
        /bl_drive_velocity_controller/commands (Float64MultiArray) - BL wheel velocity
        /br_drive_velocity_controller/commands (Float64MultiArray) - BR wheel velocity
    """
    
    def __init__(self):
        super().__init__('swerve_sim_bridge')
        
        # Wheel radius for velocity conversion (meters)
        self.wheel_radius = 0.127  # 5 inch radius = 0.127m
        
        # Subscribe to swerve module commands
        self.subscription = self.create_subscription(
            SwerveModulesList,
            '/drive/modules_command',
            self.modules_command_callback,
            10
        )
        
        # Publishers for steering (position control)
        self.fl_steer_pub = self.create_publisher(Float64MultiArray, '/fl_steer_position_controller/commands', 10)
        self.fr_steer_pub = self.create_publisher(Float64MultiArray, '/fr_steer_position_controller/commands', 10)
        self.bl_steer_pub = self.create_publisher(Float64MultiArray, '/bl_steer_position_controller/commands', 10)
        self.br_steer_pub = self.create_publisher(Float64MultiArray, '/br_steer_position_controller/commands', 10)
        
        # Publishers for drive wheels (velocity control)
        self.fl_drive_pub = self.create_publisher(Float64MultiArray, '/fl_drive_velocity_controller/commands', 10)
        self.fr_drive_pub = self.create_publisher(Float64MultiArray, '/fr_drive_velocity_controller/commands', 10)
        self.bl_drive_pub = self.create_publisher(Float64MultiArray, '/bl_drive_velocity_controller/commands', 10)
        self.br_drive_pub = self.create_publisher(Float64MultiArray, '/br_drive_velocity_controller/commands', 10)
        
        self.get_logger().info('Swerve Simulation Bridge started')
    
    def modules_command_callback(self, msg: SwerveModulesList):
        """
        Convert SwerveModulesList to individual joint commands.
        
        Args:
            msg: SwerveModulesList with angle (degrees) and speed (m/s) for each module
        """
        # Convert angles from degrees to radians
        fl_angle = math.radians(msg.front_left.angle)
        fr_angle = math.radians(msg.front_right.angle)
        bl_angle = math.radians(msg.rear_left.angle)
        br_angle = math.radians(msg.rear_right.angle)
        
        # Convert linear speed to angular velocity (rad/s)
        # angular_velocity = linear_velocity / radius
        fl_velocity = msg.front_left.speed / self.wheel_radius
        fr_velocity = msg.front_right.speed / self.wheel_radius
        bl_velocity = msg.rear_left.speed / self.wheel_radius
        br_velocity = msg.rear_right.speed / self.wheel_radius
        
        # Publish steering angles (position control)
        self.fl_steer_pub.publish(Float64MultiArray(data=[fl_angle]))
        self.fr_steer_pub.publish(Float64MultiArray(data=[fr_angle]))
        self.bl_steer_pub.publish(Float64MultiArray(data=[bl_angle]))
        self.br_steer_pub.publish(Float64MultiArray(data=[br_angle]))
        
        # Publish wheel velocities (velocity control)
        self.fl_drive_pub.publish(Float64MultiArray(data=[fl_velocity]))
        self.fr_drive_pub.publish(Float64MultiArray(data=[fr_velocity]))
        self.bl_drive_pub.publish(Float64MultiArray(data=[bl_velocity]))
        self.br_drive_pub.publish(Float64MultiArray(data=[br_velocity]))


def main(args=None):
    rclpy.init(args=args)
    node = SwerveSimBridge()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
