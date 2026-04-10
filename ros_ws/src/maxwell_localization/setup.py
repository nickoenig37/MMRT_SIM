from setuptools import find_packages, setup

package_name = 'maxwell_localization'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch',
            ['launch/maxwell_localization.launch.py']),
        ('share/' + package_name + '/config',
            ['config/ekf_localization.yaml',
             'config/maxwell_localization_rviz2.rviz']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Maxwell Team',
    maintainer_email='rover@example.com',
    description='EKF localization stack for Maxwell rover',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'wheel_odometry = maxwell_localization.wheel_odometry:main',
            'slam_pose_bridge = maxwell_localization.slam_pose_bridge:main',
        ],
    },
)
