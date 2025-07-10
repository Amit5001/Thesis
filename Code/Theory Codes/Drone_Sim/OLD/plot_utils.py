import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

def plot_angles(time_points, actual_rpy, desired_rpy, output_dir):
    """Plot attitude angles comparison for the entire session."""
    # Convert lists to numpy arrays
    time_arr = np.array(time_points)
    actual_rpy_arr = np.degrees(np.array(actual_rpy))  # Convert to degrees for better readability
    desired_rpy_arr = np.degrees(np.array(desired_rpy))

    # Create figure
    plt.figure(figsize=(12, 10))

    # Plot roll
    plt.subplot(3, 1, 1)
    plt.plot(time_arr, actual_rpy_arr[:, 0], 'b-', label='Actual Roll', linewidth=2)
    plt.plot(time_arr, desired_rpy_arr[:, 0], 'r--', label='Desired Roll', linewidth=2)
    plt.title('Roll Angle', fontsize=14)
    plt.ylabel('Degrees', fontsize=12)
    plt.grid(True)
    plt.legend(fontsize=12)

    # Plot pitch
    plt.subplot(3, 1, 2)
    plt.plot(time_arr, actual_rpy_arr[:, 1], 'g-', label='Actual Pitch', linewidth=2)
    plt.plot(time_arr, desired_rpy_arr[:, 1], 'm--', label='Desired Pitch', linewidth=2)
    plt.title('Pitch Angle', fontsize=14)
    plt.ylabel('Degrees', fontsize=12)
    plt.grid(True)
    plt.legend(fontsize=12)

    # Plot yaw
    plt.subplot(3, 1, 3)
    plt.plot(time_arr, actual_rpy_arr[:, 2], 'c-', label='Actual Yaw', linewidth=2)
    plt.plot(time_arr, desired_rpy_arr[:, 2], 'y--', label='Desired Yaw', linewidth=2)
    plt.title('Yaw Angle', fontsize=14)
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Degrees', fontsize=12)
    plt.grid(True)
    plt.legend(fontsize=12)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "attitude_angles.png"), dpi=300)
    plt.close()

    print(f"Attitude angles plot saved to {output_dir}/attitude_angles.png")


def plot_rates(time_points, actual_rates, desired_rates, output_dir):
    """Plot angular rates comparison for the entire session."""
    # Convert lists to numpy arrays
    time_arr = np.array(time_points)
    actual_rates_arr = np.degrees(np.array(actual_rates))  # Convert to degrees/s for better readability
    desired_rates_arr = np.degrees(np.array(desired_rates))

    # Create figure
    plt.figure(figsize=(12, 10))

    # Plot roll rate
    plt.subplot(3, 1, 1)
    plt.plot(time_arr, actual_rates_arr[:, 0], 'b-', label='Actual Roll Rate', linewidth=2)
    plt.plot(time_arr, desired_rates_arr[:, 0], 'r--', label='Desired Roll Rate', linewidth=2)
    plt.title('Roll Rate', fontsize=14)
    plt.ylabel('Degrees/s', fontsize=12)
    plt.grid(True)
    plt.legend(fontsize=12)

    # Plot pitch rate
    plt.subplot(3, 1, 2)
    plt.plot(time_arr, actual_rates_arr[:, 1], 'g-', label='Actual Pitch Rate', linewidth=2)
    plt.plot(time_arr, desired_rates_arr[:, 1], 'm--', label='Desired Pitch Rate', linewidth=2)
    plt.title('Pitch Rate', fontsize=14)
    plt.ylabel('Degrees/s', fontsize=12)
    plt.grid(True)
    plt.legend(fontsize=12)

    # Plot yaw rate
    plt.subplot(3, 1, 3)
    plt.plot(time_arr, actual_rates_arr[:, 2], 'c-', label='Actual Yaw Rate', linewidth=2)
    plt.plot(time_arr, desired_rates_arr[:, 2], 'y--', label='Desired Yaw Rate', linewidth=2)
    plt.title('Yaw Rate', fontsize=14)
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Degrees/s', fontsize=12)
    plt.grid(True)
    plt.legend(fontsize=12)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "angular_rates.png"), dpi=300)
    plt.close()

    print(f"Angular rates plot saved to {output_dir}/angular_rates.png")


def plot_pwm(time_points, pwm_values_history, output_dir):
    """Plot PWM values for each motor for the entire session."""
    # Convert lists to numpy arrays
    time_arr = np.array(time_points)
    pwm_arr = np.array(pwm_values_history)

    # Create figure
    plt.figure(figsize=(12, 8))

    # Plot PWM values
    plt.plot(time_arr, pwm_arr[:, 0], 'r-', label='Motor 1 (Front-Right)', linewidth=2)
    plt.plot(time_arr, pwm_arr[:, 1], 'g-', label='Motor 2 (Back-Right)', linewidth=2)
    plt.plot(time_arr, pwm_arr[:, 2], 'b-', label='Motor 3 (Back-Left)', linewidth=2)
    plt.plot(time_arr, pwm_arr[:, 3], 'c-', label='Motor 4 (Front-Left)', linewidth=2)

    plt.title('Motor PWM Values', fontsize=14)
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('PWM (μs)', fontsize=12)
    plt.ylim(900, 2100)  # Set y-axis limits slightly outside the PWM range
    plt.axhline(y=1500, color='k', linestyle='--', alpha=0.3, label='Hover PWM (1500)')
    plt.grid(True)
    plt.legend(fontsize=12)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "motor_pwm.png"), dpi=300)
    plt.close()

    print(f"Motor PWM plot saved to {output_dir}/motor_pwm.png")


def plot_thrust(time_points, thrust_values_history, output_dir, mass=0.83, g=9.8):
    """Plot thrust values for each motor for the entire session."""
    # Convert lists to numpy arrays
    time_arr = np.array(time_points)
    thrust_arr = np.array(thrust_values_history)

    # Create figure
    plt.figure(figsize=(12, 8))

    # Plot thrust values
    plt.plot(time_arr, thrust_arr[:, 0], 'r-', label='Motor 1 (Front-Right)', linewidth=2)
    plt.plot(time_arr, thrust_arr[:, 1], 'g-', label='Motor 2 (Back-Right)', linewidth=2)
    plt.plot(time_arr, thrust_arr[:, 2], 'b-', label='Motor 3 (Back-Left)', linewidth=2)
    plt.plot(time_arr, thrust_arr[:, 3], 'c-', label='Motor 4 (Front-Left)', linewidth=2)

    plt.title('Motor Thrust Values', fontsize=14)
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Thrust (N)', fontsize=12)
    plt.grid(True)
    plt.legend(fontsize=12)

    # Add a horizontal line for the hover thrust (weight/4)
    hover_thrust = mass * g / 4.0  # mass * g / 4 motors
    plt.axhline(y=hover_thrust, color='k', linestyle='--', alpha=0.3,
                label=f'Hover Thrust ({hover_thrust:.2f} N)')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "motor_thrust.png"), dpi=300)
    plt.close()

    print(f"Motor thrust plot saved to {output_dir}/motor_thrust.png")


def save_all_plots(time_points, actual_rpy, desired_rpy, actual_rates, desired_rates,
                  pwm_values_history, thrust_values_history, output_dir, mass=0.83, g=9.8):
    """Generate all plots in one function call."""
    plot_angles(time_points, actual_rpy, desired_rpy, output_dir)
    plot_rates(time_points, actual_rates, desired_rates, output_dir)
    plot_pwm(time_points, pwm_values_history, output_dir)
    plot_thrust(time_points, thrust_values_history, output_dir, mass, g)