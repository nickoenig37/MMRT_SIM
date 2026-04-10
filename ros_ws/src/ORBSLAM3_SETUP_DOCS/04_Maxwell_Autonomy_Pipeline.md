# 04 - Maxwell autonomy pipeline (SLAM localization + EKF + obstacle sensing)

This setup separates localization from obstacle sensing:

- **Localization**
  - Wheel + IMU are fused in `robot_localization` local EKF (`odom -> base_footprint`).
  - ORB-SLAM3 publishes global pose on `/robot/robot_pose_slam`.
  - Global EKF fuses `/odometry/local` + `/robot/robot_pose_slam` and publishes `map -> odom`.
- **Obstacle detection**
  - Use **dense** depth data from D435 simulation:
    - `/camera/depth/color/points` (PointCloud2)
    - `/camera/depth/scan` (LaserScan generated from raw depth)

---

## A) Launch Maxwell sim + localization pipeline (maxwell repo)

```bash
cd ~/Documents/MMRT_2025_Autonomy/ros2_ws
source install/setup.bash
ros2 launch maxwell_gazebo maxwell_autonomy_sim.launch.py world:=marsyard2020
```

Key outputs:

- `/wheel/odometry`
- `/odometry/local`
- `/odometry/global`
- `/camera/depth/color/points`
- `/camera/depth/scan`

---

## B) Launch ORB-SLAM3 (orbslam3 repo / container)

Inside your ORB-SLAM3 environment:

```bash
ros2 launch orb_slam3_ros2_wrapper maxwell_sim_rover.launch.py
```

The launch now uses `rover-maxwell-rgbd-imu-ros-params.yaml`, which maps topics to Maxwell sim and keeps TF publishing disabled so EKF owns `map -> odom`.

---

## C) Quick checks

```bash
ros2 topic echo /robot/robot_pose_slam --once
ros2 topic echo /odometry/local --once
ros2 topic echo /odometry/global --once
ros2 topic echo /camera/depth/scan --once
ros2 run tf2_tools view_frames
```

Expected TF tree core:

- `map -> odom` (global EKF)
- `odom -> base_footprint` (local EKF)
- `base_footprint -> Base_link` (URDF fixed joint)

---

## D) Nav2 costmap inputs

For local/global costmaps, use one (or both):

- `/camera/depth/color/points` for 3D obstacle layers
- `/camera/depth/scan` for 2D obstacle layers

Do **not** use ORB-SLAM3 sparse map points for obstacle inflation/collision checking.
