import numpy as np
from NeuralNetwork import AdamOptimizer
from PolicyNetwork import PolicyNetwork
from ValueNN import ValueNetwork


class A2CAgent:
    """Actor-Critic Agent implementing policy gradient algorithm"""

    def __init__(self, state_size, action_size, policy_lr=0.001, value_lr=0.001, gamma=0.99):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma

        # Networks
        self.policy = PolicyNetwork(state_size, action_size, hidden_sizes=[64])
        self.value = ValueNetwork(state_size, hidden_sizes=[64])

        # Optimizers
        self.policy_optimizer = AdamOptimizer(learning_rate=policy_lr)
        self.value_optimizer = AdamOptimizer(learning_rate=value_lr)

    def generate_episode(self, env, max_steps=200):
        """Generate one episode using current policy"""
        states, actions, rewards, log_probs = [], [], [], []

        state = env.reset()
        done = False
        step = 0

        while not done and step < max_steps:
            # Sample action from policy
            action, log_prob = self.policy.sample_action(state)

            # Take step in environment
            next_state, reward, done, _ = env.step(action)

            # Store transition
            states.append(state.copy())
            actions.append(action)
            rewards.append(reward)
            log_probs.append(log_prob)

            state = next_state
            step += 1

        return np.array(states), np.array(actions), np.array(rewards), np.array(log_probs)

    def compute_returns(self, rewards):
        """Compute Monte Carlo returns G_t = sum(gamma^k * r_{t+k})"""
        returns = np.zeros_like(rewards, dtype=np.float32)
        G = 0

        # Work backwards from end of episode
        for t in reversed(range(len(rewards))):
            G = rewards[t] + self.gamma * G
            returns[t] = G

        return returns

    def compute_advantages(self, states, returns):
        """Compute advantages A = G - V(s)"""
        values = self.value.forward(states)
        advantages = returns - values
        return advantages

    def update_networks(self, states, actions, returns, advantages):
        """Update both policy and value networks"""
        # Update value network
        value_gradients, value_loss = self.value.compute_value_loss(states, returns)
        self.value_optimizer.update(self.value.network, value_gradients)

        # Update policy network
        policy_gradients, policy_loss = self.policy.compute_policy_gradient(states, actions, advantages)
        self.policy_optimizer.update(self.policy.network, policy_gradients)

        return policy_loss, value_loss

    def train_episode(self, env):
        """Train on one episode"""
        # Generate episode
        states, actions, rewards, log_probs = self.generate_episode(env)

        if len(states) == 0:
            return 0, 0, 0

        # Compute returns and advantages
        returns = self.compute_returns(rewards)
        advantages = self.compute_advantages(states, returns)

        # Update networks
        policy_loss, value_loss = self.update_networks(states, actions, returns, advantages)

        total_reward = np.sum(rewards)
        return total_reward, policy_loss, value_loss


def train_agent(env, agent, num_episodes=1000, print_every=100):
    """Complete training loop"""
    episode_rewards = []
    policy_losses = []
    value_losses = []

    for episode in range(num_episodes):
        # Train on one episode
        total_reward, policy_loss, value_loss = agent.train_episode(env)

        # Store metrics
        episode_rewards.append(total_reward)
        policy_losses.append(policy_loss)
        value_losses.append(value_loss)

        # Print progress
        if episode % print_every == 0:
            avg_reward = np.mean(episode_rewards[-print_every:])
            avg_policy_loss = np.mean(policy_losses[-print_every:])
            avg_value_loss = np.mean(value_losses[-print_every:])

            print(f"Episode {episode}")
            print(f"  Avg Reward: {avg_reward:.2f}")
            print(f"  Policy Loss: {avg_policy_loss:.4f}")
            print(f"  Value Loss: {avg_value_loss:.4f}")

    return episode_rewards, policy_losses, value_losses


def evaluate_agent(env, agent, num_episodes=10):
    """Test trained agent"""
    test_rewards = []

    for _ in range(num_episodes):
        state = env.reset()
        total_reward = 0
        done = False
        steps = 0

        while not done and steps < 200:
            # Use deterministic policy (no sampling)
            action_probs = agent.policy.get_action_probs(state)
            action = np.argmax(action_probs)  # Take best action

            state, reward, done, _ = env.step(action)
            total_reward += reward
            steps += 1

        test_rewards.append(total_reward)

    return test_rewards


# Example usage
if __name__ == "__main__":
    # Import environment (you need to have the environment_interface.py file)
    from Environment import CartPole

    # Create environment and agent
    env = CartPole()
    agent = A2CAgent(
        state_size=env.get_state_size(),
        action_size=env.get_action_size(),
        policy_lr=0.001,
        value_lr=0.002
    )

    print("Training A2C Agent on CartPole...")

    # Train agent
    rewards, policy_losses, value_losses = train_agent(env, agent, num_episodes=5000, print_every=100)

    print("\nTraining completed!")

    # Test trained agent
    print("\nTesting trained agent...")
    test_rewards = evaluate_agent(env, agent, num_episodes=10)
    print(f"Test rewards: {test_rewards}")
    print(f"Average test reward: {np.mean(test_rewards):.2f}")

    # Show final performance
    print(f"\nFinal training performance:")
    print(f"Last 100 episodes average reward: {np.mean(rewards[-100:]):.2f}")