import numpy as np
from collections import deque
import random


class BasicRLController:
    def __init__(self, state_dim, action_dim, hidden_layers=[64, 32],
                 learning_rate=0.001, gamma=0.99, exploration_rate=0.3,
                 exploration_decay=0.995, min_exploration=0.01):

        self.state_dim = state_dim
        self.action_dim = action_dim
        self.learning_rate = learning_rate
        self.gamma = gamma  # Discount factor

        # Exploration parameters
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.min_exploration = min_exploration

        # Experience replay buffer
        self.memory = deque(maxlen=10000)
        self.batch_size = 32

        # Initialize policy network
        self.policy_weights, self.policy_biases = self._initialize_network(
                                                            hidden_layers, state_dim, action_dim
                                                                        )
        # Initialize value network

        self.value_weights, self.value_biases = self._initialize_network(
                                                            hidden_layers, state_dim, 1
                                                                        )

        # Training statistics
        self.episode_rewards = []
        self.episode_count = 0

    def _initialize_network(self, hidden_layers, input_dim, output_dim):
        """Initialize network weights and biases."""
        weights = []
        biases = []

        # First layer
        prev_dim = input_dim
        for layer_size in hidden_layers:
            # Xavier/He initialization
            w = np.random.randn(prev_dim, layer_size) * np.sqrt(2.0 / prev_dim)
            b = np.zeros((1, layer_size))
            weights.append(w)
            biases.append(b)
            prev_dim = layer_size

        # Output layer
        w = np.random.randn(prev_dim, output_dim) * 0.1
        b = np.zeros((1, output_dim))
        weights.append(w)
        biases.append(b)

        return weights, biases

    def _relu(self, x):
        """ReLU activation function."""
        return np.maximum(0, x)

    def _forward_pass(self, x, weights, biases):
        """Forward pass through network."""
        x = np.array(x).reshape(1, -1)

        for i, (w, b) in enumerate(zip(weights, biases)):
            x = x @ w + b
            if i < len(weights) - 1:  # Apply ReLU to all layers except output
                x = self._relu(x)

        return x

    def get_action(self, state, training=True):
        """
        Get action for given state.
        Args:
            state: Current state
            training: If True, adds exploration noise
        Returns:
            action: Action to take
        """
        # Get action from policy network
        action = self._forward_pass(state, self.policy_weights, self.policy_biases)

        # Add exploration noise during training
        if training and np.random.random() < self.exploration_rate:
            noise = np.random.normal(0, 0.1, action.shape)
            action = action + noise

        return action.flatten()

    def get_value(self, state):
        """Get value estimate for given state."""
        value = self._forward_pass(state, self.value_weights, self.value_biases)
        return value.flatten()[0]

    def store_experience(self, state, action, reward, next_state, done):
        """
        Store experience in replay buffer.
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode is finished
        """
        self.memory.append((
            np.array(state).flatten(),
            np.array(action).flatten(),
            reward,
            np.array(next_state).flatten(),
            done
        ))

    def _compute_targets(self, batch):
        """Compute target values for training."""
        states, actions, rewards, next_states, dones = batch

        value_targets = []
        policy_targets = []

        for i in range(len(states)):
            # Value target using Bellman equation: V(s) = r + γ * V(s')
            if dones[i]:
                value_target = rewards[i]
            else:
                next_value = self.get_value(next_states[i])
                value_target = rewards[i] + self.gamma * next_value

            value_targets.append(value_target)

            # Policy target using advantage
            current_value = self.get_value(states[i])
            advantage = value_target - current_value

            # If advantage > 0, action was good; if < 0, action was bad
            if advantage > 0:
                # Reinforce good actions
                policy_target = actions[i] * (1 + 0.1 * np.tanh(advantage))
            else:
                # Discourage bad actions
                policy_target = actions[i] * (1 + 0.1 * np.tanh(advantage))

            policy_targets.append(policy_target)

        return np.array(value_targets), np.array(policy_targets)

    def _compute_gradients(self, states, targets, weights, biases, target_type='value'):
        """Compute gradients using finite differences."""
        gradients_w = []
        gradients_b = []
        epsilon = 1e-7

        for layer_idx, (w, b) in enumerate(zip(weights, biases)):
            # Weight gradients
            grad_w = np.zeros_like(w)
            for i in range(w.shape[0]):
                for j in range(w.shape[1]):
                    # Perturb weight
                    weights[layer_idx][i, j] += epsilon
                    loss_plus = self._compute_loss(states, targets, weights, biases, target_type)

                    weights[layer_idx][i, j] -= 2 * epsilon
                    loss_minus = self._compute_loss(states, targets, weights, biases, target_type)

                    # Restore weight
                    weights[layer_idx][i, j] += epsilon

                    # Compute gradient
                    grad_w[i, j] = (loss_plus - loss_minus) / (2 * epsilon)

            gradients_w.append(grad_w)

            # Bias gradients
            grad_b = np.zeros_like(b)
            for j in range(b.shape[1]):
                # Perturb bias
                biases[layer_idx][0, j] += epsilon
                loss_plus = self._compute_loss(states, targets, weights, biases, target_type)

                biases[layer_idx][0, j] -= 2 * epsilon
                loss_minus = self._compute_loss(states, targets, weights, biases, target_type)

                # Restore bias
                biases[layer_idx][0, j] += epsilon

                # Compute gradient
                grad_b[0, j] = (loss_plus - loss_minus) / (2 * epsilon)

            gradients_b.append(grad_b)

        return gradients_w, gradients_b

    def _compute_loss(self, states, targets, weights, biases, target_type):
        """Compute mean squared error loss."""
        total_loss = 0
        for i, (state, target) in enumerate(zip(states, targets)):
            prediction = self._forward_pass(state, weights, biases)
            if target_type == 'value':
                loss = (prediction[0, 0] - target) ** 2
            else:  # policy
                target = target.reshape(1, -1)
                loss = np.sum((prediction - target) ** 2)
            total_loss += loss
        return total_loss / len(states)

    def _update_weights(self, weights, biases, grad_w, grad_b):
        """Update network weights using gradients."""
        for i in range(len(weights)):
            weights[i] -= self.learning_rate * grad_w[i]
            biases[i] -= self.learning_rate * grad_b[i]

    def learn(self):
        """
        Learn from stored experiences.
        Returns:
            dict: Training statistics
        """
        if len(self.memory) < self.batch_size:
            return None

        # Sample batch from memory
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        # Compute targets
        value_targets, policy_targets = self._compute_targets(
            (states, actions, rewards, next_states, dones)
        )

        # Train value network
        value_grad_w, value_grad_b = self._compute_gradients(
            states, value_targets, self.value_weights, self.value_biases, 'value'
        )
        self._update_weights(self.value_weights, self.value_biases, value_grad_w, value_grad_b)

        # Train policy network
        policy_grad_w, policy_grad_b = self._compute_gradients(
            states, policy_targets, self.policy_weights, self.policy_biases, 'policy'
        )
        self._update_weights(self.policy_weights, self.policy_biases, policy_grad_w, policy_grad_b)

        # Decay exploration rate
        self.exploration_rate = max(
            self.min_exploration,
            self.exploration_rate * self.exploration_decay
        )

        # Compute losses for monitoring
        value_loss = self._compute_loss(states, value_targets, self.value_weights, self.value_biases, 'value')
        policy_loss = self._compute_loss(states, policy_targets, self.policy_weights, self.policy_biases, 'policy')

        return {
            'value_loss': value_loss,
            'policy_loss': policy_loss,
            'exploration_rate': self.exploration_rate
        }

    def train_episode(self, env, max_steps=200):
        """
        Train for one complete episode.
        Args:
            env: Environment with reset() and step(action) methods
            max_steps: Maximum steps per episode
        Returns:
            dict: Episode statistics
        """
        state = env.reset()
        if hasattr(state, 'flatten'):
            state = state.flatten()

        total_reward = 0
        step_count = 0
        losses = []

        for step in range(max_steps):
            # Get action
            action = self.get_action(state, training=True)

            # Take step in environment
            next_state, reward, done = env.step(action)
            if hasattr(next_state, 'flatten'):
                next_state = next_state.flatten()

            # Store experience
            self.store_experience(state, action, reward, next_state, done)

            # Learn from experience
            loss_info = self.learn()
            if loss_info:
                losses.append(loss_info)

            total_reward += reward
            state = next_state
            step_count += 1

            if done:
                break

        # Record episode statistics
        self.episode_rewards.append(total_reward)
        self.episode_count += 1

        # Compute average losses
        avg_losses = {}
        if losses:
            for key in losses[0].keys():
                avg_losses[key] = np.mean([loss[key] for loss in losses])

        return {
            'episode': self.episode_count,
            'total_reward': total_reward,
            'steps': step_count,
            'avg_losses': avg_losses
        }

    def evaluate(self, env, num_episodes=10, max_steps=200):
        """
        Evaluate the learned policy without exploration.
        Args:
            env: Environment
            num_episodes: Number of episodes to evaluate
            max_steps: Maximum steps per episode
        Returns:
            dict: Evaluation statistics
        """
        episode_rewards = []
        episode_lengths = []

        for episode in range(num_episodes):
            state = env.reset()
            if hasattr(state, 'flatten'):
                state = state.flatten()

            total_reward = 0
            steps = 0

            for step in range(max_steps):
                # Get action without exploration
                action = self.get_action(state, training=False)

                # Take step
                next_state, reward, done = env.step(action)
                if hasattr(next_state, 'flatten'):
                    next_state = next_state.flatten()

                total_reward += reward
                state = next_state
                steps += 1

                if done:
                    break

            episode_rewards.append(total_reward)
            episode_lengths.append(steps)

        return {
            'mean_reward': np.mean(episode_rewards),
            'std_reward': np.std(episode_rewards),
            'mean_length': np.mean(episode_lengths),
            'episodes': episode_rewards
        }

    def get_training_stats(self):
        """Get training statistics."""
        return {
            'episode_count': self.episode_count,
            'episode_rewards': self.episode_rewards,
            'current_exploration_rate': self.exploration_rate
        }


