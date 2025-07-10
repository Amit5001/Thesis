import pybullet as p
import pybullet_data
import numpy as np
import time
import matplotlib.pyplot as plt  # Add matplotlib for plotting

# Import the RadiomasterController class
from Read_Controller import RadiomasterController

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

# Motor layout and directions (X configuration, matching the image)
# Motor numbering from the image:
# Motor 1 (A): Front-right, CCW
# Motor 2 (C): Back-left, CCW
# Motor 3 (D): Front-left, CW
# Motor 4 (B): Back-right, CW
motor_dirs = [
    np.array([arm_length, arm_length, 0]),  # Motor 1 (A): Front-right (CCW)
    np.array([-arm_length, -arm_length, 0]),  # Motor 2 (C): Back-left (CCW)
    np.array([-arm_length, arm_length, 0]),  # Motor 3 (D): Front-left (CW)
    np.array([arm_length, -arm_length, 0]),  # Motor 4 (B): Back-right (CW)
]

# Motor rotation directions (1 for CCW, -1 for CW)
motor_rotation_dir = [1, 1, -1, -1]  # 1, 2 are CCW; 3, 4 are CW


# ----- Initialize Radio Controller ----- #
try:
    # Initialize controller
    rc = RadiomasterController()
    controller_connected = True
    print(f"Controller connected: {rc.get_controller_info()['name']}")
except Exception as e:
    controller_connected = False
    print(f"Could not initialize controller: {e}")
    print("Running simulation with default values.")

# Base hover PWM
base_hover_pwm = 1300

# ----- Initialize PyBullet ----- #
p.connect(p.GUI)
p.setGravity(0, 0, gravity)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.loadURDF("plane.urdf")
start_pos = [0, 0, 1]
# No rotation needed - we'll use the drone's natural orientation and control correctly for X config
start_orientation = p.getQuaternionFromEuler([0, 0, 0])
drone = p.loadURDF("quadrotor_x_config.urdf", start_pos, start_orientation, useFixedBase=False)

# Create visual indicators for motor positions and rotation
motor_visuals = []
motor_colors = [[0, 0, 1, 0.8], [0, 0, 1, 0.8], [0, 1, 0, 0.8], [0, 1, 0, 0.8]]  # Blue for CCW, Green for CW


def update_motor_visuals(position, orientation):
    """Update visual indicators for motors to help understand the configuration."""
    global motor_visuals

    # Clear previous visuals
    for visual in motor_visuals:
        if visual is not None:
            p.removeUserDebugItem(visual)

    motor_visuals = []

    # Create sphere at each motor position and line showing rotation direction
    for i, motor_pos in enumerate(motor_dirs):
        # Transform motor position from local to world coordinates
        pos_world = np.array(position) + p.rotateVector(orientation, motor_pos)

        # Create motor position indicator (small sphere)
        visual_id = p.addUserDebugText(
            text=str(i + 1),  # Motor number
            textPosition=pos_world,
            textColorRGB=motor_colors[i][:3],
            textSize=1.5
        )
        motor_visuals.append(visual_id)

        # Create a line showing rotation direction
        rot_dir = motor_rotation_dir[i]
        start = pos_world

        # Calculate end point for rotation indicator
        radius = 0.03
        if i == 0:  # Front-right
            angle = np.pi / 4 if rot_dir > 0 else 5 * np.pi / 4
        elif i == 1:  # Back-left
            angle = 5 * np.pi / 4 if rot_dir > 0 else np.pi / 4
        elif i == 2:  # Front-left
            angle = 3 * np.pi / 4 if rot_dir > 0 else 7 * np.pi / 4
        else:  # Back-right
            angle = 7 * np.pi / 4 if rot_dir > 0 else 3 * np.pi / 4

        end = pos_world + np.array([radius * np.cos(angle), radius * np.sin(angle), 0])

        line_id = p.addUserDebugLine(
            start,
            end,
            lineColorRGB=motor_colors[i][:3],
            lineWidth=2.0
        )
        motor_visuals.append(line_id)


