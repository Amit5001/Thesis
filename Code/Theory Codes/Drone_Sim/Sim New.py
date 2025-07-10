import pybullet as p
import pybullet_data
import numpy as np
import time
import matplotlib.pyplot as plt  # Add matplotlib for plotting

# ----- Constants and Parameters ----- #
pwm_min = 1000
pwm_max = 2000
previous_motor_outputs = np.zeros(4)  # Store previous motor outputs
motor_time_constant = 0.3  # Time constant from your transfer function (0.3s)


def pwm_to_thrust(pwm):
    """Convert PWM to thrust in Newtons (using corrected quadratic model)."""
    return 2.37e-5 * pwm ** 2 - 4.71e-2 * pwm + 23.58


# Drone physical parameters
arm_length = 0.1  # meters
mass = 1.0  # kg
gravity = -9.81

# Motor layout and directions (X configuration)
motor_dirs = [
    np.array([arm_length, arm_length, 0]),  # Front Right (CCW)
    np.array([-arm_length, arm_length, 0]),  # Front Left  (CW)
    np.array([-arm_length, -arm_length, 0]),  # Rear Left   (CW)
    np.array([arm_length, -arm_length, 0]),  # Rear Right  (CCW)
]

# ----- Initialize PyBullet ----- #
p.connect(p.GUI)
p.setGravity(0, 0, gravity)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.loadURDF("plane.urdf")
start_pos = [0, 0, 1]
start_orientation = p.getQuaternionFromEuler([0, 0, 0])
drone = p.loadURDF("quadrotor.urdf", start_pos, start_orientation, useFixedBase=False)

# Optimize physics for speed
p.setPhysicsEngineParameter(numSolverIterations=5)
p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS, 0)

# ----- PID Controller ----- #
kp, ki, kd = 3, 0.0, 0.00  # Adjusted gains
integral_error = np.zeros(3)
prev_error = np.zeros(3)


def pid_controller(w_desired, w_actual, dt):
    global integral_error, prev_error
    error = w_desired - w_actual
    integral_error += error * dt
    integral_error = np.clip(integral_error, -1, 1)
    derivative = (error - prev_error) / dt
    prev_error = error
    return -(kp * error + ki * integral_error + kd * derivative)


# ----- Main Simulation Loop ----- #
dt = 1. / 833.
w_desired = np.array([0.0, 0.5, 0.0])  # Only roll for testing

# For debugging
debug_lines = [None, None, None, None]
debug_text = p.addUserDebugText("", [0, 0, 0], textColorRGB=[1, 1, 1])
hover_pwm = 1300  # Base hover PWM

# Initialize motors at hover PWM
previous_motor_outputs = np.ones(4) * hover_pwm

# Control scaling factors
roll_scale = 1.0
pitch_scale = 1.0
yaw_scale = 1.0

# Speed optimization parameters
vis_update_freq = 20  # Update visualization every N iterations
print_freq = 50  # Print debug info every N iterations
steps_per_iter = 2  # Physics steps per iteration
real_time_factor = 4.0  # Run faster than real-time

# Data collection for plotting
max_iterations = 2000  # Set max iterations to limit simulation time
time_points = []
roll_velocity = []
pitch_velocity = []
yaw_velocity = []
desired_roll = []
desired_pitch = []
desired_yaw = []

