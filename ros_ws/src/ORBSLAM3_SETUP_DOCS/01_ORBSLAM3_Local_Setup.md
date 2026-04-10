# 01 - ORB-SLAM3 local setup (first-time user)

This guide explains how to set up and run your ORB-SLAM3 Docker environment on a local Linux machine.

## Prerequisites

- Ubuntu 22.04 (recommended)
- Docker and Docker Compose
- Git
- X11 desktop session (for ORB-SLAM3 viewer window)

---

## 1) Clone the repository and submodules

```bash
git clone https://github.com/nickoenig37/ORB-SLAM3-ROS2-MONO-Docker.git
cd ORB-SLAM3-ROS2-MONO-Docker
git submodule update --init --recursive --remote
```

---

## 2) Install Docker (if needed)

Use the included installer script:

```bash
cd /path/to/rover_simulation/ORB-SLAM3-ROS2-MONO-Docker
chmod +x container_root/shell_scripts/docker_install.sh
./container_root/shell_scripts/docker_install.sh
```

If Docker is already installed, skip this step.

---

## 3) Enable GUI forwarding from container to host

The ORB-SLAM3 viewer needs X11 access:

```bash
echo "xhost +" >> ~/.bashrc
source ~/.bashrc
```

> Note: `xhost +` is broad access. For stricter security, replace with a narrower X11 permission rule.

---

## 4) Build the ORB-SLAM3 image

From the ORB-SLAM3 Docker folder:

```bash
docker build --build-arg USE_CI=false -t orb-slam3-humble:22.04 .
```

Confirm image exists:

```bash
docker images | grep orb-slam3-humble
```

---

## 5) Start the container

```bash
cd /path/to/rover_simulation/ORB-SLAM3-ROS2-MONO-Docker
docker compose run orb_slam3_22_humble
```

You should now be inside the container shell.

Quick GUI test:

```bash
xeyes
```

If the window appears, GUI forwarding is working.

---

## 6) Build ORB-SLAM3 and ROS 2 wrapper (inside container)

```bash
cd /home/orb/ORB_SLAM3
chmod +x build.sh
./build.sh

cd /root/colcon_ws
colcon build --symlink-install
source install/setup.bash
```

---

## 7) Launch ORB-SLAM3 (inside container)

```bash
ros2 launch orb_slam3_ros2_wrapper maxwell_sim_rover.launch.py
```

If image topics are available, the ORB-SLAM3 viewer will start tracking.

---

## Useful checks

Inside the container:

```bash
printenv | grep -E 'ROS_DOMAIN_ID|RMW_IMPLEMENTATION|CYCLONEDDS_URI|ROS_LOCALHOST_ONLY'
ros2 topic list
```

If camera topics are not visible, use the communication guide in [02_Simulation_ORBSLAM3_Communication.md](02_Simulation_ORBSLAM3_Communication.md).