# Function to calculate camera yaw from drone orientation
def get_camera_heading_yaw(orientation):
    """
    Calculate camera yaw to align with drone's heading direction.
    This makes the camera point in the same direction as the drone is facing.
    """
    # Front direction vector (X-axis in drone's local frame)
    front_dir = np.array([1.0, 0.0, 0.0])

    # Rotate to world frame
    front_dir_world = p.rotateVector(orientation, front_dir)

    # Calculate yaw angle from the rotated vector (in XY plane)
    # atan2(y, x) gives us the angle in radians
    heading_yaw = np.degrees(np.arctan2(front_dir_world[1], front_dir_world[0]))

    return heading_yaw


# Add keyboard handler information
print("Controls:")
print("  Press 'r' to reset the simulation")
print("  Press 'c' to reset camera position")
print("  Press 'f' to toggle camera following")
print("  Press 'h' to toggle heading-aligned camera (first-person view)")
print("  Press '+'/'-' to adjust camera distance")
print("  Use arrow keys to adjust camera angle")
print("  Press 'q' to quit the simulation")

# Initialize the motor visuals
update_motor_visuals(start_pos, start_orientation)


def reset_simulation():
    """Reset the drone to starting position with zero velocity."""
    global integral_error, prev_error, previous_motor_outputs, hover_pwm

    # Reset drone position and orientation
    p.resetBasePositionAndOrientation(drone, start_pos, start_orientation)

    # Reset drone velocity (linear and angular)
    p.resetBaseVelocity(drone, linearVelocity=[0, 0, 0], angularVelocity=[0, 0, 0])

    # Reset controller variables
    integral_error = np.zeros(3)
    prev_error = np.zeros(3)

    # Reset motor outputs
    previous_motor_outputs = np.ones(4) * base_hover_pwm
    hover_pwm = base_hover_pwm

    # Update motor visuals after reset
    update_motor_visuals(start_pos, start_orientation)

    print("Simulation reset - drone position and state restored to initial values")


def keyboardCallback(keyCode):
    global follow_drone, camera_distance, camera_yaw, camera_pitch, align_camera_with_heading

    # Reset simulation with 'r' key
    if keyCode == ord('r'):
        reset_simulation()

    # Toggle camera following with 'f' key
    elif keyCode == ord('f'):
        follow_drone = not follow_drone
        print(f"Camera following: {'ON' if follow_drone else 'OFF'}")

    # Toggle camera alignment with heading with 'h' key
    elif keyCode == ord('h'):
        align_camera_with_heading = not align_camera_with_heading
        print(f"Camera aligned with heading: {'ON' if align_camera_with_heading else 'OFF'}")

    # Reset camera with 'c' key
    elif keyCode == ord('c'):
        camera_distance = 2.0
        camera_yaw = 45.0
        camera_pitch = -30.0
        print("Camera reset")

    # Quit simulation with 'q' key
    elif keyCode == ord('q'):
        print("Quitting simulation...")
        return True  # Signal to quit

    # Adjust camera distance with '+' and '-' keys
    elif keyCode == ord('+'):
        camera_distance = max(0.5, camera_distance - 0.2)
    elif keyCode == ord('-'):
        camera_distance += 0.2

    # Adjust camera angle with arrow keys
    elif keyCode == p.B3G_LEFT_ARROW:
        camera_yaw += 5.0
    elif keyCode == p.B3G_RIGHT_ARROW:
        camera_yaw -= 5.0
    elif keyCode == p.B3G_UP_ARROW:
        camera_pitch = min(camera_pitch + 5.0, -5.0)
    elif keyCode == p.B3G_DOWN_ARROW:
        camera_pitch = max(camera_pitch - 5.0, -85.0)

    return False  # Continue simulation


