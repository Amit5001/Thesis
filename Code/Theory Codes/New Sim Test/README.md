This is implementation of a simulation for my thesis drone based on the original `gym-pybullet-drones` repository, which is designed to be compatible with `gymnasium`, `stable-baselines3`, and SITL `betaflight`/`crazyflie-firmware`.

First, an implementation of the INDI controller is created to control the drone's angular velocity and position.

The simulation is based on the environment of CtrlAviary.

### The CtrlAviary is the most suited environment because:
1. Motor dynamics included: BaseAviary (which CtrlAviary inherits from) implements motor delay and advanced ESC modeling gym-pybullet-drones/gym_pybullet_drones/envs/VelocityAviary.py at master · utiasDSL/gym-pybullet-drones
2. Direct motor control: You send RPM commands directly, which is perfect for INDI's incremental motor commands
3. High control frequency: Supports high-frequency control loops (240Hz default, configurable higher)
4. Raw state access: No preprocessing of angular velocities/positions - you get the actual dynamics
5. No interference: No built-in controllers or reward functions to interfere with your INDI implementation

It is possible to use BaseAviary in order to achieve more customization.

