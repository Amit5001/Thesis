import numpy as np
import pybullet as p
from gym_pybullet_drones.utils.enums import DroneModel


class CascadedPIDControl:
    """Cascaded PID control class for racer drones.

    Implements a two-level PID control structure:
    - Outer loop: Controls attitude (roll, pitch, yaw)
    - Inner loop: Controls angular rates

    Both loops generate PWM signals in the range of 1000-2000 μs.
    """

    def __init__(self, drone_model=DroneModel.RACE, g=9.8, mass=0.5, control_mode="rate"):
        """Initialize the cascaded PID controller.

        Parameters
        ----------
        drone_model : DroneModel
            The drone model to use (default is racer)
        g : float
            Gravity constant
        mass : float
            Mass of the drone in kilograms
        control_mode : str
            Control mode - either "rate" (rate control only) or "angle" (cascaded angle and rate control)
        """
        # Get drone parameters
        self.DRONE_MODEL = drone_model
        self.MASS = mass  # Mass of the drone in kg

        # Custom moment of inertia for your specific drone
        self.J = np.array([
            [4.5929e-3, 4.915e-6, -2.905e-6],
            [4.915e-6, 3.307063e-3, 0.176e-6],
            [-2.905e-6, 0.176e-6, 7.174892e-3]
        ])

        # Control constants
        self.GRAVITY = g
        self.WEIGHT = self.MASS * self.GRAVITY

        # PWM settings
        self.MIN_PWM = 1000
        self.MAX_PWM = 2000
        self.HOVER_PWM = 1500

        # Thrust-to-PWM conversion constants - adjust these for better PWM spread
        self.THRUST_PWM_SLOPE = 0.012155  # in g/μs - reduced from 1.2226
        self.THRUST_PWM_INTERCEPT = -13.225  # in g - adjusted from -1325.7
        self.GRAMS_TO_NEWTONS = 0.00981  # conversion factor
        self.NEWTONS_TO_GRAMS = 101.937  # conversion factor

        # Calculate minimum PWM that produces positive thrust
        self.MIN_EFFECTIVE_PWM = (0 - self.THRUST_PWM_INTERCEPT) / self.THRUST_PWM_SLOPE  # adjusted minimum

        # Add control mode
        self.control_mode = control_mode
        print(f"[INFO] Controller initialized in {self.control_mode} mode")

        # Adjusted PID gains for better performance
        # Outer loop PID gains (attitude control)
        self.P_att = np.array([0.5, 0.5, 0.3])  # Roll, Pitch, Yaw - increased from original
        self.I_att = np.array([0.03, 0.03, 0.01])  # Reduced I gain to prevent integral windup
        self.D_att = np.array([0.05, 0.05, 0.02])  # Increased D gain for damping

        # Inner loop PID gains (rate control)
        self.P_rate = np.array([0.05, 0.05, 0.02])  # Increased from original
        self.I_rate = np.array([0.0002, 0.0002, 0.0001])  # Reduced to prevent integral windup
        self.D_rate = np.array([0.001, 0.001, 0.0005])  # Increased for better damping

        # Mixer matrix with adjusted scaling for better response
        self.MIXER_MATRIX = np.array([
            [-0.5, -0.5, -0.2],  # Motor 0: front-right - increased effect
            [-0.5, 0.5, 0.2],    # Motor 1: back-right
            [0.5, 0.5, -0.2],    # Motor 2: back-left
            [0.5, -0.5, 0.2]     # Motor 3: front-left
        ])

        # Reset the controller state
        self.reset()

    def reset(self):
        """Reset the controller's internal states."""
        # Control counter and timestamps
        self.control_counter = 0
        self.last_time = None

        # Previous errors for derivative terms
        self.prev_att_error = np.zeros(3)
        self.prev_rate_error = np.zeros(3)

        # Error integrals
        self.att_error_integral = np.zeros(3)
        self.rate_error_integral = np.zeros(3)

        # Previous state
        self.last_rpy = np.zeros(3)

        # For rate limiting
        self.last_pwm = np.ones(4) * self.HOVER_PWM

    def set_control_mode(self, mode):
        """Set the control mode.

        Parameters
        ----------
        mode : str
            Either "rate" or "angle"
        """
        if mode not in ["rate", "angle"]:
            print(f"[WARNING] Invalid mode '{mode}'. Using current mode '{self.control_mode}'")
            return

        self.control_mode = mode
        print(f"[INFO] Control mode changed to {self.control_mode}")

        # Reset integral terms when switching modes
        self.att_error_integral = np.zeros(3)
        self.rate_error_integral = np.zeros(3)

    def print_debug_info(self, iteration):
        """Print debug information about the controller state."""
        if iteration % 100 == 0:  # Print every 100 iterations
            print(f"\nDebug [{self.control_mode} mode] - Iteration {iteration}")
            print(f"P Rate: {self.P_rate}")
            print(f"I Rate: {self.I_rate}")
            print(f"D Rate: {self.D_rate}")
            print(f"Rate Error Integral: {self.rate_error_integral}")
            if self.control_mode == "angle":
                print(f"P Att: {self.P_att}")
                print(f"I Att: {self.I_att}")
                print(f"D Att: {self.D_att}")
                print(f"Att Error Integral: {self.att_error_integral}")

    def compute_control(self,
                        timestep,
                        current_position,
                        current_quat,
                        current_vel,
                        current_ang_vel,
                        target_attitude=None,
                        target_rates=None):
        """Compute PWM control signals.

        Parameters
        ----------
        timestep : float
            Time step for derivative and integral calculations
        current_position : ndarray
            Current drone position (x, y, z)
        current_quat : ndarray
            Current drone orientation as quaternion (x, y, z, w)
        current_vel : ndarray
            Current drone velocity (vx, vy, vz)
        current_ang_vel : ndarray
            Current drone angular velocity (wx, wy, wz)
        target_attitude : ndarray, optional
            Target attitude as roll, pitch, yaw in radians (used only in "angle" mode)
        target_rates : ndarray, optional
            Target angular rates in rad/s (used only in "rate" mode)

        Returns
        -------
        ndarray
            4 PWM values (1000-2000) for the drone motors
        ndarray
            3 desired angular rates
        ndarray
            4 thrust values (in Newtons) for each motor
        """
        self.control_counter += 1

        # Print debug info occasionally
        self.print_debug_info(self.control_counter)

        # Ensure inputs are properly shaped numpy arrays
        current_position = np.array(current_position, dtype=float)
        current_quat = np.array(current_quat, dtype=float)
        current_vel = np.array(current_vel, dtype=float)
        current_ang_vel = np.array(current_ang_vel, dtype=float)

        # Ensure angular velocity is a 3-element array
        if current_ang_vel.size != 3:
            print(f"WARNING: Angular velocity has unexpected shape {current_ang_vel.shape}. Using zeros.")
            current_ang_vel = np.zeros(3, dtype=float)

        # Ensure quaternion is a 4-element array
        if current_quat.size != 4:
            print(f"WARNING: Quaternion has unexpected shape {current_quat.shape}. Using identity quaternion.")
            current_quat = np.array([0, 0, 0, 1], dtype=float)  # Identity quaternion [x, y, z, w]

        try:
            # Get current attitude
            current_rpy = np.array(p.getEulerFromQuaternion(current_quat))
        except Exception as e:
            print(f"Error with quaternion: {current_quat}, error: {e}")
            print("Using default orientation (level)")
            current_rpy = np.zeros(3)

        # Determine desired rates based on control mode
        if self.control_mode == "angle" and target_attitude is not None:
            # Angle mode: Compute desired rates from attitude error (full cascaded control)
            # Compute attitude error
            attitude_error = target_attitude - current_rpy
            # Normalize yaw error to [-pi, pi]
            attitude_error[2] = (attitude_error[2] + np.pi) % (2 * np.pi) - np.pi

            # Compute the integral of the error
            self.att_error_integral += attitude_error * timestep
            # Anti-windup: limit the integral term
            self.att_error_integral = np.clip(self.att_error_integral, -0.3, 0.3)  # Reduced from -0.5, 0.5

            # Compute the derivative of the error
            if self.control_counter > 1:
                att_error_derivative = (attitude_error - self.prev_att_error) / timestep
            else:
                att_error_derivative = np.zeros(3)
            self.prev_att_error = attitude_error.copy()  # Added .copy() to prevent reference issues

            # Outer loop PID to calculate desired rates
            desired_rates = (self.P_att * attitude_error +
                            self.I_att * self.att_error_integral +
                            self.D_att * att_error_derivative)

            # Limit maximum desired rates to realistic values (in rad/s)
            max_rates = np.array([2.0, 2.0, 1.5])  # About 115°/s for roll/pitch, 86°/s for yaw
            desired_rates = np.clip(desired_rates, -max_rates, max_rates)

            # For debugging
            if self.control_counter % 100 == 0:
                print(f"Angle Mode - Att Error: {attitude_error}, Desired Rates: {desired_rates}")
        else:
            # Rate mode: Use provided target rates directly (rate-only control)
            if target_rates is None:
                # If no target rates provided, default to zero
                desired_rates = np.zeros(3)
            else:
                desired_rates = target_rates

            # For debugging
            if self.control_counter % 100 == 0:
                print(f"Rate Mode - Desired Rates: {desired_rates}")

        # Inner loop: Rate control (common to both modes)
        # Rate PID control
        rate_error = desired_rates - current_ang_vel
        self.rate_error_integral += rate_error * timestep
        # Anti-windup: limit the integral term (reduced from original)
        self.rate_error_integral = np.clip(self.rate_error_integral, -0.5, 0.5)

        # Compute the derivative of the rate error
        if self.control_counter > 1:
            rate_error_derivative = (rate_error - self.prev_rate_error) / timestep
        else:
            rate_error_derivative = np.zeros(3)
        self.prev_rate_error = rate_error.copy()  # Added .copy() to prevent reference issues

        # Apply PID control to get torques
        PID_rate_out = (self.P_rate * rate_error +
                        self.I_rate * self.rate_error_integral +
                        self.D_rate * rate_error_derivative)

        # Calculate base thrust for hover
        base_thrust = self.WEIGHT / 4.0  # Each motor needs to produce 1/4 of the weight

        # Apply motor mixing
        motor_mix = np.zeros(4)
        for i in range(4):
            torque_contribution = np.dot(self.MIXER_MATRIX[i], PID_rate_out)
            # Add base thrust and torque effect
            motor_mix[i] = base_thrust + torque_contribution

        # Ensure non-negative thrust values
        motor_thrust = np.clip(motor_mix, 0, None)

        # Convert thrust to PWM
        pwm_values = self.thrust_to_pwm(motor_thrust)

        # Add rate limiting to avoid sudden changes
        if hasattr(self, 'last_pwm'):
            # Limit PWM changes to 20 per timestep (reduced from 30)
            pwm_rate_limit = 20
            pwm_values = np.clip(
                pwm_values,
                self.last_pwm - pwm_rate_limit,
                self.last_pwm + pwm_rate_limit
            )
        self.last_pwm = pwm_values.copy()

        return pwm_values, desired_rates, motor_thrust

    def thrust_to_pwm(self, thrust_values_newtons):
        """Convert thrust values from Newtons to PWM signals using the empirical model.

        Based on the adjusted equation: thrust_grams = THRUST_PWM_SLOPE * PWM + THRUST_PWM_INTERCEPT

        Parameters
        ----------
        thrust_values_newtons : ndarray
            Array of thrust values for each motor in Newtons

        Returns
        -------
        ndarray
            Array of PWM values (1000-2000) for each motor
        """
        # Convert thrust from Newtons to grams
        thrust_values_grams = thrust_values_newtons * self.NEWTONS_TO_GRAMS

        # Solve for PWM: PWM = (thrust_grams - INTERCEPT) / SLOPE
        pwm = (thrust_values_grams - self.THRUST_PWM_INTERCEPT) / self.THRUST_PWM_SLOPE

        # Ensure PWM values are within acceptable range
        return np.clip(pwm, self.MIN_EFFECTIVE_PWM, self.MAX_PWM)

    def pwm_to_thrust(self, pwm_values):
        """Convert PWM values to thrust using the empirical model.

        Based on the adjusted equation: thrust_grams = THRUST_PWM_SLOPE * PWM + THRUST_PWM_INTERCEPT

        Parameters
        ----------
        pwm_values : ndarray
            Array of PWM values (1000-2000) for each motor

        Returns
        -------
        ndarray
            Array of thrust values in Newtons for each motor
        """
        # Convert thrust from grams to Newtons
        thrust_newtons = (self.THRUST_PWM_SLOPE * pwm_values + self.THRUST_PWM_INTERCEPT)

        # Ensure non-negative thrust (motors can't push downward)
        return np.clip(thrust_newtons, 0, None)