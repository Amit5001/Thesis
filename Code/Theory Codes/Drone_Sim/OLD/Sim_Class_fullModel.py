import pybullet as p
import time
import os
import numpy as np
import matplotlib

matplotlib.use('Agg')  # Non-interactive backend
from ThrustAviary import ThrustAviary  # Import our custom aviary
from gym_pybullet_drones.utils.enums import DroneModel, Physics
from gym_pybullet_drones.utils.Logger import Logger
from gym_pybullet_drones.utils.utils import sync
from datetime import datetime

# Import our custom controller and plotting utilities
from Custom_DroneEnv import CascadedPIDControl
from plot_utils import plot_angles, plot_rates, plot_pwm, plot_thrust, save_all_plots


def run_simulation(control_mode="rate", simulation_duration=30):
    """
    Run the drone simulation with the specified control mode.

    Parameters
    ----------
    control_mode : str
        Either "rate" or "angle" - determines which control mode to use for the entire simulation
    simulation_duration : int
        Duration of the simulation in seconds
    """
    # Create output directory for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"drone_simulation_{control_mode}_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created output directory: {output_dir}")

    # Create log file for real-time data
    log_file = open(os.path.join(output_dir, "drone_state_log.csv"), "w")
    log_file.write(
        "time,roll,pitch,yaw,roll_rate,pitch_rate,yaw_rate,des_roll,des_pitch,des_yaw,des_roll_rate,des_pitch_rate,des_yaw_rate,pwm1,pwm2,pwm3,pwm4,thrust1,thrust2,thrust3,thrust4\n")

    # Create the environment using ThrustAviary
    env = ThrustAviary(
        drone_model=DroneModel.RACE,  # Use racer drone
        initial_xyzs=np.array([[0, 0, 1.0]]),  # Start above ground for stability
        initial_rpys=np.array([[0, 0, 0]]),  # Level orientation
        physics=Physics.PYB,  # Use PyBullet physics
        pyb_freq=240,  # Standard physics frequency
        ctrl_freq=120,  # Control frequency - half of physics for stability
        gui=True,  # Enable GUI for debugging
        record=False,  # Don't record video
        obstacles=False,  # No obstacles
        user_debug_gui=True  # Enable debug GUI
    )

    # Create our custom controller with the specified control mode
    controller = CascadedPIDControl(
        drone_model=DroneModel.RACE,
        g=9.8,
        mass=0.83,
        control_mode=control_mode  # Use the provided control mode for the entire simulation
    )

    # Create logger
    logger = Logger(
        logging_freq_hz=int(env.CTRL_FREQ),
        num_drones=1,
        duration_sec=simulation_duration,
        output_folder=output_dir
    )

    # Initial state
    obs, _ = env.reset()
    start_time = time.time()

    # Print initial observation
    print("Observation shape:", obs.shape)

    # Define rate mode trajectory function
    def get_rate_targets(t):
        """Rate mode trajectory - simple angular rates."""
        # First 5 seconds: hover to stabilize
        if t < 5:
            return np.zeros(3)
        # 5-7s: Small roll rate (0.2 rad/s = ~11.5 deg/s)
        elif t < 7:
            return np.array([0.2, 0, 0])
        # 7-9s: Small pitch rate
        elif t < 9:
            return np.array([0, 0.2, 0])
        # 9-11s: Small yaw rate
        elif t < 11:
            return np.array([0, 0, 0.2])
        # 11-13s: Combined small rates
        elif t < 13:
            return np.array([0.1, 0.1, 0.1])
        # 13-15s: Small negative roll rate
        elif t < 15:
            return np.array([-0.1, 0, 0])
        # 15-17s: Small negative pitch rate
        elif t < 17:
            return np.array([0, -0.1, 0])
        # 17-19s: Small negative yaw rate
        elif t < 19:
            return np.array([0, 0, -0.1])
        # 19-21s: Sine wave roll rate
        elif t < 21:
            return np.array([0.15 * np.sin(2 * np.pi * (t - 19)), 0, 0])
        # 21-23s: Sine wave pitch rate
        elif t < 23:
            return np.array([0, 0.15 * np.sin(2 * np.pi * (t - 21)), 0])
        # 23-25s: Sine wave yaw rate
        elif t < 25:
            return np.array([0, 0, 0.15 * np.sin(2 * np.pi * (t - 23))])
        # 25s+ gradual return to hover
        else:
            decay = max(0, 1 - (t - 25) / 5)  # Linear decay over 5 seconds
            return np.array([0, 0, 0])

    # Define angle mode trajectory function
    def get_angle_targets(t):
        """Angle mode trajectory - angles to achieve."""
        # First 5 seconds: hover to stabilize
        if t < 5:
            return np.array([0, 0, 0])
        # 5-10s: Small roll angle (0.1 rad = ~5.7 degrees)
        elif t < 10:
            roll = min(0.1, (t - 5) * 0.02)  # Gradual ramp to 0.1 rad
            return np.array([roll, 0, 0])
        # 10-15s: Small pitch angle
        elif t < 15:
            pitch = min(0.1, (t - 10) * 0.02)  # Gradual ramp to 0.1 rad
            return np.array([0, pitch, 0])
        # 15-20s: Small yaw angle rotation
        elif t < 20:
            yaw = min(0.2, (t - 15) * 0.04)  # Gradual ramp to 0.2 rad
            return np.array([0, 0, yaw])
        # 20-25s: Sine wave roll oscillation (small amplitude)
        elif t < 25:
            roll = 0.08 * np.sin(np.pi * (t - 20))
            return np.array([roll, 0, 0])
        # 25s+: Sine wave pitch oscillation (small amplitude)
        else:
            pitch = 0.08 * np.sin(np.pi * (t - 25))
            return np.array([0, pitch, 0])

    # Store desired and actual states for plotting
    time_points = []
    actual_rpy = []
    actual_rates = []
    desired_rpy = []
    desired_rates = []
    pwm_values_history = []
    thrust_values_history = []

    # Run the simulation
    for i in range(simulation_duration * int(env.CTRL_FREQ)):
        # Current time
        current_time = i / env.CTRL_FREQ

        # Extract state from observation
        current_pos = obs[0, 0:3]
        current_quat = obs[0, 3:7]
        current_vel = obs[0, 10:13]
        current_ang_vel = obs[0, 13:16]
        current_rpy = np.array(p.getEulerFromQuaternion(current_quat))

        # Store for plotting
        time_points.append(current_time)
        actual_rpy.append(current_rpy)
        actual_rates.append(current_ang_vel)

        # Determine targets based on mode
        if controller.control_mode == "rate":
            target_rates = get_rate_targets(current_time)
            target_attitude = None
            # For rate mode, there's no direct desired attitude, so we just track current
            desired_rpy.append(current_rpy)
            desired_rates.append(target_rates)
        else:  # angle mode
            target_attitude = get_angle_targets(current_time)
            target_rates = None
            desired_rpy.append(target_attitude)
            # For angle mode, desired rates will be computed by the controller
            # We'll store them after the controller call

        # Print debug info at 1Hz
        if i % env.CTRL_FREQ == 0:
            print(f"\n==== Time: {current_time:.2f}s - Mode: {controller.control_mode} ====")
            print(f"Position: X={current_pos[0]:.2f}, Y={current_pos[1]:.2f}, Z={current_pos[2]:.2f}")
            roll, pitch, yaw = np.degrees(current_rpy)
            print(f"Attitude: Roll={roll:.2f}°, Pitch={pitch:.2f}°, Yaw={yaw:.2f}°")
            roll_rate, pitch_rate, yaw_rate = np.degrees(current_ang_vel)
            print(f"Angular Rates: Roll={roll_rate:.2f}°/s, Pitch={pitch_rate:.2f}°/s, Yaw={yaw_rate:.2f}°/s")

            if controller.control_mode == "rate":
                des_roll_rate, des_pitch_rate, des_yaw_rate = np.degrees(target_rates)
                print(
                    f"Desired Rates: Roll={des_roll_rate:.2f}°/s, Pitch={des_pitch_rate:.2f}°/s, Yaw={des_yaw_rate:.2f}°/s")
            else:
                des_roll, des_pitch, des_yaw = np.degrees(target_attitude)
                print(f"Desired Attitude: Roll={des_roll:.2f}°, Pitch={des_pitch:.2f}°, Yaw={des_yaw:.2f}°")

        # Compute control action
        pwm, des_rates, motor_thrust = controller.compute_control(
            timestep=1.0 / env.CTRL_FREQ,
            current_position=current_pos,
            current_quat=current_quat,
            current_vel=current_vel,
            current_ang_vel=current_ang_vel,
            target_attitude=target_attitude,
            target_rates=target_rates
        )

        # For angle mode, now we have the desired rates
        if controller.control_mode == "angle":
            desired_rates.append(des_rates)

        # Store control values
        pwm_values_history.append(pwm)
        thrust_values_history.append(motor_thrust)

        # Write to log file
        log_file.write(f"{current_time:.4f},{current_rpy[0]:.4f},{current_rpy[1]:.4f},{current_rpy[2]:.4f},")
        log_file.write(f"{current_ang_vel[0]:.4f},{current_ang_vel[1]:.4f},{current_ang_vel[2]:.4f},")

        # Log desired values based on control mode
        if controller.control_mode == "rate":
            log_file.write(f"{current_rpy[0]:.4f},{current_rpy[1]:.4f},{current_rpy[2]:.4f},")
            log_file.write(f"{target_rates[0]:.4f},{target_rates[1]:.4f},{target_rates[2]:.4f},")
        else:
            log_file.write(f"{target_attitude[0]:.4f},{target_attitude[1]:.4f},{target_attitude[2]:.4f},")
            log_file.write(f"{des_rates[0]:.4f},{des_rates[1]:.4f},{des_rates[2]:.4f},")

        # Log PWM and thrust values
        log_file.write(f"{pwm[0]:.1f},{pwm[1]:.1f},{pwm[2]:.1f},{pwm[3]:.1f},")
        log_file.write(f"{motor_thrust[0]:.4f},{motor_thrust[1]:.4f},{motor_thrust[2]:.4f},{motor_thrust[3]:.4f}\n")

        # Use thrust values directly for the simulation
        thrust_input = np.array(motor_thrust).reshape(1, 4)

        # Step the simulation with thrust values
        obs, _, _, _, _ = env.step(thrust_input)

        # Create a compatible state array for logging
        log_state = np.zeros(20)
        log_state[0:3] = obs[0, 0:3]  # Position
        log_state[3:7] = obs[0, 3:7]  # Quaternion
        log_state[10:13] = obs[0, 10:13]  # Linear velocity
        log_state[13:16] = obs[0, 13:16]  # Angular velocity
        log_state[16:20] = np.sqrt(thrust_input[0] / env.KF)  # Convert back to RPM for logging

        # Log the step with the correctly formatted state
        logger.log(drone=0, timestamp=current_time, state=log_state)

        # Enable this for real-time visualization
        # sync(i, start_time, 1.0/env.CTRL_FREQ)

    # Close the log file
    log_file.close()

    # Create the final plots
    save_all_plots(
        time_points,
        actual_rpy,
        desired_rpy,
        actual_rates,
        desired_rates,
        pwm_values_history,
        thrust_values_history,
        output_dir,
        mass=0.83,
        g=9.8
    )

    # Close the environment and save logger data
    env.close()
    logger.save()
    logger.save_as_csv("full_simulation")

    print(f"Simulation complete. All data saved to {output_dir}/")
    return output_dir


if __name__ == "__main__":
    # Run simulation in rate mode
    output_dir_rate = run_simulation(control_mode="rate")
    print(f"Rate mode simulation data saved to: {output_dir_rate}")

    # Run simulation in angle mode
    output_dir_angle = run_simulation(control_mode="angle")
    print(f"Angle mode simulation data saved to: {output_dir_angle}")