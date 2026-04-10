# 03 - Launch ORB-SLAM3 and map topic names for Maxwell Mars simulation

This guide covers:

1. what to launch,
2. what topic names must match,
3. what to edit when ORB-SLAM3 is not receiving images.

---

## A) Launch order

### 1) Start simulation on host

From your ROS 2 workspace, launch the Mars world simulation first.

Example:

```bash
ros2 launch maxwell_gazebo maxwell_sim.launch.py world:=marsyard2020
```

### 2) Start ORB-SLAM3 container

```bash
cd /___/ORB-SLAM3-ROS2-MONO-Docker
docker compose run orb_slam3_22_humble
```
- Also can get the docker extension from VSCode and start the container from there

### 3) Inside container, launch ORB-SLAM3

```bash
cd ~/colcon_ws
ros2 launch orb_slam3_ros2_wrapper unirobot.launch.py
```

---

## B) Camera topic names that must match

Maxwell Gazebo camera plugin publishes:

- `camera/color/image_raw`
- `camera/depth/image_raw`

The ORB-SLAM3 wrapper uses parameters:

- `rgb_image_topic_name`
- `depth_image_topic_name`

If these do not match, ORB-SLAM3 will open but not track.

---

## C) What to edit for Maxwell

Edit:

- `orb_slam3_ros2_wrapper/params/rgbd-ros-params.yaml`

Set:

```yaml
rgb_image_topic_name: camera/color/image_raw
depth_image_topic_name: camera/depth/image_raw
```

If you use namespaces, add leading `/` to force global topics:

```yaml
rgb_image_topic_name: /camera/color/image_raw
depth_image_topic_name: /camera/depth/image_raw
```

> The wrapper comments already note this behavior: leading `/` avoids namespacing side-effects.

---

## D) Validate before launching SLAM

Inside container:

```bash
ros2 topic list | grep -E 'camera/color/image_raw|camera/depth/image_raw'
```

If missing, fix communication first (see [02_Simulation_ORBSLAM3_Communication.md](02_Simulation_ORBSLAM3_Communication.md)).

You can also inspect frequency:

```bash
ros2 topic hz /camera/color/image_raw
ros2 topic hz /camera/depth/image_raw
```

---

## E) Optional launch path

Instead of launching `unirobot.launch.py`, you can launch RGB-D directly from the helper script in container:

```bash
/root/shell_scripts/launch_orb.sh
```

This runs:

```bash
ros2 launch orb_slam3_ros2_wrapper rgbd.launch.py
```

---

## F) Other parameters you may need to tune

In `rgbd-ros-params.yaml`:

- `robot_base_frame` (default `base_footprint`)
- `global_frame` (default `map`)
- `odom_frame` (default `odom`)
- `visualization` (`true` to show ORB-SLAM3 viewer)
- `publish_tf`

For Maxwell, `base_footprint` exists in the rover URDF, so default frame settings are valid.

---

## G) Common failure modes

- **No SLAM motion / frozen viewer**: wrong RGB/depth topic names.
- **No topics inside container**: DDS env mismatch (`ROS_DOMAIN_ID`, Cyclone config, or `CYCLONEDDS_URI`).
- **Window does not appear**: X11 forwarding not set (`xhost +`).
- **Runs but poor tracking**: camera parameters in `gazebo_rgbd.yaml` may need calibration updates.