p.setRealTimeSimulation(0)  # Disable real-time simulation to use stepSimulation
p.configureDebugVisualizer(p.COV_ENABLE_KEYBOARD_SHORTCUTS, 0)  # Disable default keyboard shortcuts

# Optimize physics for speed
p.setPhysicsEngineParameter(numSolverIterations=5)
p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS, 0)

# Set up camera to follow the drone
camera_distance = 2.0
camera_yaw = 45.0
camera_pitch = -30.0
p.resetDebugVisualizerCamera(camera_distance, camera_yaw, camera_pitch, start_pos)

# Add heading-aligned camera option
align_camera_with_heading = False

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
w_desired = np.array([0.0, 0.0, 0.0])  # Default rates if no controller
hover_pwm = base_hover_pwm  # Initialize at base hover PWM

# For debugging
debug_lines = [None, None, None, None]
debug_text = p.addUserDebugText("", [0, 0, 0], textColorRGB=[1, 1, 1])

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

# Camera parameters
camera_distance = 2.0
camera_yaw = 45.0
camera_pitch = -30.0
follow_drone = True  # Enable/disable camera following the drone
camera_update_freq = 1  # Update camera every N iterations

# Data collection for plotting
max_iterations = 5000  # Increased max iterations for controller input
time_points = []
roll_velocity = []
pitch_velocity = []
yaw_velocity = []
desired_roll = []
desired_pitch = []
desired_yaw = []
throttle_values = []

try:
    should_exit = False
    for iteration in range(max_iterations):
        # Check if we should exit the simulation
        if should_exit:
            break

        # Check for keyboard input
        keys = p.getKeyboardEvents()
        for key, state in keys.items():
            if state & p.KEY_WAS_TRIGGERED:
                should_exit = keyboardCallback(key)

        # Get controller input if connected
        if controller_connected:
            # Read and map gimbal values
            rc.read_gimbals()
            rc.map_gimbals_acro()

            # Convert from deg/s to rad/s for rates (roll, pitch, yaw)
            w_desired = np.array([
                np.radians(rc.map_acro[0]),  # Roll rate (deg/s -> rad/s)
                np.radians(rc.map_acro[1]),  # Pitch rate (deg/s -> rad/s)
                np.radians(rc.map_acro[3])  # Yaw rate (deg/s -> rad/s)
            ])

            # Update hover PWM based on throttle input
            hover_pwm = rc.map_acro[2]  # Throttle directly maps to PWM (1000-2000)
            throttle_values.append(hover_pwm)
        else:
            # Use default values if no controller
            w_desired = np.array([0.0, 0.0, 0.0])
            hover_pwm = base_hover_pwm
            throttle_values.append(hover_pwm)

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
            text = f"Ang Vel: [{ang_vel[0]:.2f}, {ang_vel[1]:.2f}, {ang_vel[2]:.2f}] Throttle: {hover_pwm:.0f}"
            p.removeUserDebugItem(debug_text)
            debug_text = p.addUserDebugText(text, [pos[0], pos[1], pos[2] + 0.3], textColorRGB=[1, 1, 1])

        # Run PID controller to get control output
        control_output = pid_controller(w_desired, ang_vel, dt)
        roll_cmd, pitch_cmd, yaw_cmd = control_output

        # Calculate motor PWMs (vectorized approach)
        motor_pwms = np.ones(4) * hover_pwm

        # Apply roll, pitch, yaw commands
        # For X configuration matching the image:
        # Motor numbering:
        # 3(D)   1(A)
        #   \   /
        #    \ /
        #    / \
        #   /   \
        # 2(C)   4(B)
        #
        # For roll (right wing down):
        # - Motors 1,4 decrease
        # - Motors 2,3 increase
        # For pitch (nose up):
        # - Motors 1,3 increase
        # - Motors 2,4 decrease
        # For yaw (clockwise, right):
        # - CCW motors (1,2) increase
        # - CW motors (3,4) decrease

        # Control mixer for X configuration
        roll_effect = np.array([-1, 1, 1, -1]) * roll_cmd * roll_scale
        pitch_effect = np.array([1, -1, 1, -1]) * pitch_cmd * pitch_scale
        yaw_effect = np.array([1, 1, -1, -1]) * yaw_cmd * yaw_scale  # Based on motor_rotation_dir

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
            print(f"Desired Rates: {w_desired}")
            print(f"Throttle/Hover PWM: {hover_pwm}")
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

        # Run multiple simulation steps per iteration
        for _ in range(steps_per_iter):
            p.stepSimulation()

        # Update camera position to follow the drone
        if follow_drone and iteration % camera_update_freq == 0:
            # If heading-aligned camera is enabled, calculate camera yaw from drone orientation
            if align_camera_with_heading:
                # Get the heading direction yaw angle
                heading_yaw = get_camera_heading_yaw(ori)

                # Set camera yaw to match drone's heading
                p.resetDebugVisualizerCamera(
                    cameraDistance=camera_distance,
                    cameraYaw=heading_yaw -90,  # Use drone's heading angle
                    cameraPitch=camera_pitch,
                    cameraTargetPosition=pos
                )
            else:
                # Use user-defined camera yaw
                p.resetDebugVisualizerCamera(
                    cameraDistance=camera_distance,
                    cameraYaw=camera_yaw -45,
                    cameraPitch=camera_pitch,
                    cameraTargetPosition=pos
                )

        # Update motor visuals to show configuration
        if iteration % vis_update_freq == 0:
            update_motor_visuals(pos, ori)

        # Sleep less for faster than real-time simulation
        time.sleep(dt / real_time_factor)  # Comment out completely for maximum speed

