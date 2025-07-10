import numpy as np
from NeuralNetwork import AdamOptimizer
from PolicyNetwork import PolicyNetwork
from ValueNN import ValueNetwork
from Environment import LinearSystem
from PolicyGradient import A2CAgent, train_agent, evaluate_agent


class LinearControlAgent(A2CAgent):
    """A2C Agent specialized for linear control systems"""

    def __init__(self, A, B, Q, R, **kwargs):
        # Get system dimensions
        state_size = A.shape[0]
        action_size = 11  # Discretized actions for continuous control

        super().__init__(state_size, action_size, **kwargs)

        # Store system matrices for analysis
        self.A = A
        self.B = B
        self.Q = Q
        self.R = R

    def extract_policy_gain(self, num_samples=1000):
        """Extract linear policy K from trained network: u = -Kx"""
        # Sample states and get actions
        states = np.random.randn(num_samples, self.state_size)
        actions = []

        for state in states:
            action_probs = self.policy.get_action_probs(state)
            action_idx = np.argmax(action_probs)
            # Convert discrete action to continuous
            continuous_action = -2 + action_idx * (4 / (self.action_size - 1))
            actions.append(continuous_action)

        actions = np.array(actions).reshape(-1, 1)

        # Solve least squares: actions = -K * states
        K = -np.linalg.lstsq(states, actions, rcond=None)[0].T

        return K


def train_linear_control():
    """Train A2C agent on linear control system"""

    # Define linear system: x_{k+1} = Ax_k + Bu_k + noise
    A = np.array([[1.1, 0.1],
                  [0.0, 0.9]])

    B = np.array([[0.1],
                  [1.0]])

    Q = np.eye(2)  # State cost
    R = np.array([[0.1]])  # Control cost

    # Create environment
    env = LinearSystem(A=A, B=B, Q=Q, R=R, noise_std=0.01, max_steps=50)

    # Create specialized agent
    agent = LinearControlAgent(
        A=A, B=B, Q=Q, R=R,
        policy_lr=0.001,
        value_lr=0.002,
        gamma=0.95
    )

    print("Training A2C Agent on Linear Control System...")
    print(f"System: A = \n{A}")
    print(f"B = \n{B}")
    print(f"Q = \n{Q}")
    print(f"R = \n{R}")

    # Train agent
    rewards, policy_losses, value_losses = train_agent(
        env, agent,
        num_episodes=10000,
        print_every=200
    )

    print("\nTraining completed!")

    # Test performance
    test_rewards = evaluate_agent(env, agent, num_episodes=20)
    print(f"Test rewards: {test_rewards}")
    print(f"Average test reward: {np.mean(test_rewards):.2f}")

    # Extract learned policy gain
    K_learned = agent.extract_policy_gain()
    print(f"\nLearned policy gain K: {K_learned}")

    # Compare with optimal LQR solution
    try:
        import control
        # Create discrete system
        sys = control.ss(A, B, np.eye(A.shape[0]), 0, dt=True)

        # Solve LQR
        K_optimal, S, E = control.dlqr(A, B, Q, R)

        print(f"Optimal LQR gain K*: {K_optimal}")
        print(f"Learned gain K: {K_learned}")
        print(f"Gain difference: {np.abs(K_learned - K_optimal)}")
        print(f"Relative error: {np.linalg.norm(K_learned - K_optimal) / np.linalg.norm(K_optimal) * 100:.2f}%")

        return agent, K_learned, rewards, K_optimal

    except ImportError:
        print("Control library not available for LQR comparison")
        return agent, K_learned, rewards, None


def evaluate_learned_policy(agent, env, K_learned, num_episodes=5):
    """Test the learned linear policy"""
    print(f"\nTesting learned policy u = -Kx with K = {K_learned}")

    for episode in range(num_episodes):
        state = env.reset()
        total_reward = 0
        states_trajectory = [state.copy()]
        actions_trajectory = []

        for step in range(50):
            # Use learned linear policy directly
            continuous_action = -K_learned @ state.reshape(-1, 1)
            continuous_action = np.clip(continuous_action[0, 0], -2, 2)

            # Convert to discrete action for environment
            action_idx = int((continuous_action + 2) * (agent.action_size - 1) / 4)
            action_idx = np.clip(action_idx, 0, agent.action_size - 1)

            state, reward, done, _ = env.step(action_idx)
            total_reward += reward

            states_trajectory.append(state.copy())
            actions_trajectory.append(continuous_action)

            if done:
                break

        print(f"Episode {episode + 1}: Reward = {total_reward:.2f}, Steps = {len(actions_trajectory)}")

        # Show state trajectory for first episode
        if episode == 0:
            states_array = np.array(states_trajectory)
            print(f"Final state: {states_array[-1]}")
            print(f"State norm progression: {[np.linalg.norm(s) for s in states_array[::10]]}")


