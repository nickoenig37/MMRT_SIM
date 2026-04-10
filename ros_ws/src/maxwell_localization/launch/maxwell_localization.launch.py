#!/usr/bin/env python3
"""Maxwell Localization Launch

This launch composes:
- maxwell_gazebo/maxwell_sim.launch.py (Gazebo + rover + drive stack)
- wheel odometry estimator from simulated joints
- robot_localization EKF local (odom->base)
- robot_localization EKF global (map->odom), corrected by ORB-SLAM3 pose
- depthimage_to_laserscan to convert the simulated depth camera into a LaserScan for Nav2
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_maxwell_gazebo = get_package_share_directory('maxwell_gazebo')
    pkg_maxwell_localization = get_package_share_directory('maxwell_localization')

    sim_launch = os.path.join(pkg_maxwell_gazebo, 'launch', 'maxwell_sim.launch.py')
    ekf_config = os.path.join(pkg_maxwell_localization, 'config', 'ekf_localization.yaml')
    rviz_config = os.path.join(pkg_maxwell_localization, 'config', 'maxwell_localization_rviz2.rviz')

    use_sim_time = LaunchConfiguration('use_sim_time')
    world = LaunchConfiguration('world')
    x_pose = LaunchConfiguration('x_pose')
    y_pose = LaunchConfiguration('y_pose')
    z_pose = LaunchConfiguration('z_pose')
    drive_mode = LaunchConfiguration('drive_mode')
    run_rviz = LaunchConfiguration('run_rviz')
    slam = LaunchConfiguration('slam')

    declare_args = [
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('world', default_value='marsyard2020'),
        DeclareLaunchArgument('x_pose', default_value='0.0'),
        DeclareLaunchArgument('y_pose', default_value='0.0'),
        DeclareLaunchArgument('z_pose', default_value='2.5'),
        DeclareLaunchArgument('drive_mode', default_value='SWERVE_DRIVE'),
        DeclareLaunchArgument('slam', default_value='false', description='If true, disable global EKF map->odom TF to avoid conflict with SLAM toolbox'),
        DeclareLaunchArgument('rviz_config', default_value=rviz_config, description='Absolute path to RViz config file'),
        DeclareLaunchArgument('run_rviz', default_value='true', description='Launch RViz visualization'),
    ]

    # Launch Maxwell Gazebo simulation
    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(sim_launch),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'world': world,
            'x_pose': x_pose,
            'y_pose': y_pose,
            'z_pose': z_pose,
            'drive_mode': drive_mode,
            'rviz_config': LaunchConfiguration('rviz_config'),
            'run_rviz': run_rviz,
        }.items(),
    )

    # Wheel odometry estimator
    wheel_odometry = Node(
        package='maxwell_localization',
        executable='wheel_odometry',
        name='wheel_odometry',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )

    # EKF local filter (odom frame)
    ekf_odom = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_odom',
        output='screen',
        parameters=[ekf_config, {'use_sim_time': use_sim_time}],
        remappings=[('odometry/filtered', '/odometry/local')],
    )

    # Bridge ORB-SLAM3 PoseStamped -> PoseWithCovarianceStamped for robot_localization
    slam_pose_bridge = Node(
        package='maxwell_localization',
        executable='slam_pose_bridge',
        name='slam_pose_bridge',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )

    # EKF global filter (map frame)
    ekf_map = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_map',
        output='screen',
        parameters=[ekf_config, {'use_sim_time': use_sim_time}],
        remappings=[('odometry/filtered', '/odometry/global')],
    )

    # Depth camera -> LaserScan for Nav2 obstacle layers
    depth_to_scan = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='depthimage_to_laserscan',
                executable='depthimage_to_laserscan_node',
                name='depth_to_scan',
                output='screen',
                respawn=True,
                respawn_delay=2.0,
                parameters=[{
                    'use_sim_time': use_sim_time,
                    'output_frame': 'camera_depth_frame',
                    'scan_time': 0.033,
                    'range_min': 0.2,
                    'range_max': 8.0,
                    'scan_height': 5,
                }],
                remappings=[
                    ('depth', '/camera/depth/image_raw'),
                    ('depth_camera_info', '/camera/depth/camera_info'),
                    ('scan', '/camera/depth/scan'),
                ],
            )
        ]
    )

    ld = LaunchDescription()
    for action in declare_args:
        ld.add_action(action)

    ld.add_action(sim)
    ld.add_action(wheel_odometry)
    ld.add_action(ekf_odom)
    ld.add_action(slam_pose_bridge)
    ld.add_action(ekf_map)
    ld.add_action(depth_to_scan)

    return ld
