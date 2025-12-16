# Maxwell Gazebo Simulation

This package provides Gazebo simulation for the Maxwell rover with full swerve drive functionality.

## Quick Start

### 1. Build and Source

```bash
cd /path/to/ros2_ws
colcon build --packages-select maxwell_gazebo
source install/setup.bash
```

### 2. Launch Simulation

```bash
ros2 launch maxwell_gazebo maxwell_sim.launch.py
```

This will:
- Start Gazebo with the Maxwell rover model
- Load all ROS2 control controllers (8 joint controllers + joint state broadcaster)
- Launch the drive controller and swerve simulation bridge
- Spawn the robot at position (0, 0, 0.3)

### 3. Control the Robot

In a new terminal (after sourcing the workspace):

```bash
# Keyboard control (recommended for testing)
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/drive/cmd_vel
```

**Controls:**
- `i` - Forward
- `k` - Stop
- `j` - Strafe left
- `l` - Strafe right
- `u` - Forward + rotate left
- `o` - Forward + rotate right
- `m` - Backward
- `,` - Backward + rotate left
- `.` - Backward + rotate right

## Package Structure

```
maxwell_gazebo/
├── config/
│   └── swerve_controllers.yaml    # ROS2 control configuration
├── launch/
│   └── maxwell_sim.launch.py      # Main simulation launch file
├── maxwell_gazebo/
│   └── swerve_sim_bridge.py       # Bridge node (SwerveModulesList → Joint commands)
├── urdf/
│   └── maxwell_swerve.urdf        # Simulation URDF with ros2_control & Gazebo plugins
└── README.md
```

## How It Works

The swerve drive simulation pipeline:

1. **Twist Command** (`/drive/cmd_vel`) - User input (teleop, autonomous, etc.)
2. **Drive Controller** - Converts Twist to swerve module commands
3. **SwerveModulesList** (`/drive/modules_command`) - 4 modules with angle/speed
4. **Swerve Sim Bridge** - Converts to 8 individual joint commands
5. **ROS2 Controllers** - 4 position controllers (steering) + 4 velocity controllers (wheels)
6. **Gazebo** - Simulates physics and joint actuation
7. **Joint States** - Published back for odometry and visualization

## Swerve Module Configuration

Each of the 4 modules has two joints:
- **FL** (Front Left): `FL_Rot_Joint` (steering), `FL_Joint` (drive)
- **FR** (Front Right): `FR_Rot_Joint` (steering), `FR_Joint` (drive)
- **BL** (Back Left): `BL_Rot_Joint` (steering), `BL_Joint` (drive)
- **BR** (Back Right): `BR_Rot_Joint` (steering), `BR_Joint` (drive)

**Capabilities:**
- ±120° steering range per module
- Independent wheel velocity control
- True omnidirectional movement (strafe, crab, rotate in place)

## Verification Commands

Check that everything is running correctly:

```bash
# List active controllers (should show 9 controllers as 'active')
ros2 control list_controllers

# Check hardware interfaces (should show all as 'claimed')
ros2 control list_hardware_interfaces

# View joint states
ros2 topic echo /joint_states

# Monitor drive commands
ros2 topic echo /drive/modules_command
```

## Troubleshooting

**Robot not moving:**
- Verify controllers loaded: `ros2 control list_controllers` (all should be "active")
- Check bridge is running: `ros2 node list | grep swerve_sim_bridge`
- Verify commands reaching Gazebo: `ros2 topic echo /fl_steer_position_controller/commands`

**Controllers fail to load:**
- Ensure Gazebo is fully started before controllers spawn (5-7 second delays in launch file)
- Check controller configuration: `ros2 param list /controller_manager`

**Wheels sliding:**
- Adjust friction in URDF (`mu1`, `mu2` parameters)
- Check wheel inertia values

## Advanced Usage

### Custom Spawn Position

```bash
ros2 launch maxwell_gazebo maxwell_sim.launch.py x_pose:=2.0 y_pose:=1.0 z_pose:=0.5
```

### Different Drive Mode

```bash
ros2 launch maxwell_gazebo maxwell_sim.launch.py drive_mode:=TANK_STEER_HYBRID
```

## Dependencies

- ROS 2 Humble
- Gazebo Classic 11
- gazebo_ros2_control
- controller_manager
- forward_command_controller
- Custom packages: `drive`, `custom_interfaces`, `maxwell_description`
