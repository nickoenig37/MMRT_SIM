#!/usr/bin/env python3
"""Maxwell Navigation Launch

This launch composes:
- maxwell_localization/maxwell_localization.launch.py (Gazebo + localization)
- Nav2 navigation stack for autonomous path planning and control
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_maxwell_localization = get_package_share_directory('maxwell_localization')
    pkg_maxwell_navigation = get_package_share_directory('maxwell_navigation')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    localization_launch = os.path.join(pkg_maxwell_localization, 'launch', 'maxwell_localization.launch.py')
    nav2_params = os.path.join(pkg_maxwell_navigation, 'config', 'nav2_params.yaml')
    default_map = os.path.join(pkg_nav2_bringup, 'maps', 'turtlebot3_world.yaml')
    rviz_config = os.path.join(pkg_maxwell_navigation, 'config', 'maxwell_navigation_rviz2.rviz')

    use_sim_time = LaunchConfiguration('use_sim_time')
    slam = LaunchConfiguration('slam')
    map_file = LaunchConfiguration('map')
    world = LaunchConfiguration('world')
    x_pose = LaunchConfiguration('x_pose')
    y_pose = LaunchConfiguration('y_pose')
    z_pose = LaunchConfiguration('z_pose')
    drive_mode = LaunchConfiguration('drive_mode')
    run_rviz = LaunchConfiguration('run_rviz')

    declare_args = [
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('slam', default_value='True', description='Run SLAM instead of map-based localization'),
        DeclareLaunchArgument('map', default_value=default_map, description='Full path to map yaml file to load'),
        DeclareLaunchArgument('world', default_value='marsyard2020'),
        DeclareLaunchArgument('x_pose', default_value='0.0'),
        DeclareLaunchArgument('y_pose', default_value='0.0'),
        DeclareLaunchArgument('z_pose', default_value='2.5'),
        DeclareLaunchArgument('drive_mode', default_value='SWERVE_DRIVE'),
        DeclareLaunchArgument('rviz_config', default_value=rviz_config, description='Absolute path to RViz config file'),
        DeclareLaunchArgument('run_rviz', default_value='true', description='Launch RViz visualization'),
    ]

    # Launch Maxwell Localization (which includes Gazebo simulation)
    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(localization_launch),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'world': world,
            'x_pose': x_pose,
            'y_pose': y_pose,
            'z_pose': z_pose,
            'drive_mode': drive_mode,
            'slam': slam,
            'rviz_config': LaunchConfiguration('rviz_config'),
            'run_rviz': run_rviz,
        }.items(),
    )

    # Launch Nav2 Bringup Stack
    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'slam': slam,
            'map': map_file,
            'use_sim_time': use_sim_time,
            'params_file': nav2_params,
            'use_composition': 'True',
        }.items(),
    )

    ld = LaunchDescription()
    for action in declare_args:
        ld.add_action(action)

    ld.add_action(localization)
    ld.add_action(nav2_bringup)

    return ld