def evaluate_lqr_policy(env, K_optimal, num_episodes=5):
    """Test the optimal LQR policy for comparison"""
    print(f"\nTesting optimal LQR policy u = -K*x with K* = {K_optimal}")

    for episode in range(num_episodes):
        state = env.reset()
        total_reward = 0

        for step in range(50):
            # Use optimal LQR policy
            continuous_action = -K_optimal @ state.reshape(-1, 1)
            continuous_action = np.clip(continuous_action[0, 0], -2, 2)

            # Convert to discrete action for environment
            action_idx = int((continuous_action + 2) * (env.get_action_size() - 1) / 4)
            action_idx = np.clip(action_idx, 0, env.get_action_size() - 1)

            state, reward, done, _ = env.step(action_idx)
            total_reward += reward

            if done:
                break

        print(f"Episode {episode + 1}: Reward = {total_reward:.2f}")


def compare_policies(agent, env, K_learned, K_optimal):
    """Compare learned vs optimal policies"""
    print("\nPolicy Comparison:")

    # Test learned policy
    learned_rewards = []
    for _ in range(10):
        state = env.reset()
        total_reward = 0
        for step in range(50):
            continuous_action = -K_learned @ state.reshape(-1, 1)
            continuous_action = np.clip(continuous_action[0, 0], -2, 2)
            action_idx = int((continuous_action + 2) * (agent.action_size - 1) / 4)
            action_idx = np.clip(action_idx, 0, agent.action_size - 1)
            state, reward, done, _ = env.step(action_idx)
            total_reward += reward
            if done: break
        learned_rewards.append(total_reward)

    # Test optimal policy
    optimal_rewards = []
    for _ in range(10):
        state = env.reset()
        total_reward = 0
        for step in range(50):
            continuous_action = -K_optimal @ state.reshape(-1, 1)
            continuous_action = np.clip(continuous_action[0, 0], -2, 2)
            action_idx = int((continuous_action + 2) * (env.get_action_size() - 1) / 4)
            action_idx = np.clip(action_idx, 0, env.get_action_size() - 1)
            state, reward, done, _ = env.step(action_idx)
            total_reward += reward
            if done: break
        optimal_rewards.append(total_reward)

    print(f"Learned policy average reward: {np.mean(learned_rewards):.2f} ± {np.std(learned_rewards):.2f}")
    print(f"Optimal LQR average reward: {np.mean(optimal_rewards):.2f} ± {np.std(optimal_rewards):.2f}")
    print(f"Performance ratio: {np.mean(learned_rewards) / np.mean(optimal_rewards) * 100:.1f}%")


if __name__ == "__main__":
    # Train the agent
    result = train_linear_control()

    if len(result) == 4:
        agent, K_learned, training_rewards, K_optimal = result

        # Create fresh environment for testing
        A = np.array([[1.1, 0.1], [0.0, 0.9]])
        B = np.array([[0.1], [1.0]])
        Q = np.eye(2)
        R = np.array([[0.1]])

        test_env = LinearSystem(A=A, B=B, Q=Q, R=R, noise_std=0.01, max_steps=100)

        # Test both policies
        evaluate_learned_policy(agent, test_env, K_learned)

        if K_optimal is not None:
            evaluate_lqr_policy(test_env, K_optimal)
            compare_policies(agent, test_env, K_learned, K_optimal)

        print(f"\nTraining summary:")
        print(f"Final 100 episodes average reward: {np.mean(training_rewards[-100:]):.2f}")
        print(f"Learned control law: u = -{K_learned[0, 0]:.3f}*x1 + {-K_learned[0, 1]:.3f}*x2")
        if K_optimal is not None:
            print(f"Optimal control law: u = -{K_optimal[0, 0]:.3f}*x1 + {-K_optimal[0, 1]:.3f}*x2")

    else:
        agent, K_learned, training_rewards = result
        print("LQR comparison not available")