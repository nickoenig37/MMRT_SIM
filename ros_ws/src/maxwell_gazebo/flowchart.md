---
config:
  layout: fixed
---
flowchart TB
 subgraph subGraph0["Simulation & Data Acquisition (ROS2 Humble Gazebo 11 Simulation)"]
        B("ROS 2 Bridge")
        A["D435 Camera: RGB-D / Stereo"]
        IMU["IMU Sensor"]
        SimTime["Sim Clock"]
  end
 subgraph subGraph1["Perception Layer (ORB-SLAM3 [DOCKER CONTAINER])"]
        C{"ORB-SLAM3 Engine"}
        D["TF Tree"]
        E["Feature Map"]
  end
 subgraph subGraph2["Environmental Modeling"]
        F["Depth to LaserScan / PointCloud2"]
        G["Nav2 Costmap Server"]
        MapSvr["Map Server"]
  end
 subgraph subGraph3["Navigation Stack (Nav2)"]
        H["BT Navigator"]
        I["Global Planner"]
        J["Local Controller"]
        Recovery["Recovery Server"]
  end
 subgraph Actuation["Actuation"]
        K["Rover Differential Drive Plugin"]
  end
    A -- raw images --> B
    IMU -- angular vel / linear accel --> B
    SimTime --> B
    B -- /camera/image_raw --> C
    B -- /imu/data --> C
    C -- Transform: map to odom --> D
    C -- Transform: odom to base_link --> D
    C -- Sparse Point Cloud --> E
    B -- Depth Image --> F
    F -- /scan --> G
    E -- Manual/Heuristic Projection --> G
    MapSvr -- Static Map --> G
    G --> H
    H -- Action Call --> I & J
    I -- Global Path --> J
    J -- Obstacle Avoidance --> Recovery
    Recovery -- Clear Costmaps/Spin --> H
    J -- cmd_vel --> K
    K -- Physics Feedback --> A

    style subGraph1 fill:#BBDEFB
    style subGraph0 fill:#E1BEE7
    style subGraph2 fill:#C8E6C9
    style subGraph3 fill:#C8E6C9