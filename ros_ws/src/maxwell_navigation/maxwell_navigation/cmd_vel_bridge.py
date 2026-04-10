#!/usr/bin/env python3

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class CmdVelBridge(Node):
    def __init__(self) -> None:
        super().__init__('cmd_vel_bridge')

        self.declare_parameter('input_topic', '/cmd_vel')
        self.declare_parameter('output_topic', '/drive/cmd_vel')

        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value

        self._publisher = self.create_publisher(Twist, output_topic, 10)
        self._subscriber = self.create_subscription(Twist, input_topic, self._callback, 10)

        self.get_logger().info(f'Bridging {input_topic} -> {output_topic}')

    def _callback(self, message: Twist) -> None:
        self._publisher.publish(message)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = CmdVelBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
