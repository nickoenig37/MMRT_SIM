# Maxwell Autonomy Architecture

## Overview

The Maxwell autonomy system is built as a **hierarchical three-tier architecture** using ROS 2 packages. Each tier builds upon the previous one, allowing independent usage or full integration for autonomous navigation.

```
┌─────────────────────────────────────────────────────────────┐
│  TIER 3: maxwell_navigation (Autonomous Navigation)         │
│  • Nav2 autonomous navigation stack                         │
│  • AMCL particle filter localization                        │
│  • NavFN global planner + Regulated Pure Pursuit controller │
│  • Dependency: maxwell_localization                         │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
                   Includes via Launch
                            │
┌─────────────────────────────────────────────────────────────┐
│  TIER 2: maxwell_localization (Sensor Fusion & Odometry)    │
│  • Robot Localization (Dual EKF filters)                    │
│  • Wheel odometry estimation                                │
│  • Local + Global reference frames                          │
│  • Dependency: maxwell_gazebo                               │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
                   Includes via Launch
                            │
┌─────────────────────────────────────────────────────────────┐
│  TIER 1: maxwell_gazebo (Simulation Core)                   │
│  • Gazebo physics simulation                                │
│  • Maxwell rover URDF model with swerve drive               │
│  • Sensor plugins (RGB-D, IMU)                              │
│  • Terrain worlds (Marsyard 2020/2021/2022)                 │
│  • No dependencies on localization/navigation               │
└─────────────────────────────────────────────────────────────┘
```

---

## Package Descriptions

### 1. maxwell_gazebo - Simulation Foundation

**Purpose**: Core Gazebo simulation of the Maxwell rover in realistic terrain environments.

**Location**: `ros2_ws/src/maxwell/ros_ws/src/maxwell_gazebo/`

**Key Components**:
- **URDF Model**: `urdf/maxwell_swerve.urdf` - Complete rover geometry with 4 swerve drive modules
- **Launch File**: `launch/maxwell_sim.launch.py` - Base simulation launcher (accepts `run_rviz` parameter)
- **Worlds**: Three Marsyard terrain variants in `worlds/`
- **RViz Config**: `config/maxwell_sim_rviz2_setup.rviz` - Visualization setup for pure simulation

**Usage**:
```bash
# Launch simulation only (no localization/navigation)
ros2 launch maxwell_gazebo maxwell_sim.launch.py world:=marsyard_2021

# With RViz for monitoring
ros2 launch maxwell_gazebo maxwell_sim.launch.py world:=marsyard_2021 run_rviz:=true

# Without RViz (for headless operation)
ros2 launch maxwell_gazebo maxwell_sim.launch.py world:=marsyard_2021 run_rviz:=false
```

**Dependencies**:
- gazebo_ros, gazebo_plugins
- robot_state_publisher
- drive package (Maxwell motor controllers)
- maxwell_description

---

### 2. maxwell_localization - Sensor Fusion Layer

**Purpose**: Adds sensor fusion and odometry estimation on top of Gazebo simulation.

**Location**: `ros2_ws/src/maxwell/ros_ws/src/maxwell_localization/`

**Key Components**:
- **Wheel Odometry Node**: `maxwell_localization/wheel_odometry.py` - Converts joint states to odometry messages
  - Calculates swerve drive kinematics
  - Fuses wheel encoder data with IMU
  - Publishes `/wheel/odometry` topic
  
- **EKF Localization Filters**: `config/ekf_localization.yaml` - Dual Extended Kalman Filters
  - **Local Filter** (`ekf_odom`): Fuses wheel odometry + IMU → `/odometry/local` (local reference frame)
  - **Global Filter** (`ekf_map`): Fuses local odometry + SLAM/mapping → `/odometry/global` (global reference frame)
  - Broadcasts `map→odom` transform for navigation stack
  
- **Launch File**: `launch/maxwell_localization.launch.py`
  - Calls `maxwell_gazebo/maxwell_sim.launch.py` with `run_rviz:=false`
  - Starts wheel_odometry node
  - Configures and starts both EKF filters
  - Converts depth camera to 2D laser scan for Nav2
  - Conditionally launches RViz via `run_rviz` parameter
  
- **RViz Config**: `config/maxwell_localization_rviz2.rviz` - Localization-focused visualization
  - Shows odometry topics
  - Displays sensor data (RGB-D, IMU)
  - Shows odometry reference frames

**Usage**:
```bash
# Launch simulation + localization (no Nav2)
ros2 launch maxwell_localization maxwell_localization.launch.py world:=marsyard_2021

# With RViz to monitor localization
ros2 launch maxwell_localization maxwell_localization.launch.py world:=marsyard_2021 run_rviz:=true

# Headless (for autonomous navigation via Nav2)
ros2 launch maxwell_localization maxwell_localization.launch.py world:=marsyard_2021 run_rviz:=false
```

