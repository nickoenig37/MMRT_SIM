# Maxwell Gazebo Swerve Drive Simulation - Summary

## What Was Done

Created a complete ROS 2 simulation package (`maxwell_gazebo`) that integrates your real swerve drive system with Gazebo simulation.

## Package Structure

```
maxwell_gazebo/
├── urdf/maxwell_swerve.urdf              # Simulation robot model
├── config/swerve_controllers.yaml        # Joint controller configuration  
├── launch/maxwell_sim.launch.py          # Main launch file
├── maxwell_gazebo/swerve_sim_bridge.py   # Bridge node
├── README.md                             # Package documentation
├── QUICKSTART.md                         # Quick start guide
├── package.xml                           # Package manifest
└── setup.py                              # Python package setup
```

## Key Features

**Full Swerve Drive**: 4 independent steering and drive joints
**Uses Your Drive Code**: Integrates `drive` package's `drive_controller`, `heartbeat`, and `SteeringModel`
**No Modifications**: Original `maxwell_description` package untouched
**Complete Control Stack**: Twist commands → Drive controller → Gazebo joints
**ROS 2 Control**: Position controllers for steering, velocity controllers for wheels

## Quick Start

### 1. Launch Simulation
```bash
cd /home/koener/Documents/MMRT_2025_Autonomy/ros2_ws
source install/setup.bash
ros2 launch maxwell_gazebo maxwell_sim.launch.py
```

### 2. Control Robot (new terminal)
```bash
source install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/drive/cmd_vel
```

## How It Works

**Data Flow:**
```
Twist Command → Drive Controller → SwerveModulesList → Swerve Bridge → Joint Commands → Gazebo → Robot Moves
```

**Components:**
1. **Drive Controller** (`drive` package): Converts Twist to SwerveModulesList using your `SteeringModel`
2. **Swerve Sim Bridge** (`maxwell_gazebo`): Converts SwerveModulesList to 8 individual joint commands
3. **ROS2 Control**: Manages position/velocity controllers for each joint
4. **Gazebo**: Simulates physics and renders robot

## Swerve Module Mapping

| Module | Steering Joint | Drive Joint | Position in URDF |
|--------|---------------|-------------|------------------|
| FL (Front Left)  | `FL_Rot_Joint` | `FL_Joint` | (+0.49, +0.31, -0.18) |
| FR (Front Right) | `FR_Rot_Joint` | `FR_Joint` | (+0.49, -0.31, -0.18) |
| BL (Rear Left)   | `BL_Rot_Joint` | `BL_Joint` | (-0.49, +0.31, -0.18) |
| BR (Rear Right)  | `BR_Rot_Joint` | `BR_Joint` | (-0.49, -0.31, -0.18) |

Each module:
- **Steers**: ±120° (±2.094 rad)
- **Drives**: Continuous rotation

## Testing Your Swerve Drive

### Test 1: Forward Motion
```bash
ros2 topic pub /drive/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" --rate 10
```
**Expected**: All wheels point forward, spin at same speed

### Test 2: Rotation in Place
```bash
ros2 topic pub /drive/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.5}}" --rate 10
```
**Expected**: Wheels point tangent to circle, robot spins

### Test 3: Strafing (Swerve Magic!)
```bash
ros2 topic pub /drive/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.5, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" --rate 10
```
**Expected**: All wheels point sideways (90°), robot moves laterally

### Test 4: Diagonal Movement
```bash
ros2 topic pub /drive/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5, y: 0.5, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" --rate 10
```
**Expected**: All wheels point 45°, robot moves diagonally

## Configuration Files

### `maxwell_swerve.urdf`
- Copied all links/joints from original URDF
- Fixed steering joint limits: `-2.094` to `+2.094` rad (±120°)
- Added `base_footprint` for odometry
- Added wheel friction (`mu1=1.0`, `mu2=1.0`)
- Added ros2_control hardware interface
- Added Gazebo plugins

### `swerve_controllers.yaml`
- 1 joint_state_broadcaster (publishes all joint states)
- 4 position controllers (steering angles)
- 4 velocity controllers (wheel speeds)

### `maxwell_sim.launch.py`
- Launches Gazebo
- Spawns robot
- Loads all controllers (with delays for stability)
- Starts drive_controller, heartbeat, and swerve_sim_bridge

### `swerve_sim_bridge.py`
- Subscribes to `/drive/modules_command` (SwerveModulesList)
- Publishes to 8 controller topics (Float64 messages)
- Converts degrees to radians for steering
- Converts m/s to rad/s for wheels (using wheel_radius=0.127m)

## Customization

### Change Wheel Friction
Edit `urdf/maxwell_swerve.urdf`, find `<gazebo reference="FL_Link">` sections:
```xml
<mu1>1.0</mu1>  <!-- Static friction -->
<mu2>1.0</mu2>  <!-- Dynamic friction -->
```

### Change Controller Gains
Edit `config/swerve_controllers.yaml` to add PID gains if needed.

### Change Spawn Position
```bash
ros2 launch maxwell_gazebo maxwell_sim.launch.py x_pose:=5.0 y_pose:=3.0 z_pose:=0.5
```

## Troubleshooting

**Robot falls through ground?**
- Increase `z_pose` (default 0.3)
- Check collision meshes exist

**Wheels slip?**
- Increase friction in URDF
- Check wheel contact with ground

**Controllers don't load?**
- Wait 7 seconds after launch
- Check `ros2 control list_controllers`

**No movement?**
- Verify `ros2 topic echo /drive/modules_command` shows data
- Check `ros2 node list` includes `swerve_sim_bridge`

## Next Steps

1. ✅ **Test basic movements** (forward, rotate, strafe)
2. ⬜ **Add sensors** (cameras, lidar, IMU) to URDF
3. ⬜ **Tune parameters** (friction, gains, dynamics)
4. ⬜ **Create test worlds** (obstacles, terrain)
5. ⬜ **Compare sim vs real** robot behavior
6. ⬜ **Use for algorithm development** before deploying to hardware

## Files NOT Modified

The following packages remain unchanged:
- `maxwell_description/` - Original URDF and meshes
- `drive/` - Your drive controller code

All simulation code is isolated in `maxwell_gazebo/`.

---

**You now have a fully functional swerve drive robot in Gazebo simulation!** 🎉
