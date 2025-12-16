#!/usr/bin/env python3
"""
Maxwell Rover Gazebo Simulation Launch File

This launch file starts:
1. Gazebo with the Maxwell rover model
2. Robot state publisher
3. ROS2 control controllers for swerve drive
4. Drive controller for velocity command processing
5. Swerve simulation bridge to connect drive commands to Gazebo
6. Joint state publisher
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, SetEnvironmentVariable, RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Get package directories
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_maxwell_gazebo = get_package_share_directory('maxwell_gazebo')
    pkg_maxwell_description = get_package_share_directory('maxwell_description')
    
    # Define file paths
    world_launch_file = os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
    urdf_file_path = os.path.join(pkg_maxwell_gazebo, 'urdf', 'maxwell_swerve.urdf')
    controllers_yaml = os.path.join(pkg_maxwell_gazebo, 'config', 'swerve_controllers.yaml')
    
    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')
    z_pose = LaunchConfiguration('z_pose', default='0.3')
    drive_mode = LaunchConfiguration('drive_mode', default='SWERVE_DRIVE')
    
    # Declare launch arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )
    
    declare_x_position_cmd = DeclareLaunchArgument(
        'x_pose',
        default_value='0.0',
        description='X position to spawn the robot'
    )
    
    declare_y_position_cmd = DeclareLaunchArgument(
        'y_pose',
        default_value='0.0',
        description='Y position to spawn the robot'
    )
    
    declare_z_position_cmd = DeclareLaunchArgument(
        'z_pose',
        default_value='0.3',
        description='Z position to spawn the robot (height above ground)'
    )
    
    declare_drive_mode_cmd = DeclareLaunchArgument(
        'drive_mode',
        default_value='SWERVE_DRIVE',
        description='Drive mode: SWERVE_DRIVE or TANK_STEER_HYBRID'
    )
    
    # Set GAZEBO_MODEL_PATH
    set_gazebo_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=os.path.join(pkg_maxwell_description, '..')
    )
    
    # Start Gazebo
    start_gazebo_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(world_launch_file),
        launch_arguments={
            'verbose': 'false',
            'pause': 'false'
        }.items()
    )
    
    # Read URDF file
    with open(urdf_file_path, 'r') as urdf_file:
        robot_description_content = urdf_file.read()
    
    # Replace controller file path placeholder
    robot_description_content = robot_description_content.replace(
        'CONTROLLERS_FILE_PATH',
        controllers_yaml
    )
    
    # Robot State Publisher
    robot_state_publisher_cmd = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': robot_description_content
        }]
    )
    
    # Spawn the robot in Gazebo
    spawn_entity_cmd = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_maxwell_rover',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'maxwell_rover',
            '-x', x_pose,
            '-y', y_pose,
            '-z', z_pose
        ],
        output='screen'
    )
    
    # Joint State Broadcaster
    load_joint_state_broadcaster_cmd = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    # Load steering position controllers
    load_fl_steer_controller_cmd = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['fl_steer_position_controller', '--controller-manager', '/controller_manager'],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    load_fr_steer_controller_cmd = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['fr_steer_position_controller', '--controller-manager', '/controller_manager'],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    load_bl_steer_controller_cmd = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['bl_steer_position_controller', '--controller-manager', '/controller_manager'],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    load_br_steer_controller_cmd = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['br_steer_position_controller', '--controller-manager', '/controller_manager'],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    # Load drive velocity controllers
    load_fl_drive_controller_cmd = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['fl_drive_velocity_controller', '--controller-manager', '/controller_manager'],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    load_fr_drive_controller_cmd = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['fr_drive_velocity_controller', '--controller-manager', '/controller_manager'],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    load_bl_drive_controller_cmd = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['bl_drive_velocity_controller', '--controller-manager', '/controller_manager'],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    load_br_drive_controller_cmd = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['br_drive_velocity_controller', '--controller-manager', '/controller_manager'],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    # Launch drive controller (at 7s to ensure controllers are loaded)
    drive_controller_cmd = Node(
        package='drive',
        executable='drive_controller.py',
        name='drive_controller',
        output='screen'
    )
    
    # Launch heartbeat (at 7s)
    heartbeat_cmd = Node(
        package='drive',
        executable='heartbeat.py',
        name='heartbeat',
        output='screen'
    )
    
    # Swerve Simulation Bridge
    swerve_sim_bridge_cmd = Node(
        package='maxwell_gazebo',
        executable='swerve_sim_bridge',
        name='swerve_sim_bridge',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    # Create the launch description
    ld = LaunchDescription()
    
    # Environment and arguments
    ld.add_action(set_gazebo_model_path)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_x_position_cmd)
    ld.add_action(declare_y_position_cmd)
    ld.add_action(declare_z_position_cmd)
    ld.add_action(declare_drive_mode_cmd)
    
    # Start Gazebo and spawn robot
    ld.add_action(start_gazebo_cmd)
    ld.add_action(robot_state_publisher_cmd)
    ld.add_action(spawn_entity_cmd)
    
    # Load controllers after robot is spawned (with delay)
    ld.add_action(TimerAction(
        period=5.0,
        actions=[load_joint_state_broadcaster_cmd]
    ))
    
    ld.add_action(TimerAction(
        period=6.0,
        actions=[
            load_fl_steer_controller_cmd,
            load_fr_steer_controller_cmd,
            load_bl_steer_controller_cmd,
            load_br_steer_controller_cmd,
            load_fl_drive_controller_cmd,
            load_fr_drive_controller_cmd,
            load_bl_drive_controller_cmd,
            load_br_drive_controller_cmd
        ]
    ))
    
    # Start drive system (with delay)
    ld.add_action(TimerAction(
        period=7.0,
        actions=[
            drive_controller_cmd,
            heartbeat_cmd,
            swerve_sim_bridge_cmd
        ]
    ))
    
    return ld
