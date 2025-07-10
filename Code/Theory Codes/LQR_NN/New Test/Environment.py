import numpy as np


class Environment:
    """Base environment interface"""

    def __init__(self):
        self.state = None
        self.done = False

    def reset(self):
        """Reset environment to initial state"""
        raise NotImplementedError

    def step(self, action):
        """Take action, return (next_state, reward, done, info)"""
        raise NotImplementedError

    def get_state_size(self):
        """Return dimensionality of state space"""
        raise NotImplementedError

    def get_action_size(self):
        """Return number of discrete actions"""
        raise NotImplementedError


class GridWorld(Environment):
    """Simple grid world environment"""

    def __init__(self, size=5):
        super().__init__()
        self.size = size
        self.goal_pos = (size - 1, size - 1)  # Bottom-right corner
        self.agent_pos = None

    def reset(self):
        """Reset agent to top-left corner"""
        self.agent_pos = (0, 0)
        self.done = False
        return self._get_state()

    def step(self, action):
        """Actions: 0=up, 1=right, 2=down, 3=left"""
        if self.done:
            return self._get_state(), 0, True, {}

        # Action mapping
        moves = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # up, right, down, left

        # Calculate new position
        dr, dc = moves[action]
        new_row = max(0, min(self.size - 1, self.agent_pos[0] + dr))
        new_col = max(0, min(self.size - 1, self.agent_pos[1] + dc))

        self.agent_pos = (new_row, new_col)

        # Calculate reward
        if self.agent_pos == self.goal_pos:
            reward = 10
            self.done = True
        else:
            reward = -0.1  # Small penalty for each step

        return self._get_state(), reward, self.done, {}

    def _get_state(self):
        """Convert position to state vector"""
        state = np.zeros(self.size * self.size)
        idx = self.agent_pos[0] * self.size + self.agent_pos[1]
        state[idx] = 1
        return state

    def get_state_size(self):
        return self.size * self.size

    def get_action_size(self):
        return 4


class CartPole(Environment):
    """Simple cart-pole environment (linear dynamics)"""

    def __init__(self):
        super().__init__()
        self.gravity = 9.8
        self.masscart = 1.0
        self.masspole = 0.1
        self.total_mass = self.masspole + self.masscart
        self.length = 0.5
        self.polemass_length = self.masspole * self.length
        self.force_mag = 10.0
        self.tau = 0.02  # Time step

        # State bounds
        self.x_threshold = 2.4
        self.theta_threshold = 12 * 2 * np.pi / 360  # 12 degrees

        self.state = None
        self.steps = 0

    def reset(self):
        """Reset to random initial state"""
        self.state = np.random.uniform(-0.05, 0.05, size=(4,))
        self.steps = 0
        self.done = False
        return self.state.copy()

    def step(self, action):
        """Actions: 0=left, 1=right"""
        if self.done:
            return self.state.copy(), 0, True, {}

        # Convert action to force
        force = self.force_mag if action == 1 else -self.force_mag

        # Current state
        x, x_dot, theta, theta_dot = self.state

        # Physics simulation (simplified linear dynamics)
        costheta = np.cos(theta)
        sintheta = np.sin(theta)

        temp = (force + self.polemass_length * theta_dot ** 2 * sintheta) / self.total_mass
        thetaacc = (self.gravity * sintheta - costheta * temp) / \
                   (self.length * (4.0 / 3.0 - self.masspole * costheta ** 2 / self.total_mass))
        xacc = temp - self.polemass_length * thetaacc * costheta / self.total_mass

        # Update state using Euler integration
        x = x + self.tau * x_dot
        x_dot = x_dot + self.tau * xacc
        theta = theta + self.tau * theta_dot
        theta_dot = theta_dot + self.tau * thetaacc

        self.state = np.array([x, x_dot, theta, theta_dot])
        self.steps += 1

        # Check termination conditions
        done = (x < -self.x_threshold or x > self.x_threshold or
                theta < -self.theta_threshold or theta > self.theta_threshold or
                self.steps >= 200)

        # Reward: +1 for each step, 0 if terminated
        reward = 1.0 if not done else 0.0
        self.done = done

        return self.state.copy(), reward, done, {}

    def get_state_size(self):
        return 4

    def get_action_size(self):
        return 2


class LinearSystem(Environment):
    """Simple linear control system: x_{t+1} = Ax_t + Bu_t + noise"""

    def __init__(self, A=None, B=None, Q=None, R=None, noise_std=0.01, max_steps=50):
        super().__init__()

        # Default 2D system if not specified
        if A is None:
           A = np.array([[1.1, 0.1], [0, 0.9]])
        if B is None:
           B = np.array([[0.1], [1.0]])
        if Q is None:
           Q = np.eye(A.shape[0])  # State cost
        if R is None:
           R = np.array([[0.1]])  # Control cost

        self.A = A
        self.B = B
        self.Q = Q
        self.R = R
        self.noise_std = noise_std
        self.max_steps = max_steps

        self.state_dim = A.shape[0]
        self.action_dim = B.shape[1]

        self.state = None
        self.steps = 0

    def reset(self):
        """Reset to random initial state"""
        self.state = np.random.randn(self.state_dim) * 2
        self.steps = 0
        self.done = False
        return self.state.copy()

    def step(self, action):
        """Continuous action (will be discretized for policy gradient)"""
        if self.done:
            return self.state.copy(), 0, True, {}

        # Ensure action is proper shape
        action = np.array(action).reshape(-1, 1)

        # Linear dynamics with noise
        noise = np.random.randn(self.state_dim) * self.noise_std
        self.state = (self.A @ self.state.reshape(-1, 1) +
                      self.B @ action + noise.reshape(-1, 1)).flatten()

        # Quadratic cost (negative reward)
        state_cost = self.state.T @ self.Q @ self.state
        action_cost = action.T @ self.R @ action
        reward = -(state_cost + action_cost).item()

        self.steps += 1
        self.done = self.steps >= self.max_steps

        return self.state.copy(), reward, self.done, {}

    def get_state_size(self):
        return self.state_dim

    def get_action_size(self):
        # For discrete action space, discretize continuous actions
        return 101  # e.g., [0, 1] with steps of 0.1

    def discrete_to_continuous(self, discrete_action):
        """Convert discrete action to continuous"""
        action_values = np.linspace(0, 1, self.get_action_size())
        return action_values[discrete_action]


# Test environments
if __name__ == "__main__":

    print("\nTesting LinearSystem:")
    env = LinearSystem()
    state = env.reset()
    print(f"Initial state: {state}")

    action = np.random.randint(5)
    continuous_action = env.discrete_to_continuous(action)
    state, reward, done, _ = env.step([continuous_action])
    print(f"Action: {action} ({continuous_action:.1f}), Reward: {reward:.2f}")