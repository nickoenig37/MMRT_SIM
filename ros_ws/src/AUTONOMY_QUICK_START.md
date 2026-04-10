# Maxwell Autonomy - Quick Start

## Build Everything

```bash
cd ~/Documents/MMRT_2025_Autonomy/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

## Quick Launch Commands

### Option 1: Simulation Only (Pure Gazebo)
```bash
ros2 launch maxwell_gazebo maxwell_sim.launch.py world:=marsyard_2021 run_rviz:=true
```

### Option 2: Simulation + Localization (Odometry Fusion)
```bash
ros2 launch maxwell_localization maxwell_localization.launch.py world:=marsyard_2021 run_rviz:=true
```

### Option 3: Full Autonomy (Simulation + Localization + Nav2)
```bash
ros2 launch maxwell_navigation maxwell_navigation.launch.py world:=marsyard_2021 run_rviz:=true
```

## Send Navigation Goals

Once full autonomy is running, in another terminal:

```bash
# Source workspace
source ~/Documents/MMRT_2025_Autonomy/ros2_ws/install/setup.bash

# Send goal to specific coordinates
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {pose: {position: {x: 5.0, y: 5.0}, orientation: {w: 1.0}}}}"
```

Or use **RViz**: Click the "2D Nav Goal" button and click on the map to set a goal.

## Check System Status

```bash
# List active nodes
ros2 node list

# Check published topics
ros2 topic list

# Monitor odometry
ros2 topic echo /odometry/local

# Check Nav2 lifecycle state
ros2 lifecycle get /amcl_node
```

## Available Worlds

- `marsyard_2020` - 2020 Marsyard terrain
- `marsyard_2021` - 2021 Marsyard terrain (default)
- `marsyard_2022` - 2022 Marsyard terrain

## Package Hierarchy

```
maxwell_navigation (Autonomous Navigation)
    └─ maxwell_localization (Odometry Fusion)
        └─ maxwell_gazebo (Simulation)
```

Each layer can run independently!

## Documentation

- **Full Architecture Guide**: `AUTONOMY_ARCHITECTURE.md`
- **Each Package**: Individual README.md files

---

**ROS 2 Version**: Humble  
**Status**: ✓ Ready for testing
