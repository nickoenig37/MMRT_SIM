#!/usr/bin/env python3
"""Wheel odometry estimator for Maxwell swerve simulation.

This node converts simulated wheel/steering joint states into:
1) `/drive/drive_modules` (`custom_interfaces/SwerveModulesList`) so existing drive stack
   can keep working in simulation.
2) `/wheel/odometry` (`nav_msgs/Odometry`) for robot_localization EKF fusion.
"""

import math
from typing import Dict, Optional, Sequence, Tuple

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Quaternion
from custom_interfaces.msg import SwerveModule, SwerveModulesList  # type: ignore


class WheelOdometry(Node):
    def __init__(self) -> None:
        super().__init__('wheel_odometry')

        self.declare_parameter('wheel_radius', 0.127)
        self.declare_parameter('base_frame', 'base_footprint')
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('module_length', 1.0)
        self.declare_parameter('module_width', 0.625)

        self.wheel_radius = self.get_parameter('wheel_radius').get_parameter_value().double_value
        self.base_frame = self.get_parameter('base_frame').get_parameter_value().string_value
        self.odom_frame = self.get_parameter('odom_frame').get_parameter_value().string_value
        length = self.get_parameter('module_length').get_parameter_value().double_value
        width = self.get_parameter('module_width').get_parameter_value().double_value

        # (x, y) positions of wheel modules in body frame.
        self.module_positions = {
            'front_left': (-length / 2.0, width / 2.0),
            'front_right': (length / 2.0, width / 2.0),
            'rear_left': (-length / 2.0, -width / 2.0),
            'rear_right': (length / 2.0, -width / 2.0),
        }

        self.steer_joint_names = {
            'front_left': 'FL_Rot_Joint',
            'front_right': 'FR_Rot_Joint',
            'rear_left': 'BL_Rot_Joint',
            'rear_right': 'BR_Rot_Joint',
        }

        self.drive_joint_names = {
            'front_left': 'FL_Joint',
            'front_right': 'FR_Joint',
            'rear_left': 'BL_Joint',
            'rear_right': 'BR_Joint',
        }

        self.pub_modules = self.create_publisher(SwerveModulesList, '/drive/drive_modules', 20)
        self.pub_odom = self.create_publisher(Odometry, '/wheel/odometry', 20)

        self.create_subscription(JointState, '/joint_states', self.joint_state_cb, 20)

        self.get_logger().info('Wheel odometry node started')

    @staticmethod
    def yaw_to_quaternion(yaw: float) -> Quaternion:
        q = Quaternion()
        q.z = math.sin(yaw / 2.0)
        q.w = math.cos(yaw / 2.0)
        return q

    def extract_module_state(
        self,
        joint_index: Dict[str, int],
        position: Sequence[float],
        velocity: Sequence[float],
        module_key: str,
    ) -> Optional[Tuple[float, float]]:
        steer_name = self.steer_joint_names[module_key]
        drive_name = self.drive_joint_names[module_key]

        if steer_name not in joint_index or drive_name not in joint_index:
            return None

        steer_i = joint_index[steer_name]
        drive_i = joint_index[drive_name]

        if steer_i >= len(position) or drive_i >= len(velocity):
            return None

        angle_rad = position[steer_i]
        wheel_ang_vel = velocity[drive_i]
        wheel_lin_vel = wheel_ang_vel * self.wheel_radius

        return angle_rad, wheel_lin_vel

    def joint_state_cb(self, msg: JointState) -> None:
        if not msg.name:
            return

        joint_index = {name: i for i, name in enumerate(msg.name)}

        module_states: Dict[str, Tuple[float, float]] = {}
        for module in self.module_positions.keys():
            state = self.extract_module_state(joint_index, msg.position, msg.velocity, module)
            if state is None:
                return
            module_states[module] = state

        modules_msg = SwerveModulesList()

        fl = SwerveModule()
        fl.speed = module_states['front_left'][1]
        fl.angle = math.degrees(module_states['front_left'][0])
        modules_msg.front_left = fl

        fr = SwerveModule()
        fr.speed = module_states['front_right'][1]
        fr.angle = math.degrees(module_states['front_right'][0])
        modules_msg.front_right = fr

        rl = SwerveModule()
        rl.speed = module_states['rear_left'][1]
        rl.angle = math.degrees(module_states['rear_left'][0])
        modules_msg.rear_left = rl

        rr = SwerveModule()
        rr.speed = module_states['rear_right'][1]
        rr.angle = math.degrees(module_states['rear_right'][0])
        modules_msg.rear_right = rr

        self.pub_modules.publish(modules_msg)

        # Convert per-wheel speeds to body-frame velocity estimate.
        wheel_vectors = {}
        for name, (angle, speed) in module_states.items():
            wheel_vectors[name] = (speed * math.cos(angle), speed * math.sin(angle))

        vx = sum(v[0] for v in wheel_vectors.values()) / 4.0
        vy = sum(v[1] for v in wheel_vectors.values()) / 4.0

        omega_samples = []
        for name, (vx_i, vy_i) in wheel_vectors.items():
            x_i, y_i = self.module_positions[name]
            if abs(y_i) > 1e-6:
                omega_samples.append((vx - vx_i) / (-y_i))
            if abs(x_i) > 1e-6:
                omega_samples.append((vy_i - vy) / x_i)

        omega = sum(omega_samples) / len(omega_samples) if omega_samples else 0.0

        odom = Odometry()
        odom.header.stamp = msg.header.stamp if msg.header.stamp.sec != 0 or msg.header.stamp.nanosec != 0 else self.get_clock().now().to_msg()
        odom.header.frame_id = self.odom_frame
        odom.child_frame_id = self.base_frame

        odom.pose.pose.orientation = self.yaw_to_quaternion(0.0)

        # Mark pose as very uncertain; this is a velocity-focused wheel odom source.
        odom.pose.covariance[0] = 1e6
        odom.pose.covariance[7] = 1e6
        odom.pose.covariance[14] = 1e6
        odom.pose.covariance[21] = 1e6
        odom.pose.covariance[28] = 1e6
        odom.pose.covariance[35] = 1e6

        odom.twist.twist.linear.x = vx
        odom.twist.twist.linear.y = vy
        odom.twist.twist.angular.z = omega

        odom.twist.covariance[0] = 0.08
        odom.twist.covariance[7] = 0.08
        odom.twist.covariance[14] = 1e6
        odom.twist.covariance[21] = 1e6
        odom.twist.covariance[28] = 1e6
        odom.twist.covariance[35] = 0.15

        self.pub_odom.publish(odom)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = WheelOdometry()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
