# Maxwell Robot Description

This package contains the URDF description and visualization tools for the Maxwell rover, imported from SolidWorks.

## Setup Changes Made After Import

### 1. Package Configuration
- **Updated `package.xml`**: Changed package name from `robot_description` to `maxwell_description`
- **Updated `CMakeLists.txt`**: Changed project name to match `maxwell_description`
- **Added dependency**: Added `gazebo_ros` to package dependencies

### 2. URDF Mesh Path Corrections
- **Fixed mesh references**: Updated all mesh file paths in `PROPER_Simplified Rover.SLDASM.urdf`
  - Changed from: `package://PROPER_Simplified Rover.SLDASM/meshes/`
  - Changed to: `package://maxwell_description/meshes/`

### 3. Gazebo Launch File Creation
- **Created `launch/gazebo.launch.py`**: New launch file for Gazebo visualization with:
  - Robot state publisher for TF broadcasting
  - Gazebo world spawning
  - Entity spawner with configurable position
  - `GAZEBO_MODEL_PATH` environment variable configuration for mesh loading
  - XML declaration stripping to prevent spawn errors

### 4. Workspace Cleanup
- **Removed conflicting package**: Deleted old `maxwell_urdf` package from install directory to prevent naming conflicts

## Launch Commands

### Visualize in Gazebo

```bash
cd /home/koener/Documents/MMRT_2025_Autonomy/ros2_ws
source install/setup.bash
ros2 launch maxwell_description gazebo.launch.py
```

### Visualize in RViz

```bash
ros2 launch maxwell_description display.launch.py
```

### Launch with Custom Position (Gazebo)

```bash
ros2 launch maxwell_description gazebo.launch.py x_pose:=1.0 y_pose:=2.0 z_pose:=1.0
```

### Available Launch Arguments

- `use_sim_time` (default: `true`) - Use simulation clock
- `x_pose` (default: `0.0`) - X position to spawn the robot
- `y_pose` (default: `0.0`) - Y position to spawn the robot  
- `z_pose` (default: `0.5`) - Z position to spawn the robot (height above ground)

## Building the Package

```bash
cd /home/koener/Documents/MMRT_2025_Autonomy/ros2_ws
colcon build --packages-select maxwell_description --symlink-install
source install/setup.bash
```

## Known Issues & Warnings

- **KDL Parser Warning**: The root link `Base_link` has inertia specified, which KDL doesn't support. This is a harmless warning and doesn't affect visualization.
- **Missing model.config**: Gazebo may show warnings about missing `model.config` files for directories in the model path. These are harmless and don't affect robot visualization.

## Robot Structure

The robot includes the following links:
- `Base_link` - Main chassis
- `Camera_link` - Camera mount
- `FL_Link`, `FR_Link`, `BL_Link`, `BR_Link` - Wheel links (Front/Back Left/Right)
- `FL_Rot_Link`, `FR_Rot_Link`, `BL_Rot_Link`, `BR_Rot_Link` - Wheel rotation links

All mesh files are located in the `meshes/` directory as STL files.