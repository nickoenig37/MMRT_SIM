#!/usr/bin/env python3

import rclpy
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from rclpy.node import Node


class SlamPoseBridge(Node):
    def __init__(self) -> None:
        super().__init__('slam_pose_bridge')

        self.declare_parameter('input_topic', '/robot/robot_pose_slam')
        self.declare_parameter('output_topic', '/robot/robot_pose_slam_cov')
        self.declare_parameter('xy_variance', 0.05)
        self.declare_parameter('yaw_variance', 0.1)

        input_topic = self.get_parameter('input_topic').get_parameter_value().string_value
        output_topic = self.get_parameter('output_topic').get_parameter_value().string_value
        self._xy_var = self.get_parameter('xy_variance').get_parameter_value().double_value
        self._yaw_var = self.get_parameter('yaw_variance').get_parameter_value().double_value

        self._pub = self.create_publisher(PoseWithCovarianceStamped, output_topic, 10)
        self._sub = self.create_subscription(PoseStamped, input_topic, self._pose_cb, 10)

        self.get_logger().info(f'Bridging {input_topic} (PoseStamped) -> {output_topic} (PoseWithCovarianceStamped)')

    def _pose_cb(self, msg: PoseStamped) -> None:
        out = PoseWithCovarianceStamped()
        out.header = msg.header
        out.pose.pose = msg.pose

        cov = [0.0] * 36
        cov[0] = self._xy_var      # x
        cov[7] = self._xy_var      # y
        cov[14] = 1e6              # z (unused in 2D)
        cov[21] = 1e6              # roll
        cov[28] = 1e6              # pitch
        cov[35] = self._yaw_var    # yaw
        out.pose.covariance = cov

        self._pub.publish(out)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = SlamPoseBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