# Simple test environment
class SimpleEnv:
    def __init__(self):
        self.state = None
        self.target = np.array([1.0, 1.0])

    def reset(self):
        self.state = np.random.randn(2) * 2
        return self.state.copy()

    def step(self, action):
        # Simple dynamics: move towards action
        self.state += np.array(action) * 0.1

        # Reward based on distance to target
        distance = np.linalg.norm(self.state - self.target)
        reward = -distance

        # Episode ends when close to target or after many steps
        done = distance < 0.2

        return self.state.copy(), reward, done


# Example usage and test
if __name__ == "__main__":


    # Create controller and environment
    controller = BasicRLController(state_dim=2, action_dim=2, learning_rate=0.01)
    env = SimpleEnv()

    print("Training Basic RL Controller...")

    # Training loop
    for episode in range(100):
        result = controller.train_episode(env)

        if episode % 20 == 0:
            print(f"Episode {result['episode']}: "
                  f"Reward={result['total_reward']:.2f}, "
                  f"Steps={result['steps']}, "
                  f"Exploration={result['avg_losses'].get('exploration_rate', 0):.3f}")

    # Evaluate the learned policy
    print("\nEvaluating learned policy...")
    eval_stats = controller.evaluate(env, num_episodes=10)
    print(f"Evaluation - Mean Reward: {eval_stats['mean_reward']:.2f} ± {eval_stats['std_reward']:.2f}")
    print(f"Mean Episode Length: {eval_stats['mean_length']:.1f}")