for iteration in range(max_iterations):
    # Record time point
    time_points.append(iteration * dt)

    # Get orientation and angular velocity
    pos, ori = p.getBasePositionAndOrientation(drone)
    linear_vel, ang_vel_world = p.getBaseVelocity(drone)

    # Convert to body frame
    rot_mat = np.array(p.getMatrixFromQuaternion(ori)).reshape(3, 3)
    ang_vel_body = rot_mat.T @ np.array(ang_vel_world)
    ang_vel = np.array([ang_vel_body[1], ang_vel_body[0], ang_vel_body[2]])

    # Record angular velocity for plotting
    roll_velocity.append(ang_vel[0])
    pitch_velocity.append(ang_vel[1])
    yaw_velocity.append(ang_vel[2])
    desired_roll.append(w_desired[0])
    desired_pitch.append(w_desired[1])
    desired_yaw.append(w_desired[2])

    # Update debug text (less frequently)
    if iteration % vis_update_freq == 0:
        text = f"Ang Vel: [{ang_vel[0]:.2f}, {ang_vel[1]:.2f}, {ang_vel[2]:.2f}]"
        p.removeUserDebugItem(debug_text)
        debug_text = p.addUserDebugText(text, [pos[0], pos[1], pos[2] + 0.3], textColorRGB=[1, 1, 1])

    # Run PID controller to get control output
    control_output = pid_controller(w_desired, ang_vel, dt)
    roll_cmd, pitch_cmd, yaw_cmd = control_output

    # Calculate motor PWMs (vectorized approach)
    motor_pwms = np.ones(4) * hover_pwm

    # Apply roll, pitch, yaw commands
    roll_effect = np.array([-1, 1, 1, -1]) * roll_cmd * roll_scale
    pitch_effect = np.array([-1, -1, 1, 1]) * pitch_cmd * pitch_scale
    yaw_effect = np.array([1, -1, -1, 1]) * yaw_cmd * yaw_scale

    motor_pwms += roll_effect + pitch_effect + yaw_effect
    motor_pwms = np.clip(motor_pwms, pwm_min, pwm_max)

    # Apply first-order filter (vectorized)
    alpha = dt / (motor_time_constant + dt)
    filtered_pwms = (1 - alpha) * previous_motor_outputs + alpha * motor_pwms
    previous_motor_outputs = filtered_pwms.copy()

    # Calculate thrusts (vectorized)
    actual_thrusts = 2.37e-5 * filtered_pwms ** 2 - 4.71e-2 * filtered_pwms + 23.58

    # Print debug info (less frequently)
    if iteration % print_freq == 0:
        print(f"Iteration {iteration}")
        print(f"Angular Velocity: {ang_vel}")
        print(f"Control Output: [{roll_cmd:.4f}, {pitch_cmd:.4f}, {yaw_cmd:.4f}]")
        print(f"Motor PWMs: {motor_pwms}")
        print(f"Thrusts: {actual_thrusts}")
        print("-" * 50)

    # Apply forces at motor positions
    for i, thrust in enumerate(actual_thrusts):
        pos_world = motor_dirs[i]
        force = [0, 0, thrust]
        p.applyExternalForce(objectUniqueId=drone,
                             linkIndex=-1,
                             forceObj=force,
                             posObj=pos_world,
                             flags=p.LINK_FRAME)

    # Visualize thrust as debug lines (less frequently)
    if iteration % vis_update_freq == 0:
        for i, thrust in enumerate(actual_thrusts):
            if debug_lines[i] is not None:
                p.removeUserDebugItem(debug_lines[i])
            start = np.array(pos) + p.rotateVector(ori, motor_dirs[i])
            end = start + p.rotateVector(ori, [0, 0, thrust * 0.01])
            debug_lines[i] = p.addUserDebugLine(start, end, [1, 0, 0], 2)

    # Run multiple simulation steps per iteration
    for _ in range(steps_per_iter):
        p.stepSimulation()

    # Sleep less for faster than real-time simulation
    time.sleep(dt / real_time_factor)  # Comment out completely for maximum speed

p.disconnect()

# Create plots after simulation is complete
plt.figure(figsize=(12, 8))

# Plot angular velocities
plt.subplot(3, 1, 1)
plt.plot(time_points, roll_velocity, 'r-', label='Roll Velocity')
plt.plot(time_points, desired_roll, 'r--', label='Desired Roll')
plt.ylabel('Roll Rate (rad/s)')
plt.grid(True)
plt.legend()
plt.title('Drone Angular Velocity vs Time')

plt.subplot(3, 1, 2)
plt.plot(time_points, pitch_velocity, 'g-', label='Pitch Velocity')
plt.plot(time_points, desired_pitch, 'g--', label='Desired Pitch')
plt.ylabel('Pitch Rate (rad/s)')
plt.grid(True)
plt.legend()

plt.subplot(3, 1, 3)
plt.plot(time_points, yaw_velocity, 'b-', label='Yaw Velocity')
plt.plot(time_points, desired_yaw, 'b--', label='Desired Yaw')
plt.xlabel('Time (s)')
plt.ylabel('Yaw Rate (rad/s)')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.savefig('drone_angular_velocity.png')  # Save the plot to a file
plt.show()  # Display the plot