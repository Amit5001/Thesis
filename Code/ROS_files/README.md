After updates:
1. rebuild using - colcon build --cmake-args -DPython3_EXECUTABLE=/opt/anaconda3/envs/ros2/bin/python3
2. source the project - source install/setup.zsh

If there are errors try to remove old libraries and clean the workspace:
  rm -f /opt/anaconda3/envs/ros2/lib/libdrone_c__*.dylib
  rm -rf build/ install/ log/

### In order to run plotjuggler and the app:
ros2 launch drone_c drone_launch.launch.py plotjuggler:=true

In order to start rosbag recording- 
ros2 bag record -a