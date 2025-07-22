import sys
if sys.prefix == '/opt/anaconda3/envs/ThesisRos':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/Users/amitgedj/Library/CloudStorage/OneDrive-Personal/University/MsC/Thesis/Code/ROS_files/install/drone_tuner'
