import numpy as np
import control as ctrl


class LQR_Env:
    def __init__(self, A, B, Q, R, noise_std=0.0):
        self.A = A
        self.B = B
        self.Q = Q
        self.R = R
        self.noise_std = noise_std
        self.state_dim = A.shape[0]
        self.action_dim = B.shape[1]

        self.state = np.random.randn(self.state_dim, 1)  # Starting with a random initial state
        self.K, self.P = self.calculate_lqr_gain()

    def reset(self):
        self.state = np.random.randn(self.state_dim, 1)  # resetting the state
        return self.state.copy()

    def step(self, action):
        # Apply the control input
        u = action.reshape(-1, 1)
        noise = np.random.normal(0, self.noise_std, (self.state_dim, 1))

        next_state = self.A @ self.state + self.B @ u + noise

        # Calculate the cost
        cost = (self.state.T @ self.Q @ self.state + u.T @ self.R @ u).item()
        reward = -cost  # Reward is negative of cost

        # Update the state
        self.state = next_state
        done = False  # LQR typically runs indefinitely
        return next_state.flatten(), reward, done

    def calculate_lqr_gain(self, cont_or_discrete='continuous'):
        """
        Calculate the LQR gain using the continuous-time algebraic Riccati equation.
        """
        if cont_or_discrete == 'discrete':
            K, P, E = ctrl.dlqr(self.A, self.B, self.Q, self.R)
        else:
            K, P, E = ctrl.lqr(self.A, self.B, self.Q, self.R)
        return K, P

    def get_lqr_action(self, state):
        if state is None:
            state = self.state
        else:
            state = state.reshape(-1, 1)
        return (-self.K @ state).flatten()

    def get_true_value(self, state):
        if state is None:
            state = self.state
        else:
            state = state.reshape(-1, 1)
        return (state.T @ self.P @ state).item()

    def get_cost(self, state, action):
        """
        Calculate the cost for a given state and action.
        """
        state = state.reshape(-1, 1)
        u = action.reshape(-1, 1)
        return (state.T @ self.Q @ state + u.T @ self.R @ u).item()


if __name__ == "__main__":
    # Example usage
    A = np.array([[0.0, 1.0], [-1.0, -1.0]])
    B = np.array([[0.0], [1.0]])
    Q = np.eye(2)
    R = np.array([[1.0]])
    noise_std = 0.1

    env = LQR_Env(A, B, Q, R, noise_std)
    state = env.reset()
    action = env.get_lqr_action(state.flatten())
    next_state, reward, done = env.step(action)

    print("Initial State:", state.flatten())
    print("Action Taken:", action)
    print("Next State:", next_state)
    print("Reward:", reward)
    print("True Value:", env.get_true_value(state))