except KeyboardInterrupt:
    print("\nSimulation interrupted by user.")
finally:
    # Clean up controller if initialized
    if controller_connected:
        rc.close()

    # Disconnect from PyBullet
    p.disconnect()

    try:
        # Create plots after simulation is complete
        plt.figure(figsize=(12, 10))

        # Plot angular velocities
        plt.subplot(4, 1, 1)
        plt.plot(time_points, roll_velocity, 'r-', label='Roll Velocity')
        plt.plot(time_points, desired_roll, 'r--', label='Desired Roll')
        plt.ylabel('Roll Rate (rad/s)')
        plt.grid(True)
        plt.legend()
        plt.title('Drone Angular Velocity vs Time')

        plt.subplot(4, 1, 2)
        plt.plot(time_points, pitch_velocity, 'g-', label='Pitch Velocity')
        plt.plot(time_points, desired_pitch, 'g--', label='Desired Pitch')
        plt.ylabel('Pitch Rate (rad/s)')
        plt.grid(True)
        plt.legend()

        plt.subplot(4, 1, 3)
        plt.plot(time_points, yaw_velocity, 'b-', label='Yaw Velocity')
        plt.plot(time_points, desired_yaw, 'b--', label='Desired Yaw')
        plt.ylabel('Yaw Rate (rad/s)')
        plt.grid(True)
        plt.legend()

        # Plot throttle values
        plt.subplot(4, 1, 4)
        plt.plot(time_points, throttle_values, 'k-', label='Throttle PWM')
        plt.xlabel('Time (s)')
        plt.ylabel('Throttle PWM')
        plt.grid(True)
        plt.legend()

        plt.tight_layout()

        # Check if the plotting directory exists, if not create it
        import os

        save_dir = 'plots'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Save the plot to a file
        plt.savefig(os.path.join(save_dir, 'drone_performance.png'))

        # Show plot only if in interactive environment
        try:
            plt.show()
        except Exception as e:
            print(f"Note: Could not display plot interactively: {e}")
            print(f"Plot saved to {os.path.join(save_dir, 'drone_performance.png')}")
    except Exception as e:
        print(f"Error creating plots: {e}")