**Topics Published**:
- `/wheel/odometry` - Odometry from wheel encoders
- `/odometry/local` - Local EKF estimate
- `/odometry/global` - Global EKF estimate (with map frame)
- `/scan` - 2D laser scan from depth camera

**Transforms Broadcast**:
- `odom → base_link` (from local EKF)
- `map → odom` (from global EKF)

**Dependencies**:
- maxwell_gazebo
- robot_localization (EKF node)
- depthimage_to_laserscan (depth→scan conversion)
- rviz2

---

### 3. maxwell_navigation - Autonomous Navigation Stack

**Purpose**: Adds full Nav2 autonomous navigation capability on top of localization.

**Location**: `ros2_ws/src/maxwell/ros_ws/src/maxwell_navigation/`

**Key Components**:
- **Nav2 Parameters**: `config/nav2_params.yaml` - Complete Nav2 stack configuration
  - **AMCL**: Particle filter for global localization refinement
  - **NavFN Planner**: Global path planning algorithm
  - **Regulated Pure Pursuit**: Local trajectory controller optimized for swerve drive
  - **Costmap Configuration**: Local and global costmaps with obstacle layers
  - **Recovery Behaviors**: Spin and backup recovery behaviors
  
- **Controller Tuning**: `config/nav2_controllers.yaml` - Swerve drive-specific parameters
  - Lookahead distances for path tracking
  - Angular velocity limits
  - Acceleration constraints
  
- **Launch File**: `launch/maxwell_navigation.launch.py`
  - Calls `maxwell_localization/maxwell_localization.launch.py` with `run_rviz:=false`
  - Starts Nav2 bringup (loads parameters, starts behavior tree navigator)
  - Starts Lifecycle Manager for Nav2 nodes
  - Conditionally launches Navigation RViz via `run_rviz` parameter
  
- **RViz Config**: `config/maxwell_navigation_rviz2.rviz` - Navigation-focused visualization
  - Shows planned paths
  - Displays costmaps (local and global)
  - Shows navigation goals and robot pose
  - Displays laser scan data

**Usage**:
```bash
# Launch full autonomy stack
ros2 launch maxwell_navigation maxwell_navigation.launch.py world:=marsyard_2021

# With RViz for monitoring navigation
ros2 launch maxwell_navigation maxwell_navigation.launch.py world:=marsyard_2021 run_rviz:=true

# Headless (for deployment)
ros2 launch maxwell_navigation maxwell_navigation.launch.py world:=marsyard_2021 run_rviz:=false
```

**Then to give navigation goals**:
```bash
# Send navigation goal via CLI
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {pose: {position: {x: 5.0, y: 5.0}, orientation: {w: 1.0}}}}"

# Or use RViz 2D Nav Goal button
```

**Dependencies**:
- maxwell_localization
- nav2_bringup, nav2_core, nav2_controller, nav2_planner
- nav2_recoveries, nav2_bt_navigator
- nav2_navfn_planner, nav2_regulated_pure_pursuit_controller, nav2_amcl
- nav2_lifecycle_manager
- rviz2

---

## Launch File Hierarchy

The launch files form a clear hierarchy with parameter passing:

```
maxwell_navigation.launch.py
├─ run_rviz → false (prevents duplicate RViz)
├─ Calls: maxwell_localization.launch.py
│   ├─ run_rviz → false (prevents duplicate RViz)
│   ├─ Calls: maxwell_gazebo/maxwell_sim.launch.py
│   │   └─ run_rviz → false (base layer doesn't need RViz)
│   ├─ Starts: wheel_odometry node
│   ├─ Starts: EKF filters (ekf_odom, ekf_map)
│   ├─ Starts: depth_to_laserscan converter
│   └─ Conditionally starts: RViz (if run_rviz=true from maxwell_navigation)
├─ Starts: Nav2 bringup
├─ Starts: Lifecycle Manager
└─ Conditionally starts: Navigation RViz (if run_rviz=true)
```

**RViz Parameter Flow**:
- Top-level `run_rviz` parameter is passed down through the hierarchy
- Middle and base layers disable RViz to prevent duplicates
- Only the top-level layer with `run_rviz:=true` launches RViz
- Each layer has its own RViz config that shows layer-specific data

---

## Package Structure

