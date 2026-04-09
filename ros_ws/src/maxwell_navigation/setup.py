from setuptools import find_packages, setup

package_name = 'maxwell_navigation'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch',
            ['launch/maxwell_navigation.launch.py']),
        ('share/' + package_name + '/config',
            ['config/nav2_params.yaml',
             'config/nav2_controllers.yaml',
             'config/maxwell_navigation_rviz2.rviz']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Maxwell Team',
    maintainer_email='rover@example.com',
    description='Nav2 autonomous navigation for Maxwell rover',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={},
)
