#!/usr/bin/env python3
"""Bring up Maxwell simulation with autonomy-focused localization + obstacle pipeline.

This launch composes:
- maxwell_gazebo/maxwell_sim.launch.py (Gazebo + rover + drive stack)
- wheel odometry estimator from simulated joints
- robot_localization EKF local (odom->base)
- robot_localization EKF global (map->odom), corrected by ORB-SLAM3 pose
- depthimage_to_laserscan for dense obstacle sensing from the raw depth stream
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_maxwell_gazebo = get_package_share_directory('maxwell_gazebo')

    sim_launch = os.path.join(pkg_maxwell_gazebo, 'launch', 'maxwell_sim.launch.py')
    ekf_config = os.path.join(pkg_maxwell_gazebo, 'config', 'ekf_localization.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    world = LaunchConfiguration('world')
    x_pose = LaunchConfiguration('x_pose')
    y_pose = LaunchConfiguration('y_pose')
    z_pose = LaunchConfiguration('z_pose')
    drive_mode = LaunchConfiguration('drive_mode')

    run_localization = LaunchConfiguration('run_localization')
    run_depth_to_scan = LaunchConfiguration('run_depth_to_scan')

    declare_args = [
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('world', default_value='marsyard2020'),
        DeclareLaunchArgument('x_pose', default_value='0.0'),
        DeclareLaunchArgument('y_pose', default_value='0.0'),
        DeclareLaunchArgument('z_pose', default_value='2.5'),
        DeclareLaunchArgument('drive_mode', default_value='SWERVE_DRIVE'),
        DeclareLaunchArgument('run_localization', default_value='true'),
        DeclareLaunchArgument('run_depth_to_scan', default_value='true'),
    ]

    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(sim_launch),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'world': world,
            'x_pose': x_pose,
            'y_pose': y_pose,
            'z_pose': z_pose,
            'drive_mode': drive_mode,
        }.items(),
    )

    wheel_odometry = Node(
        package='maxwell_gazebo',
        executable='wheel_odometry',
        name='wheel_odometry',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(run_localization),
    )

    ekf_odom = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_odom',
        output='screen',
        parameters=[ekf_config, {'use_sim_time': use_sim_time}],
        remappings=[('odometry/filtered', '/odometry/local')],
        condition=IfCondition(run_localization),
    )

    ekf_map = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_map',
        output='screen',
        parameters=[ekf_config, {'use_sim_time': use_sim_time}],
        remappings=[('odometry/filtered', '/odometry/global')],
        condition=IfCondition(run_localization),
    )

    depth_to_scan = Node(
        package='depthimage_to_laserscan',
        executable='depthimage_to_laserscan_node',
        name='depth_to_scan',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'output_frame': 'camera_depth_frame',
            'scan_time': 0.033,
            'range_min': 0.2,
            'range_max': 8.0,
            'scan_height': 20,
        }],
        remappings=[
            ('depth', '/camera/depth/image_raw'),
            ('depth_camera_info', '/camera/depth/camera_info'),
            ('scan', '/camera/depth/scan'),
        ],
        condition=IfCondition(run_depth_to_scan),
    )

    ld = LaunchDescription()
    for action in declare_args:
        ld.add_action(action)

    ld.add_action(sim)
    ld.add_action(wheel_odometry)
    ld.add_action(ekf_odom)
    ld.add_action(ekf_map)
    ld.add_action(depth_to_scan)

    return ld
