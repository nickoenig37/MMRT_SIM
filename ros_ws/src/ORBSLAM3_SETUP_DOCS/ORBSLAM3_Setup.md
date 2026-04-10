# ORB-SLAM3 + Maxwell Mars Simulation Setup Docs

Use these documents in order:

1. [01_ORBSLAM3_Local_Setup.md](01_ORBSLAM3_Local_Setup.md)
2. [02_Simulation_ORBSLAM3_Communication.md](02_Simulation_ORBSLAM3_Communication.md)
3. [03_Launch_ORBSLAM3_and_Topic_Mapping.md](03_Launch_ORBSLAM3_and_Topic_Mapping.md)
4. [04_Maxwell_Autonomy_Pipeline.md](04_Maxwell_Autonomy_Pipeline.md)

## Quick intent of each file

- **01**: First-time local setup (Docker, image build, container run, ORB-SLAM3 build).
- **02**: ROS 2 DDS communication setup between local simulation and container, including CycloneDDS config.
- **03**: Launch steps and topic/remap adjustments needed for Maxwell camera topics.
- **04**: Split localization/obstacle pipeline, EKF fusion, and TF ownership for autonomy.
