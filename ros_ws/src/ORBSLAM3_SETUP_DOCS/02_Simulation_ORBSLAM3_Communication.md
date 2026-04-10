# 02 - Communication between local simulation and ORB-SLAM3 Docker

This guide explains how to make ROS 2 topics visible between:

- your **local Mars rover simulation** (host machine), and
- the **ORB-SLAM3 Docker container**.

Your Docker setup already uses `network_mode: host`, so DDS discovery happens directly on the host network stack.

---

## 1) Use matching ROS 2 middleware settings on both sides

Use the same values on host and container:

```bash
export ROS_DOMAIN_ID=55
export ROS_LOCALHOST_ONLY=0
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

The ORB-SLAM3 container already uses these values from:

- `ros_env_vars.sh`

---

## 2) Create CycloneDDS config on your host machine

Create this file on your host:

`~/.ros/cyclonedds.xml`

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<CycloneDDS xmlns="https://cdds.io/config" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <Domain id="any">
    <General>
      <NetworkInterfaceAddress>auto</NetworkInterfaceAddress>
      <AllowMulticast>false</AllowMulticast>
    </General>
    <Discovery>
      <ParticipantIndex>auto</ParticipantIndex>
      <MaxAutoParticipantIndex>100</MaxAutoParticipantIndex>
      <Peers>
        <Peer Address="localhost" />
      </Peers>
    </Discovery>
  </Domain>
</CycloneDDS>
```

This matches the container config used at `/root/.ros/cyclonedds.xml`.

---

## 3) Export CYCLONEDDS URI correctly on host vs container

Container uses:

```bash
export CYCLONEDDS_URI=/root/.ros/cyclonedds.xml
```

Host must use:

```bash
export CYCLONEDDS_URI=$HOME/.ros/cyclonedds.xml
```

Do **not** use `/root/.ros/...` on host.

---

## 4) Add host exports to your ~/.bashrc

Append this block to host `~/.bashrc`:

```bash
export ROS_DOMAIN_ID=55
export ROS_LOCALHOST_ONLY=0
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI=$HOME/.ros/cyclonedds.xml
```

Then reload:

```bash
source ~/.bashrc
```

---

## 5) Verification flow

1. Start the Mars rover simulation locally.
2. Open a new host terminal and verify camera topics exist.
3. Start ORB-SLAM3 container and run `ros2 topic list` inside it.
4. Confirm both sides see the same camera topics.

Quick check command:

```bash
ros2 topic list | grep camera
```

---

## 6) If discovery still fails

- Re-check `ROS_DOMAIN_ID` on both host and container.
- Re-check `RMW_IMPLEMENTATION` on both host and container.
- Re-check `CYCLONEDDS_URI` path (host vs container path must differ).
- Restart terminals after updating `~/.bashrc`.
- Restart Docker container after changing DDS-related env vars.

Optional fallback (if network discovery is restrictive): set `AllowMulticast` to `true` on both host and container Cyclone files.
