import pybullet as p
import pybullet_data
import numpy as np
import time

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

# Mixer matrix: roll, pitch, yaw torques to motor PWMs (simplified)
mixing_matrix = np.array([
    [1, -1, 1],  # Motor 1 (Front Right, CCW)
    [1, 1, -1],  # Motor 2 (Front Left, CW)
    [1, -1, -1],  # Motor 3 (Rear Left, CW)
    [1, 1, 1],  # Motor 4 (Rear Right, CCW)
])

# Scale the mixing matrix to produce reasonable PWM outputs
mixing_matrix = mixing_matrix * 50  # Adjusted scaling factor for PWM output

# ----- Initialize PyBullet ----- #
p.connect(p.GUI)
p.setGravity(0, 0, gravity)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.loadURDF("plane.urdf")  # Add this to have a ground plane
start_pos = [0, 0, 1]
start_orientation = p.getQuaternionFromEuler([0, 0, 0])
drone = p.loadURDF("quadrotor.urdf", start_pos, start_orientation, useFixedBase=False)

# ----- PID Controller ----- #
kp, ki, kd = 0.5, 0.1, 0.05  # Increased gains for better responsiveness
integral_error = np.zeros(3)
prev_error = np.zeros(3)


def pid_controller(w_desired, w_actual, dt):
    global integral_error, prev_error
    error = w_desired - w_actual
    integral_error += error * dt
    # Anti-windup: Limit the integral term
    integral_error = np.clip(integral_error, -10, 10)
    derivative = (error - prev_error) / dt
    prev_error = error
    return kp * error + ki * integral_error + kd * derivative


# ----- Main Simulation Loop ----- #
dt = 1. / 240.
w_desired = np.array([0.5, 0.0, 0.0])  # Desired angular velocity (roll, pitch, yaw)

# For debugging
debug_lines = [None, None, None, None]
debug_text = p.addUserDebugText("", [0, 0, 0], textColorRGB=[1, 1, 1])
hover_pwm = 1200  # Approximate PWM value for hovering

for _ in range(10000):
    # Get orientation and angular velocity
    pos, ori = p.getBasePositionAndOrientation(drone)
    linear_vel, ang_vel_world = p.getBaseVelocity(drone)

    rot_mat = np.array(p.getMatrixFromQuaternion(ori)).reshape(3, 3)
    ang_vel = rot_mat.T @ np.array(ang_vel_world)  # World to body frame conversion

    # Update debug text
    text = f"Ang Vel: [{ang_vel[0]:.2f}, {ang_vel[1]:.2f}, {ang_vel[2]:.2f}]"
    p.removeUserDebugItem(debug_text)
    debug_text = p.addUserDebugText(text, [pos[0], pos[1], pos[2] + 0.3], textColorRGB=[1, 1, 1])

    # Run PID controller
    control_output = pid_controller(w_desired, ang_vel, dt)  # outputs: torque demands
    print(f"Angular Velocity: {ang_vel}, Desired: {w_desired}, Control Output: {control_output}")
    # Motor mixing (outputs PWM values directly)
    control_effect = mixing_matrix @ control_output
    motor_pwms = np.array([hover_pwm + control_effect[i] * 50 for i in range(4)])
    motor_pwms = np.clip(motor_pwms, pwm_min, pwm_max)
    print(f"Control Effect: {control_effect}, Motor PWMs: {motor_pwms}")

    # Apply first-order filter for motor dynamics (filter the PWM values)
    filtered_pwms = np.zeros(4)
    for i in range(4):
        alpha = dt / (motor_time_constant + dt)
        filtered_pwms[i] = (1 - alpha) * previous_motor_outputs[i] + alpha * motor_pwms[i]
        previous_motor_outputs[i] = filtered_pwms[i]

    # Convert filtered PWMs to thrusts
    actual_thrusts = np.array([pwm_to_thrust(pwm) for pwm in filtered_pwms])

    # Apply forces at motor positions
    for i, thrust in enumerate(actual_thrusts):
        pos_world = motor_dirs[i]
        force = [0, 0, thrust]
        p.applyExternalForce(objectUniqueId=drone,
                             linkIndex=-1,
                             forceObj=force,
                             posObj=pos_world,
                             flags=p.LINK_FRAME)

        # Visualize thrust as debug lines (optional)
        if debug_lines[i] is not None:
            p.removeUserDebugItem(debug_lines[i])
        start = np.array(pos) + p.rotateVector(ori, pos_world)
        end = start + p.rotateVector(ori, [0, 0, thrust * 0.01])
        debug_lines[i] = p.addUserDebugLine(start, end, [1, 0, 0], 2)
    print(f"Motor PWMs: {motor_pwms}, Thrusts: {actual_thrusts}")
    p.stepSimulation()
    time.sleep(dt)

p.disconnect()