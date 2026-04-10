from setuptools import setup
import os
from glob import glob

package_name = 'maxwell_gazebo'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.xacro')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'config'), glob('config/*.rviz')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.world')),
        # Media materials
        (os.path.join('share', package_name, 'media/materials/scripts'), 
            glob('media/materials/scripts/*')),
        (os.path.join('share', package_name, 'media/materials/textures'), 
            glob('media/materials/textures/*')),
        # Marsyard2020 terrain model
        (os.path.join('share', package_name, 'models/marsyard2020_terrain'), 
            glob('models/marsyard2020_terrain/*.sdf') + glob('models/marsyard2020_terrain/*.config')),
        (os.path.join('share', package_name, 'models/marsyard2020_terrain/meshes'), 
            glob('models/marsyard2020_terrain/meshes/*.obj') + glob('models/marsyard2020_terrain/meshes/*.mtl')),
        (os.path.join('share', package_name, 'models/marsyard2020_terrain/meshes/textures'), 
            glob('models/marsyard2020_terrain/meshes/textures/*')),
        # Marsyard2021 terrain model
        (os.path.join('share', package_name, 'models/marsyard2021_terrain'), 
            glob('models/marsyard2021_terrain/*.sdf') + glob('models/marsyard2021_terrain/*.config')),
        (os.path.join('share', package_name, 'models/marsyard2021_terrain/dem'), 
            glob('models/marsyard2021_terrain/dem/*')),
        (os.path.join('share', package_name, 'models/marsyard2021_terrain/meshes'), 
            glob('models/marsyard2021_terrain/meshes/*.obj') + glob('models/marsyard2021_terrain/meshes/*.mtl')),
        (os.path.join('share', package_name, 'models/marsyard2021_terrain/meshes/textures'), 
            glob('models/marsyard2021_terrain/meshes/textures/*')),
        # Marsyard2022 terrain model
        (os.path.join('share', package_name, 'models/marsyard2022_terrain'), 
            glob('models/marsyard2022_terrain/*.sdf') + glob('models/marsyard2022_terrain/*.config')),
        (os.path.join('share', package_name, 'models/marsyard2022_terrain/dem'), 
            glob('models/marsyard2022_terrain/dem/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Maxwell Team',
    maintainer_email='rover@example.com',
    description='Gazebo simulation for Maxwell rover with swerve drive',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'swerve_sim_bridge = maxwell_gazebo.swerve_sim_bridge:main',
            'wheel_odometry = maxwell_gazebo.wheel_odometry:main',
        ],
    },
)
