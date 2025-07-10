import gymnasium as gym
import PyFlyt.gym_envs
import numpy as np
from typing import Dict, Tuple, Optional, Callable


class AngularVelocityControllerSim:
    """
    Custom PyFlyt simulator for training angular velocity controllers.
    
    - Input: PWM values for each motor [0-1] 
    - Output: State vector with angles and angular velocities
    - Reward: LQR-style with customizable error function eQe
    """
    
    def __init__(
        self,
        target_angular_rates: np.ndarray = np.array([0.0, 0.0, 0.0]),
        target_angles: np.ndarray = np.array([0.0, 0.0, 0.0]),
        Q_angular_rates: np.ndarray = None,
        Q_angles: np.ndarray = None,
        R_control: np.ndarray = None,
        error_function: Optional[Callable] = None,
        max_duration_seconds: float = 10.0,
        agent_hz: int = 40,
        render_mode: Optional[str] = None
    ):
        """
        Initialize the angular velocity controller simulator.
        
        Args:
            target_angular_rates: Desired angular rates [roll_rate, pitch_rate, yaw_rate] (rad/s)
            target_angles: Desired angles [roll, pitch, yaw] (rad)  
            Q_angular_rates: Weight matrix for angular rate errors (3x3)
            Q_angles: Weight matrix for angle errors (3x3)
            R_control: Weight matrix for control effort (4x4)
            error_function: Custom function to compute error vector e
            max_duration_seconds: Maximum episode duration
            agent_hz: Control frequency
            render_mode: 'human' for visualization, None for headless
        """
        
        # Default Q matrices (identity if not provided)
        self.Q_angular_rates = Q_angular_rates if Q_angular_rates is not None else np.eye(3)
        self.Q_angles = Q_angles if Q_angles is not None else np.eye(3) * 0.1  # Less weight on angles
        self.R_control = R_control if R_control is not None else np.eye(4) * 0.01  # Small control penalty
        
        # Target setpoints
        self.target_angular_rates = np.array(target_angular_rates)
        self.target_angles = np.array(target_angles)
        
        # Custom error function
        self.error_function = error_function if error_function is not None else self._default_error_function
        
        # Create the base environment (using pole balance for direct motor control)
        self.env = gym.make(
            "PyFlyt/QuadX-Pole-Balance-v4",
            max_duration_seconds=max_duration_seconds,
            agent_hz=agent_hz,
            render_mode=render_mode,
            sparse_reward=True  # We'll compute our own reward
        )
        
        # Action space: [motor1_pwm, motor2_pwm, motor3_pwm, motor4_pwm] 
        self.action_space = self.env.action_space  # Box(4,) with [0, 0.8]
        
        # Observation space: [angles(3), angular_rates(3)] = 6 dimensions
        self.observation_space = gym.spaces.Box(
            low=-np.inf, 
            high=np.inf, 
            shape=(6,), 
            dtype=np.float32
        )
        
        print(f"Action space: {self.action_space}")
        print(f"Observation space: {self.observation_space}")
        
    def _default_error_function(self, current_angles: np.ndarray, current_angular_rates: np.ndarray) -> np.ndarray:
        """
        Default error function: concatenate angle errors and angular rate errors.
        
        Args:
            current_angles: [roll, pitch, yaw] in radians
            current_angular_rates: [roll_rate, pitch_rate, yaw_rate] in rad/s
            
        Returns:
            error_vector: [angle_errors(3), angular_rate_errors(3)]
        """
        angle_errors = current_angles - self.target_angles
        angular_rate_errors = current_angular_rates - self.target_angular_rates
        return np.concatenate([angle_errors, angular_rate_errors])
    
    def _extract_state(self, obs: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract angles and angular rates from PyFlyt observation.
        
        Args:
            obs: Full observation from PyFlyt environment
            
        Returns:
            angles: [roll, pitch, yaw] in radians
            angular_rates: [roll_rate, pitch_rate, yaw_rate] in rad/s  
        """
        # PyFlyt observation structure:
        # [0:3] - angular velocities (rad/s)
        # [3:7] - quaternion (w,x,y,z) if quaternion mode, or [3:6] euler angles if euler mode
        # We need to extract the right components
        
        angular_rates = obs[0:3]  # First 3 are angular velocities
        
        # Check if using quaternions or euler angles based on observation length
        if len(obs) > 20:  # Pole balance env has longer obs due to pole states
            # For pole balance, angles are typically at positions [4:7] for quaternion
            # We'll convert quaternion to euler angles
            # This is a simplified extraction - you might need to adjust based on actual obs structure
            if obs.shape[0] > 10:
                # Try to extract euler angles (this might need adjustment based on actual obs structure)
                angles = obs[4:7] if len(obs[4:7]) == 3 else np.array([0.0, 0.0, 0.0])
            else:
                angles = np.array([0.0, 0.0, 0.0])  # Fallback
        else:
            angles = obs[3:6]  # Euler angles
            
        return angles, angular_rates
    
    def _compute_lqr_reward(self, current_angles: np.ndarray, current_angular_rates: np.ndarray, action: np.ndarray) -> float:
        """
        Compute LQR-style reward: -e^T Q e - u^T R u
        
        Args:
            current_angles: Current drone angles
            current_angular_rates: Current drone angular rates
            action: Control action (motor PWM values)
            
        Returns:
            reward: LQR-style reward (negative cost)
        """
        # Get error vector using the defined error function
        error_vector = self.error_function(current_angles, current_angular_rates)
        
        # Split error vector back into components for different Q matrices
        if len(error_vector) == 6:  # Default case: [angle_errors, angular_rate_errors]
            angle_errors = error_vector[:3]
            angular_rate_errors = error_vector[3:]
            
            # Compute quadratic costs
            angle_cost = angle_errors @ self.Q_angles @ angle_errors
            angular_rate_cost = angular_rate_errors @ self.Q_angular_rates @ angular_rate_errors
            # state_cost = angle_cost + angular_rate_cost
            state_cost = angular_rate_cost
        else:
            # For custom error functions, use a single Q matrix
            Q_combined = np.eye(len(error_vector))  # Default identity matrix
            state_cost = error_vector @ Q_combined @ error_vector
        
        # Control effort penalty
        control_cost = action @ self.R_control @ action
        
        # Return negative cost as reward (LQR minimizes cost, RL maximizes reward)
        reward = -(state_cost + control_cost)
        
        return reward
    
    def reset(self, seed: Optional[int] = None) -> Tuple[np.ndarray, Dict]:
        """Reset the environment."""
        full_obs, info = self.env.reset(seed=seed)
        
        # Extract our state representation
        angles, angular_rates = self._extract_state(full_obs)
        state = np.concatenate([angles, angular_rates])
        
        return state.astype(np.float32), info
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """
        Step the environment with PWM commands.
        
        Args:
            action: [motor1_pwm, motor2_pwm, motor3_pwm, motor4_pwm] in range [0, 0.8]
            
        Returns:
            state: [angles(3), angular_rates(3)]
            reward: LQR-style reward
            terminated: Episode terminated
            truncated: Episode truncated  
            info: Additional info
        """
        # Ensure action is in correct range
        action = np.clip(action, self.action_space.low, self.action_space.high)
        
        # Step the base environment
        full_obs, base_reward, terminated, truncated, info = self.env.step(action)
        
        # Extract our state representation
        angles, angular_rates = self._extract_state(full_obs)
        state = np.concatenate([angles, angular_rates])
        
        # Compute our custom LQR reward
        reward = self._compute_lqr_reward(angles, angular_rates, action)
        
        # Add some info for debugging
        info.update({
            'angles': angles,
            'angular_rates': angular_rates,
            'target_angles': self.target_angles,
            'target_angular_rates': self.target_angular_rates,
            'lqr_reward': reward
        })
        
        return state.astype(np.float32), reward, terminated, truncated, info
    
    def close(self):
        """Close the environment."""
        self.env.close()
    
    def render(self):
        """Render the environment."""
        return self.env.render()


# Example usage and testing
if __name__ == "__main__":
    # Example 1: Basic usage
    print("=== Basic Angular Velocity Controller Simulator ===")
    
    # Custom Q matrices for different priorities
    Q_rates = np.diag([1.0, 1.0, 0.5])  # Less weight on yaw rate
    Q_angles = np.diag([2.0, 2.0, 0.1])  # Much less weight on yaw angle
    R_control = np.eye(4)
    
    sim = AngularVelocityControllerSim(
        target_angular_rates=np.array([0.0, 0.0, 0.0]),  # Hover (no rotation)
        target_angles=np.array([0.0, 0.0, 0.0]),  # Level attitude
        Q_angular_rates=Q_rates,
        Q_angles=Q_angles,
        R_control=R_control,
        max_duration_seconds=5.0,
        render_mode=None  # Set to 'human' to see visualization
    )
    
    # Test the environment
    state, info = sim.reset()
    print(f"Initial state: {state}")
    print(f"State shape: {state.shape}")
    
    for step in range(10):
        # Random action (in practice, this would be your RL policy output)
        action = sim.action_space.sample()
        
        state, reward, terminated, truncated, info = sim.step(action)
        
        print(f"Step {step}: reward = {reward:.4f}, angles = {info['angles']}, rates = {info['angular_rates']}")
        
        if terminated or truncated:
            break
    
    sim.close()
    
    # Example 2: Custom error function
    print("\n=== Custom Error Function Example ===")
    
    def custom_error_function(angles, angular_rates):
        """
        Custom error function - only care about roll and pitch, ignore yaw.
        """
        angle_errors = angles[:2] - np.array([0.0, 0.0])  # Only roll, pitch
        rate_errors = angular_rates[:2] - np.array([0.0, 0.0])  # Only roll, pitch rates
        return np.concatenate([angle_errors, rate_errors])
    
    sim_custom = AngularVelocityControllerSim(
        error_function=custom_error_function,
        max_duration_seconds=3.0
    )
    
    state, info = sim_custom.reset()
    print(f"Custom sim initial state: {state}")
    
    sim_custom.close()
    
    print("Simulator setup complete!")