# Maxwell Gazebo Quick Start Guide

## What Was Created

A complete simulation package (`maxwell_gazebo`) that integrates your swerve drive system with Gazebo.

### Package Contents

```
maxwell_gazebo/
├── urdf/maxwell_swerve.urdf          # Simulation URDF with Gazebo plugins
├── config/swerve_controllers.yaml    # ROS2 control configuration
├── launch/maxwell_sim.launch.py      # Main simulation launch file
├── maxwell_gazebo/
│   ├── __init__.py
│   └── swerve_sim_bridge.py         # Bridge between drive controller and Gazebo
├── package.xml
├── setup.py
└── README.md
```

## How It Works

### Architecture

```
User Input → Drive Controller → SwerveModulesList → Swerve Sim Bridge → Gazebo Joint Controllers → Robot Movement
                ↓
         /drive/cmd_vel (/drive/cmd_vel_repeat)
                ↓
         /drive/modules_command
                ↓
    Individual Joint Commands (position/velocity)
                ↓
         Gazebo Simulation
```

### Components

1. **maxwell_swerve.urdf**: Modified URDF with:
   - Fixed joint limits on steering joints (±120° = ±2.094 rad)
   - ros2_control hardware interface
   - Gazebo plugins for physics simulation
   - Proper wheel friction and dynamics

2. **Swerve Sim Bridge**: Converts SwerveModulesList messages to individual joint commands:
   - Steering angles (degrees → radians) → Position controllers
   - Wheel speeds (m/s → rad/s) → Velocity controllers

3. **ROS2 Control**: Manages 8 joint controllers:
   - 4 position controllers for steering (FL, FR, BL, BR rotation joints)
   - 4 velocity controllers for driving (FL, FR, BL, BR wheel joints)

4. **Drive Controller**: Your existing drive system from the `drive` package

## Launch the Simulation

### Step 1: Build and Source

```bash
cd /home/koener/Documents/MMRT_2025_Autonomy/ros2_ws
colcon build --packages-select maxwell_gazebo --symlink-install
source install/setup.bash
```

### Step 2: Launch Gazebo Simulation

```bash
ros2 launch maxwell_gazebo maxwell_sim.launch.py
```

**Wait ~7 seconds** for all controllers to load. You should see messages indicating controllers are ready.

### Step 3: Control the Robot

**In a NEW terminal:**

```bash
cd /home/koener/Documents/MMRT_2025_Autonomy/ros2_ws
source install/setup.bash
```

**Option 1: Keyboard Control**
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/drive/cmd_vel
```

**Option 2: Xbox Controller**
```bash
ros2 launch drive xbox_controller.launch.py drive_mode:=SWERVE_DRIVE
```

**Option 3: Direct Command**
```bash
# Move forward
ros2 topic pub /drive/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" --rate 10

# Rotate in place
ros2 topic pub /drive/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.5}}" --rate 10

# Strafe sideways (swerve advantage!)
ros2 topic pub /drive/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.5, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" --rate 10
```

## Launch Arguments

```bash
ros2 launch maxwell_gazebo maxwell_sim.launch.py \
    x_pose:=1.0 \
    y_pose:=2.0 \
    z_pose:=0.3 \
    drive_mode:=SWERVE_DRIVE
```

- `x_pose`, `y_pose`, `z_pose`: Initial spawn position
- `drive_mode`: SWERVE_DRIVE or TANK_STEER_HYBRID
- `use_sim_time`: true (automatically set for simulation)

## Monitoring and Debugging

### Check Active Topics

```bash
ros2 topic list
```

Important topics:
- `/drive/cmd_vel` - Velocity commands (input)
- `/drive/cmd_vel_repeat` - Repeated velocity commands (heartbeat)
- `/drive/modules_command` - Swerve module commands
- `/joint_states` - Current joint positions/velocities
- `/fl_steer_position_controller/command` - FL steering angle
- `/fl_drive_velocity_controller/command` - FL wheel velocity
- (Similar for FR, BL, BR)

### View Joint States

```bash
ros2 topic echo /joint_states
```

### View Drive Commands

```bash
ros2 topic echo /drive/modules_command
```

### Check Controller Status

```bash
ros2 control list_controllers
```

You should see 9 controllers loaded:
- joint_state_broadcaster
- fl_steer_position_controller
- fr_steer_position_controller
- bl_steer_position_controller
- br_steer_position_controller
- fl_drive_velocity_controller
- fr_drive_velocity_controller
- bl_drive_velocity_controller
- br_drive_velocity_controller

## Troubleshooting

### Robot doesn't move

1. **Check controllers are loaded:**
   ```bash
   ros2 control list_controllers
   ```
   All should show `[active]`

2. **Check messages are flowing:**
   ```bash
   ros2 topic echo /drive/modules_command
   ```

3. **Verify bridge is running:**
   ```bash
   ros2 node list | grep swerve_sim_bridge
   ```

### Controllers fail to load

- Wait longer (controllers load 5-7 seconds after spawn)
- Check Gazebo is running: `ps aux | grep gzserver`
- Restart the simulation

### Wheels sliding/not gripping

- Check friction values in URDF (mu1, mu2)
- Verify wheel contact with ground (z_pose should be ~0.3)

## Understanding Swerve Drive

Your robot has **4 independent swerve modules** (FL, FR, BL, BR). Each module has:

1. **Steering Joint** (`*_Rot_Joint`): Rotates the wheel assembly ±120°
2. **Drive Joint** (`*_Joint`): Spins the wheel forward/backward

This allows:
- **Forward/backward**: All wheels point forward, spin same direction
- **Rotation**: Wheels point tangent to circle, spin appropriately
- **Strafing**: All wheels point sideways, spin same direction
- **Diagonal**: Combination of forward and sideways
- **Complex maneuvers**: Each wheel can point and spin independently

The `SteeringModel` class in `drive/model.py` computes the required angle and speed for each wheel given a desired body velocity (x, y, angular_z).

## Next Steps

1. **Tune Parameters**: Adjust wheel friction, controller gains, dynamics in the URDF
2. **Add Sensors**: Add cameras, lidars, IMU to the URDF
3. **Test Scenarios**: Create custom worlds with obstacles
4. **Record Data**: Use `rosbag` to record simulation data
5. **Compare Real vs Sim**: Test same commands on real robot and simulation

## Files Modified vs Original

**No files in maxwell_description were modified** - all simulation code is in the new `maxwell_gazebo` package. The simulation references meshes from `maxwell_description` but doesn't change them.
