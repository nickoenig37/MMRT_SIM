# Technical Guide: Integrating Swerve Drive Robots in Gazebo with ROS2 Control

This document outlines the critical steps and requirements for creating a working Gazebo simulation of a swerve drive robot using ROS2 Control framework.

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Critical Components](#critical-components)
4. [Step-by-Step Integration](#step-by-step-integration)
5. [Common Pitfalls](#common-pitfalls)
6. [Debugging Checklist](#debugging-checklist)

---

## Overview

**Goal:** Simulate a 4-wheel swerve drive robot in Gazebo with full omnidirectional control.

**Key Insight:** Swerve drive requires coordinating 8 independent joints (4 steering + 4 drive wheels). Each joint needs its own controller, and commands must be synchronized.

**Architecture:**
```
Twist Commands → Drive Controller → Swerve Modules → Bridge Node → Individual Joint Controllers → Gazebo
```

---

## Prerequisites

### Required Packages
```bash
# ROS2 Control
sudo apt install ros-humble-ros2-control
sudo apt install ros-humble-ros2-controllers
sudo apt install ros-humble-gazebo-ros2-control

# Specific controllers
sudo apt install ros-humble-forward-command-controller
sudo apt install ros-humble-joint-state-broadcaster

# Gazebo
sudo apt install ros-humble-gazebo-ros-pkgs
```

### Required Knowledge
- URDF/Xacro syntax
- ROS2 launch files (Python)
- Joint types (revolute, continuous)
- Basic understanding of ros2_control hardware interfaces

---

## Critical Components

### 1. URDF with ros2_control

Your URDF must include:

#### A. Joint Definitions
```xml
<!-- Example: Front-Left Steering Joint -->
<joint name="FL_Rot_Joint" type="revolute">
  <parent link="Base_link"/>
  <child link="FL_Rot_Link"/>
  <origin xyz="0.275 0.25 0" rpy="0 0 0"/>
  <axis xyz="0 0 1"/>
  <limit lower="-2.094" upper="2.094" effort="100" velocity="10"/>
</joint>

<!-- Example: Front-Left Drive Joint -->
<joint name="FL_Joint" type="continuous">
  <parent link="FL_Rot_Link"/>
  <child link="FL_Link"/>
  <origin xyz="0 0 -0.05" rpy="0 0 0"/>
  <axis xyz="0 1 0"/>
</joint>
```

**Key Points:**
- Steering joints: `type="revolute"` with limits (typically ±120°)
- Drive joints: `type="continuous"` for unlimited rotation
- Accurate `origin` positioning is critical for kinematics

#### B. Gazebo Properties
```xml
<gazebo reference="FL_Link">
  <material>Gazebo/Black</material>
  <mu1>1.0</mu1>  <!-- Friction coefficient -->
  <mu2>1.0</mu2>
  <kp>1000000.0</kp>  <!-- Stiffness -->
  <kd>100.0</kd>      <!-- Damping -->
</gazebo>
```

**Key Points:**
- `mu1` and `mu2`: Friction must be high enough to prevent slipping
- `kp` and `kd`: Tune for realistic wheel contact

#### C. Gazebo ros2_control Plugin
```xml
<gazebo>
  <plugin name="gazebo_ros2_control" filename="libgazebo_ros2_control.so">
    <parameters>/absolute/path/to/controllers.yaml</parameters>
  </plugin>
</gazebo>
```

**CRITICAL:** 
- Path must be absolute (use launch file substitution)
- Example substitution in launch file:
  ```python
  controllers_yaml = os.path.join(pkg_share, 'config', 'controllers.yaml')
  robot_description = urdf_content.replace('CONTROLLERS_FILE_PATH', controllers_yaml)
  ```

#### D. ros2_control Hardware Interface
```xml
<ros2_control name="GazeboSystem" type="system">
  <hardware>
    <plugin>gazebo_ros2_control/GazeboSystem</plugin>
  </hardware>

  <!-- Steering Joint (Position Control) -->
  <joint name="FL_Rot_Joint">
    <command_interface name="position">
      <param name="min">-2.094</param>
      <param name="max">2.094</param>
    </command_interface>
    <state_interface name="position"/>
    <state_interface name="velocity"/>
  </joint>

  <!-- Drive Joint (Velocity Control) -->
  <joint name="FL_Joint">
    <command_interface name="velocity"/>
    <state_interface name="position"/>
    <state_interface name="velocity"/>
  </joint>
</ros2_control>
```

**Key Points:**
- Steering joints: `command_interface name="position"`
- Drive joints: `command_interface name="velocity"`
- Always include both position and velocity as state interfaces

---

### 2. Controller Configuration (YAML)

**File:** `config/swerve_controllers.yaml`

```yaml
controller_manager:
  ros__parameters:
    update_rate: 100  # Hz

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    # Steering controllers (position)
    fl_steer_position_controller:
      type: forward_command_controller/ForwardCommandController
    
    # Drive controllers (velocity)
    fl_drive_velocity_controller:
      type: forward_command_controller/ForwardCommandController

# Individual controller parameters
fl_steer_position_controller:
  ros__parameters:
    joints:
      - FL_Rot_Joint
    interface_name: position

fl_drive_velocity_controller:
  ros__parameters:
    joints:
      - FL_Joint
    interface_name: velocity
```

**CRITICAL POINTS:**

1. **Controller Type:** Use `forward_command_controller/ForwardCommandController`
   - NOT `position_controllers/JointPositionController` (doesn't exist in Humble)
   - NOT `velocity_controllers/JointVelocityController` (doesn't exist in Humble)

2. **Parameter Format:**
   - `joints:` (PLURAL, array format) not `joint:`
   - `interface_name:` must be either `position` or `velocity`

3. **Topic Names:**
   - ForwardCommandController subscribes to `/controller_name/commands` (PLURAL)
   - Message type: `std_msgs/msg/Float64MultiArray` (not Float64!)

---

### 3. Bridge Node

You need a bridge to convert high-level swerve commands to individual joint commands.

**Example:** `swerve_sim_bridge.py`

```python
from std_msgs.msg import Float64MultiArray
from custom_interfaces.msg import SwerveModulesList

class SwerveSimBridge(Node):
    def __init__(self):
        super().__init__('swerve_sim_bridge')
        
        # Subscribe to swerve module commands
        self.subscription = self.create_subscription(
            SwerveModulesList,
            '/drive/modules_command',
            self.callback,
            10
        )
        
        # Publishers for each controller (note: /commands plural!)
        self.fl_steer_pub = self.create_publisher(
            Float64MultiArray, 
            '/fl_steer_position_controller/commands',  # PLURAL!
            10
        )
        # ... repeat for all 8 controllers
    
    def callback(self, msg):
        # Convert degrees to radians
        fl_angle_rad = math.radians(msg.front_left.angle)
        
        # Convert linear speed to angular velocity
        wheel_radius = 0.127  # meters
        fl_velocity_rad = msg.front_left.speed / wheel_radius
        
        # Publish as Float64MultiArray (even for single value!)
        self.fl_steer_pub.publish(Float64MultiArray(data=[fl_angle_rad]))
        self.fl_drive_pub.publish(Float64MultiArray(data=[fl_velocity_rad]))
```

**Key Points:**
- Topic name: `/controller_name/commands` (PLURAL)
- Message type: `Float64MultiArray`
- Data format: `Float64MultiArray(data=[value])` (array with single element)
- Convert degrees → radians for steering
- Convert m/s → rad/s for wheels (divide by wheel radius)

---

### 4. Launch File

**Critical timing:** Controllers must load AFTER Gazebo spawns the robot.

```python
from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node

def generate_launch_description():
    # ... setup code ...
    
    # Spawn robot first
    spawn_entity_cmd = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'robot_name']
    )
    
    # Load joint state broadcaster after 5 seconds
    load_joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager']
    )
    
    # Load individual controllers after 6 seconds
    load_fl_steer = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['fl_steer_position_controller', '--controller-manager', '/controller_manager']
    )
    
    ld = LaunchDescription()
    ld.add_action(start_gazebo_cmd)
    ld.add_action(spawn_entity_cmd)
    
    # Delayed controller loading
    ld.add_action(TimerAction(
        period=5.0,
        actions=[load_joint_state_broadcaster]
    ))
    
    ld.add_action(TimerAction(
        period=6.0,
        actions=[
            load_fl_steer,
            load_fr_steer,
            # ... all other controllers
        ]
    ))
    
    return ld
```

**Key Points:**
- Use `TimerAction` to delay controller loading
- Recommended delays: 5s for joint_state_broadcaster, 6s for individual controllers
- Load all steering/drive controllers in parallel at 6s
- Don't start bridge until 7s (after controllers are loaded)

---

## Step-by-Step Integration

### Step 1: Verify Base URDF
- [ ] All joints defined with correct types
- [ ] Joint axes correct (steering: Z-axis, drive: Y-axis typically)
- [ ] Origins positioned correctly
- [ ] Links have inertia values (non-zero mass)

### Step 2: Add Gazebo Properties
- [ ] Friction values on wheel links (`mu1`, `mu2` ≥ 1.0)
- [ ] Materials defined for visualization
- [ ] Contact parameters set (`kp`, `kd`)

### Step 3: Add ros2_control
- [ ] Gazebo plugin added with controller file path
- [ ] Hardware interface defined with GazeboSystem
- [ ] All 8 joints listed with correct command/state interfaces
- [ ] Steering joints use position command interface
- [ ] Drive joints use velocity command interface

### Step 4: Create Controller Config
- [ ] controller_manager section with all 9 controllers listed
- [ ] All controllers use `forward_command_controller/ForwardCommandController`
- [ ] Individual sections for each controller with `joints:` array
- [ ] `interface_name:` specified (position or velocity)

### Step 5: Create Bridge Node
- [ ] Subscribes to your high-level command topic
- [ ] Publishes to `/controller_name/commands` (PLURAL)
- [ ] Uses `Float64MultiArray` message type
- [ ] Data in array format: `data=[value]`
- [ ] Proper unit conversions (degrees→radians, m/s→rad/s)

### Step 6: Create Launch File
- [ ] Reads URDF and substitutes controller file path
- [ ] Starts Gazebo
- [ ] Spawns robot entity
- [ ] Uses TimerAction for delayed controller loading
- [ ] Launches bridge node after controllers

### Step 7: Build and Test
```bash
colcon build --packages-select your_package
source install/setup.bash
ros2 launch your_package sim.launch.py
```

### Step 8: Verify
```bash
# Check all controllers loaded and active
ros2 control list_controllers

# Check all interfaces claimed
ros2 control list_hardware_interfaces

# Test movement
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/your/cmd_vel_topic
```

---

## Common Pitfalls

### Issue 1: Controllers Won't Load
**Symptoms:** "Could not contact service /controller_manager/list_controllers"

**Causes:**
- Gazebo ros2_control plugin not loading
- Controller config file path incorrect in URDF
- URDF uses ROS1 syntax like `$(find package_name)`

**Solution:**
- Use absolute path in URDF or substitute in launch file
- Check Gazebo terminal for ros2_control plugin errors
- Verify: `ros2 node list` should show `/controller_manager`

### Issue 2: Controllers Load but Hardware Interfaces "Unclaimed"
**Symptoms:** `ros2 control list_hardware_interfaces` shows "unclaimed"

**Causes:**
- Wrong controller type in YAML
- Wrong parameter format (using `joint:` instead of `joints:`)
- Missing `interface_name` parameter

**Solution:**
- Use `forward_command_controller/ForwardCommandController`
- Use `joints:` array format
- Always specify `interface_name: position` or `interface_name: velocity`

### Issue 3: Commands Published but Robot Not Moving
**Symptoms:** Bridge publishes, controllers active, but no motion

**Causes:**
- Publishing to wrong topic (`/command` vs `/commands`)
- Wrong message type (`Float64` vs `Float64MultiArray`)
- Friction too low in URDF
- Joint limits too restrictive

**Solution:**
- Publish to `/controller_name/commands` (PLURAL)
- Use `Float64MultiArray(data=[value])`
- Increase `mu1` and `mu2` to 1.0 or higher
- Check joint limits allow desired motion

### Issue 4: Wheels Slip or Slide
**Symptoms:** Robot doesn't move straight, wheels spin without traction

**Causes:**
- Friction coefficients too low
- Contact parameters not tuned
- Wheel inertia too low

**Solution:**
```xml
<gazebo reference="wheel_link">
  <mu1>1.5</mu1>
  <mu2>1.5</mu2>
  <kp>1000000.0</kp>
  <kd>100.0</kd>
</gazebo>
```

### Issue 5: Erratic Movement or Oscillation
**Causes:**
- PID gains not tuned (if using effort controllers)
- Update rate too low
- Multiple commands conflicting

**Solution:**
- Increase controller update rate (100 Hz recommended)
- Use velocity control for drive wheels (simpler than effort)
- Ensure only one node publishes to each controller

---

## Debugging Checklist

When things don't work, go through this checklist:

### Level 1: ROS2 Control System
```bash
# Is controller_manager running?
ros2 node list | grep controller_manager

# Are controllers configured?
ros2 control list_controllers

# Are hardware interfaces available?
ros2 control list_hardware_interfaces

# What controller types are available?
ros2 service call /controller_manager/list_controller_types controller_manager_msgs/srv/ListControllerTypes
```

### Level 2: Topics and Messages
```bash
# What topics exist?
ros2 topic list | grep controller

# Who's publishing/subscribing?
ros2 topic info /fl_steer_position_controller/commands

# What's the message type?
ros2 interface show std_msgs/msg/Float64MultiArray

# Is data flowing?
ros2 topic echo /fl_steer_position_controller/commands
```

### Level 3: Bridge Node
```bash
# Is bridge node running?
ros2 node list | grep bridge

# What topics is it publishing to?
ros2 node info /swerve_sim_bridge

# Is it receiving commands?
ros2 topic echo /drive/modules_command
```

### Level 4: Gazebo
```bash
# Are joints defined in Gazebo?
gz topic -l | grep joint

# Is ros2_control plugin loaded?
# Check Gazebo terminal output for "Loaded gazebo_ros2_control"

# Are joint states being published?
ros2 topic echo /joint_states
```

---

## Key Takeaways

1. **ForwardCommandController is your friend** - Use it for individual joint control in ROS2 Humble
2. **Plural vs Singular matters** - `/commands` topic, `joints:` parameter
3. **Float64MultiArray, not Float64** - Even for single values
4. **Timing is critical** - Use TimerAction to delay controller loading
5. **Absolute paths in URDF** - Or use launch file substitution
6. **Friction prevents slipping** - Set `mu1` and `mu2` ≥ 1.0
7. **Unit conversions** - Degrees→radians, m/s→rad/s
8. **Hardware interfaces must be claimed** - Verify with `list_hardware_interfaces`

---

## Additional Resources

- [ROS2 Control Documentation](https://control.ros.org/)
- [Gazebo ROS2 Control](https://github.com/ros-controls/gazebo_ros2_control)
- [Forward Command Controller](https://github.com/ros-controls/ros2_controllers/tree/master/forward_command_controller)
- [Joint State Broadcaster](https://github.com/ros-controls/ros2_controllers/tree/master/joint_state_broadcaster)

---

**Document Version:** 1.0  
**Date:** December 2025  
**Tested On:** ROS2 Humble, Gazebo Classic 11.10.2