```
maxwell_gazebo/
├── package.xml
├── setup.py
├── setup.cfg
├── launch/
│   ├── maxwell_sim.launch.py (accepts run_rviz parameter)
│   └── maxwell_autonomy_sim.launch.py
├── urdf/
│   └── maxwell_swerve.urdf
├── worlds/
│   ├── marsyard_2020.world
│   ├── marsyard_2021.world
│   └── marsyard_2022.world
├── config/
│   ├── maxwell_sim_rviz2_setup.rviz
│   └── swerve_controllers.yaml
└── models/ (Marsyard terrain data)

maxwell_localization/
├── package.xml
├── setup.py
├── setup.cfg
├── launch/
│   └── maxwell_localization.launch.py
├── config/
│   ├── ekf_localization.yaml
│   └── maxwell_localization_rviz2.rviz
└── maxwell_localization/
    └── wheel_odometry.py

maxwell_navigation/
├── package.xml
├── setup.py
├── setup.cfg
├── launch/
│   └── maxwell_navigation.launch.py
└── config/
    ├── nav2_params.yaml
    ├── nav2_controllers.yaml
    └── maxwell_navigation_rviz2.rviz
```

---

## Usage Scenarios

### Scenario 1: Simulation Only
```bash
# Test Gazebo physics and sensor simulation
ros2 launch maxwell_gazebo maxwell_sim.launch.py world:=marsyard_2021 run_rviz:=true
```
✓ Use when: Testing rover dynamics, sensor plugins, terrain interaction

---

### Scenario 2: Localization Development
```bash
# Test sensor fusion and odometry estimation
ros2 launch maxwell_localization maxwell_localization.launch.py world:=marsyard_2021 run_rviz:=true
```
✓ Use when: 
- Tuning EKF filter parameters
- Testing odometry accuracy
- Developing new sensor fusion algorithms
- Debugging localization transforms

---

### Scenario 3: Full Autonomous Navigation
```bash
# Complete autonomy stack with visualization
ros2 launch maxwell_navigation maxwell_navigation.launch.py world:=marsyard_2021 run_rviz:=true
```
✓ Use when:
- Testing autonomous navigation algorithms
- Developing Nav2 behaviors
- Evaluating path planning and control

---

### Scenario 4: Deployment (Headless)
```bash
# Run autonomy without GUI overhead
ros2 launch maxwell_navigation maxwell_navigation.launch.py world:=marsyard_2021 run_rviz:=false
```
✓ Use when:
- Running on resource-constrained systems
- Long-duration testing without visualization
- Production deployment

---

## Parameter Documentation

### maxwell_sim.launch.py
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `world` | string | `marsyard_2021` | Gazebo world to load (marsyard_2020, marsyard_2021, marsyard_2022) |
| `run_rviz` | bool | `false` | Launch RViz2 (should be false when called by parent launch) |

### maxwell_localization.launch.py
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `world` | string | `marsyard_2021` | Gazebo world to load |
| `run_rviz` | bool | `true` | Launch localization RViz2 |

### maxwell_navigation.launch.py
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `world` | string | `marsyard_2021` | Gazebo world to load |
| `run_rviz` | bool | `true` | Launch navigation RViz2 |

---

## Building

```bash
# Build all packages
cd ~/Documents/MMRT_2025_Autonomy/ros2_ws
colcon build --symlink-install

# Build specific package
colcon build --symlink-install --packages-select maxwell_navigation

# Build with verbose output
colcon build --symlink-install --event-handlers console_direct+
```

---

## Troubleshooting

### Issue: "Package not found" error
```bash
# Ensure workspace is sourced
source ~/Documents/MMRT_2025_Autonomy/ros2_ws/install/setup.bash

# Rebuild if needed
colcon build --symlink-install
```

### Issue: RViz windows appearing multiple times
- Ensure you're only launching the top-level package with `run_rviz:=true`
- When testing individual layers, use `run_rviz:=false` to prevent cascading RViz instances

### Issue: Navigation goals not working
- Verify AMCL is reporting good localization (green particles in RViz)
- Check that Nav2 lifecycle nodes are in "active" state: `ros2 lifecycle get /amcl_node`
- Ensure `/scan` topic is being published: `ros2 topic echo /scan`

---

## Development Notes

### Adding New Nodes to Localization Layer
1. Add node startup to `maxwell_localization/launch/maxwell_localization.launch.py`
2. Ensure node uses `/odometry/local` or `/odometry/global` topics
3. Update RViz config to visualize new node outputs

### Adding New Behaviors to Navigation Layer
1. Use Nav2 Behavior Tree Framework
2. Add behavior tree XML files to maxwell_navigation
3. Reference in `nav2_params.yaml` under `bt_navigator`

### Tuning Navigation Performance
1. Edit `maxwell_navigation/config/nav2_params.yaml`
2. Focus on Regulated Pure Pursuit controller parameters (key for swerve drive)
3. Adjust costmap inflation radius for obstacle avoidance
4. Test in simulation first before deployment

---

## ROS 2 Version
- **Target**: ROS 2 Humble
- **Tested with**: Gazebo 11+

---

## Contact & Support
For issues or questions about the autonomy architecture, refer to the individual package READMEs or contact the Maxwell Autonomy Team.
