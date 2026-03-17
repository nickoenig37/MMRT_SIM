# Maxwell Terrain Worlds - Quick Reference

## Added 4 New Terrain Worlds** in `/ros2_ws/src/maxwell/ros_ws/src/maxwell_gazebo/worlds/`:

1. **mars_rough_terrain.world** - Mars-like terrain with rocks, boulders, Mars gravity
2. **rocky_hills.world** - Hills, mountains, steep slopes  
3. **obstacle_course.world** - Ramps, steps, narrow passages, obstacles
4. **empty.world** - Flat ground for basic testing

**Updated Launch File** - Added world selection parameter

## Quick Start

```bash
# 1. Build
cd /home/koener/Documents/MMRT_2025_Autonomy/ros2_ws
./src/maxwell/ros_ws/src/maxwell_gazebo/test_worlds.sh

# 2. Launch with Mars terrain (default)
ros2 launch maxwell_gazebo maxwell_sim.launch.py

# 3. Or launch specific world
ros2 launch maxwell_gazebo maxwell_sim.launch.py world:=rocky_hills
ros2 launch maxwell_gazebo maxwell_sim.launch.py world:=obstacle_course
ros2 launch maxwell_gazebo maxwell_sim.launch.py world:=empty

# 4. Control (new terminal)
source install/setup.bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}}" --once
```

## World Features

| World | Terrain | Obstacles | Difficulty | Best For |
|-------|---------|-----------|------------|----------|
| **mars_rough_terrain** | Heightmap, uneven | Rocks, boulders | High | Navigation, path planning |
| **rocky_hills** | Hills, mountains | Rock clusters | Very High | Slope handling, climbing |
| **obstacle_course** | Flat | Ramps, steps, walls | Medium | Precision, validation |
| **empty** | Flat | None | Easy | Debugging, tuning |


