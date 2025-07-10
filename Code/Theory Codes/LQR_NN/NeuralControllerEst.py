import numpy as np


class NeuralControllerEst:
    def __init__(self, state_layers, policy_layers, state_dim, action_dim, learning_rate=0.001, gamma=0.99):

        # Input Validation:
        assert state_dim > 0, "state_dim must be positive"
        assert action_dim > 0, "action_dim must be positive"
        assert 0 < learning_rate < 1, "learning_rate should be between 0 and 1"
        assert isinstance(state_layers, list), "state_layers must be a list"
        assert isinstance(policy_layers, list), "policy_layers must be a list"

        self.state_layers = state_layers
        self.policy_layers = policy_layers
        self.action_dim = action_dim
        self.state_dim = state_dim
        self.learning_rate = learning_rate
        self.gamma = gamma

        # Experience buffer and exploration
        self.experience_buffer = []
        self.exploration_noise = 0.1
        self.batch_size = 5  # Small batch for learning

        '''
            Both the value and policy networks are initialized with same amount of neurons on the first layer because:
                Value function: "Given this state, how good/bad is my situation?"
                Policy function: "Given this state, what action should I take?"

            The output of the value and policy networks are different:
                Value network: Outputs a single value (scalar) representing the value of the state.
                Policy network: Outputs a vector of actions (size equal to action_dim). For example - 4 motors of a quadcopter
        '''
        # Initialize Value function network:
        self.value_weights, self.value_biases = self.initialize_network(state_layers, state_dim, 1)

        # Initialize Policy network:
        self.policy_weights, self.policy_biases = self.initialize_network(policy_layers, state_dim, action_dim)

        self.value_cache = {}
        self.policy_cache = {}

    def initialize_network(self, hidden_layers, input_dim, output_dim):
        """
        Initialize weights and biases for a feedforward neural network.
        """
        weights = []
        biases = []

        # Input layer
        layer_input_dim = input_dim

        for layer_size in hidden_layers:
            weights.append(
                np.random.randn(layer_input_dim, layer_size) * np.sqrt(2.0 / layer_input_dim))  # He initialization
            biases.append(np.zeros((1, layer_size)))
            layer_input_dim = layer_size

        # Output layer
        weights.append(np.random.randn(layer_input_dim, output_dim) * 0.01)
        biases.append(np.zeros((1, output_dim)))

        return weights, biases

    def ReLU(self, x):
        return np.maximum(0, x)

    def ReLU_derivative(self, x):
        return np.where(x > 0, 1, 0)

    def forward_pass(self, x, weights, biases):
        """
        Perform a forward pass through the network.
        """
        for i, (w, b) in enumerate(zip(weights, biases)):
            x = x @ w + b
            if i < len(weights) - 1:  # Don't apply ReLU to output layer
                x = self.ReLU(x)
        return x

    def compute_value(self, state):
        """
        Compute the value of a given state using the value network.
        """
        state = np.array(state).reshape(1, -1)  # Ensure correct shape
        state_key = tuple(state.flatten())
        if state_key in self.value_cache:
            return self.value_cache[state_key]

        value = self.forward_pass(state, self.value_weights, self.value_biases)
        self.value_cache[state_key] = value
        return value

    def compute_policy(self, state):
        """
        Compute the policy (action) for a given state using the policy network.
        Returns clean network output without noise.
        """
        state = np.array(state).reshape(1, -1)
        state_key = tuple(state.flatten())

        if state_key in self.policy_cache:
            return self.policy_cache[state_key]

        policy = self.forward_pass(state, self.policy_weights, self.policy_biases)
        self.policy_cache[state_key] = policy
        return policy

    def get_action(self, state, training=True):
        """
        Main interface for getting actions with optional exploration noise.
        """
        action = self.compute_policy(state)
        if training:
            noise = np.random.normal(0, self.exploration_noise, action.shape)
            action = action + noise
        return action

    def store_experience(self, state, action, reward, next_state):
        """Store experience tuple for learning."""
        self.experience_buffer.append((state.flatten(), action.flatten(), reward, next_state.flatten()))

        # Keep buffer size manageable
        if len(self.experience_buffer) > 1000:
            self.experience_buffer.pop(0)

    def compute_td_target(self, reward, next_state):
        """Compute TD target: r + γ * V(s')"""
        next_value = self.compute_value(next_state)[0, 0]
        return reward + self.gamma * next_value

    def compute_advantage_based_policy_target(self, state, action, reward, next_state):
        """Compute policy target based on advantage estimation."""
        # Calculate advantage: A(s,a) = r + γV(s') - V(s)
        current_value = self.compute_value(state)[0, 0]
        next_value = self.compute_value(next_state)[0, 0]
        advantage = reward + self.gamma * next_value - current_value

        # Use advantage to modify the action
        # If advantage > 0, this was a good action - reinforce it
        # If advantage < 0, this was a bad action - discourage it
        advantage_weight = 0.1  # How much to adjust based on advantage

        if advantage > 0:
            # Good action: strengthen it slightly
            target = action * (1 + advantage_weight * np.tanh(advantage))
        else:
            # Bad action: weaken it
            target = action * (1 + advantage_weight * np.tanh(advantage))

        return target

    def learn_from_experience(self):
        """Learn from stored experiences using batch learning."""
        if len(self.experience_buffer) < 2:  # Need at least 2 experiences
            return None, None

        # Use recent experiences for learning
        batch_size = min(len(self.experience_buffer), self.batch_size)
        recent_experiences = self.experience_buffer[-batch_size:]

        states, value_targets, policy_targets = [], [], []

        for state, action, reward, next_state in recent_experiences:
            # Value target using TD learning
            value_target = self.compute_td_target(reward, next_state)
            value_targets.append(value_target)

            # Policy target using advantage
            policy_target = self.compute_advantage_based_policy_target(state, action, reward, next_state)
            policy_targets.append(policy_target)

            states.append(state)

        # Train on batch
        if len(states) > 0:
            return self.train_step(states, value_targets, policy_targets)

        return None, None

    def step_and_learn(self, state, action, reward, next_state):
        """Main interface: store experience and learn."""
        self.store_experience(state, action, reward, next_state)
        return self.learn_from_experience()

    def train_episode(self, env, max_steps=200):
        """Train for one episode."""
        state = env.reset().flatten()
        total_reward = 0
        value_losses, policy_losses = [], []

        for step in range(max_steps):
            # Get action with exploration
            action = self.get_action(state, training=True)

            # Take step in environment
            next_state, reward, done = env.step(action.flatten())
            total_reward += reward

            # Learn from this experience
            value_loss, policy_loss = self.step_and_learn(state, action.flatten(), reward, next_state)

            if value_loss is not None:
                value_losses.append(value_loss)
                policy_losses.append(policy_loss)

            state = next_state

            if done:
                break

        avg_value_loss = np.mean(value_losses) if value_losses else 0
        avg_policy_loss = np.mean(policy_losses) if policy_losses else 0

        return {
            'total_reward': total_reward,
            'steps': step + 1,
            'avg_value_loss': avg_value_loss,
            'avg_policy_loss': avg_policy_loss
        }

    def compute_value_loss(self, states, target_values):
        """Compute mean squared error loss for value function."""
        total_loss = 0
        for state, target in zip(states, target_values):
            predicted_value = self.compute_value(state)
            loss = (predicted_value - target) ** 2
            total_loss += loss.item() if hasattr(loss, 'item') else loss
        return total_loss / len(states)

    def compute_policy_loss(self, states, target_actions):
        """Compute mean squared error loss for policy function."""
        total_loss = 0
        for state, target_action in zip(states, target_actions):
            predicted_action = self.compute_policy(state)
            # Ensure shapes match for comparison
            target_action = np.array(target_action).reshape(1, -1)
            loss = np.sum((predicted_action - target_action) ** 2)
            total_loss += loss
        return total_loss / len(states)

    def compute_gradients(self, states, target_values, target_actions):
        """
        Compute gradients for both value and policy networks using finite differences.
        """
        gradients = {
            'value_weights': [],
            'value_biases': [],
            'policy_weights': [],
            'policy_biases': []
        }

        epsilon = 1e-7  # Small perturbation for finite differences

        # Compute value network gradients
        for i, (w, b) in enumerate(zip(self.value_weights, self.value_biases)):
            # Weight gradients
            dW = np.zeros_like(w)
            for j in range(w.shape[0]):
                for k in range(w.shape[1]):
                    # Perturb weight
                    self.value_weights[i][j, k] += epsilon
                    loss_plus = self.compute_value_loss(states, target_values)

                    self.value_weights[i][j, k] -= 2 * epsilon
                    loss_minus = self.compute_value_loss(states, target_values)

                    # Restore original weight
                    self.value_weights[i][j, k] += epsilon

                    # Finite difference gradient
                    dW[j, k] = (loss_plus - loss_minus) / (2 * epsilon)

            gradients['value_weights'].append(dW)

            # Bias gradients
            db = np.zeros_like(b)
            for j in range(b.shape[1]):
                # Perturb bias
                self.value_biases[i][0, j] += epsilon
                loss_plus = self.compute_value_loss(states, target_values)

                self.value_biases[i][0, j] -= 2 * epsilon
                loss_minus = self.compute_value_loss(states, target_values)

                # Restore original bias
                self.value_biases[i][0, j] += epsilon

                # Finite difference gradient
                db[0, j] = (loss_plus - loss_minus) / (2 * epsilon)

            gradients['value_biases'].append(db)

        # Compute policy network gradients
        for i, (w, b) in enumerate(zip(self.policy_weights, self.policy_biases)):
            # Weight gradients
            dW = np.zeros_like(w)
            for j in range(w.shape[0]):
                for k in range(w.shape[1]):
                    # Perturb weight
                    self.policy_weights[i][j, k] += epsilon
                    loss_plus = self.compute_policy_loss(states, target_actions)

                    self.policy_weights[i][j, k] -= 2 * epsilon
                    loss_minus = self.compute_policy_loss(states, target_actions)

                    # Restore original weight
                    self.policy_weights[i][j, k] += epsilon

                    # Finite difference gradient
                    dW[j, k] = (loss_plus - loss_minus) / (2 * epsilon)

            gradients['policy_weights'].append(dW)

            # Bias gradients
            db = np.zeros_like(b)
            for j in range(b.shape[1]):
                # Perturb bias
                self.policy_biases[i][0, j] += epsilon
                loss_plus = self.compute_policy_loss(states, target_actions)

                self.policy_biases[i][0, j] -= 2 * epsilon
                loss_minus = self.compute_policy_loss(states, target_actions)

                # Restore original bias
                self.policy_biases[i][0, j] += epsilon

                # Finite difference gradient
                db[0, j] = (loss_plus - loss_minus) / (2 * epsilon)

            gradients['policy_biases'].append(db)

        return gradients

    def train_step(self, states, target_values, target_actions):
        """
        Perform one training step: compute gradients and update weights.
        """
        # Clear cache before training step
        self.reset_cache()

        # Compute gradients
        gradients = self.compute_gradients(states, target_values, target_actions)

        # Update weights
        self.update_weights(gradients)

        # Compute losses after update
        value_loss = self.compute_value_loss(states, target_values)
        policy_loss = self.compute_policy_loss(states, target_actions)

        return value_loss, policy_loss

    def update_weights(self, gradients):
        """
        Update the weights and biases of the network using the computed gradients.
        """
        for i in range(len(self.value_weights)):
            self.value_weights[i] -= self.learning_rate * gradients['value_weights'][i]
            self.value_biases[i] -= self.learning_rate * gradients['value_biases'][i]

        for i in range(len(self.policy_weights)):
            self.policy_weights[i] -= self.learning_rate * gradients['policy_weights'][i]
            self.policy_biases[i] -= self.learning_rate * gradients['policy_biases'][i]

    def reset_cache(self):
        """
        Reset the caches for value and policy computations.
        """
        self.value_cache.clear()
        self.policy_cache.clear()

    def get_weights(self):
        """
        Get the current weights and biases of the value and policy networks.
        """
        return {
            'value_weights': self.value_weights,
            'value_biases': self.value_biases,
            'policy_weights': self.policy_weights,
            'policy_biases': self.policy_biases
        }

    def get_network_info(self):
        """Get information about network architecture."""

        def count_params(weights, biases):
            return sum(w.size + b.size for w, b in zip(weights, biases))

        return {
            'state_dim': self.state_dim,
            'action_dim': self.action_dim,
            'value_architecture': [self.state_dim] + self.state_layers + [1],
            'policy_architecture': [self.state_dim] + self.policy_layers + [self.action_dim],
            'value_parameters': count_params(self.value_weights, self.value_biases),
            'policy_parameters': count_params(self.policy_weights, self.policy_biases)
        }

    def set_exploration_noise(self, noise_level):
        """Adjust exploration noise level."""
        self.exploration_noise = noise_level


    def get_policy_matrix_approximation(self, state_range=(-3, 3), grid_size=50):
        """
        Approximate the learned policy as a linear controller: u = -K_learned * x
        by evaluating the network on a grid and fitting a linear model.
        """
        # Generate grid of states
        if self.state_dim == 2:
            x1 = np.linspace(state_range[0], state_range[1], grid_size)
            x2 = np.linspace(state_range[0], state_range[1], grid_size)
            X1, X2 = np.meshgrid(x1, x2)
            states = np.column_stack([X1.ravel(), X2.ravel()])
        else:
            # For higher dimensions, use random sampling
            states = np.random.uniform(state_range[0], state_range[1], (grid_size ** 2, self.state_dim))

        # Get actions from neural network
        actions = []
        for state in states:
            action = self.get_action(state, training=False)
            actions.append(action.flatten())

        actions = np.array(actions)

        # Fit linear model: action = -K * state (adding bias term)
        # Using least squares: K = -(X^T X)^(-1) X^T u
        X_with_bias = np.column_stack([states, np.ones(states.shape[0])])
        K_with_bias = -np.linalg.lstsq(X_with_bias, actions, rcond=None)[0]

        K_learned = K_with_bias[:-1]  # Remove bias term
        bias = K_with_bias[-1]

        # Calculate R-squared to see how linear the policy is
        actions_pred = states @ K_learned.T + bias
        ss_res = np.sum((actions - actions_pred) ** 2)
        ss_tot = np.sum((actions - np.mean(actions)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        return K_learned, bias, r_squared


    def compare_with_optimal_lqr(self, env, state_range=(-3, 3), num_samples=100):
        """Compare learned policy with optimal LQR policy."""

        # Get learned policy approximation
        K_learned, bias, r_squared = self.get_policy_matrix_approximation(state_range, int(np.sqrt(num_samples)))
        K_optimal = env.K

        print("=== Policy Comparison ===")
        print(f"Optimal LQR gain matrix K:")
        print(K_optimal)
        print(f"\nLearned policy gain matrix K (linear approximation):")
        print(K_learned)
        print(f"Bias term: {bias}")
        print(f"Linearity (R²): {r_squared:.4f}")

        # Compare on random states
        states = np.random.uniform(state_range[0], state_range[1], (num_samples, self.state_dim))

        errors = []
        for state in states:
            # Learned action
            action_learned = self.get_action(state, training=False).flatten()

            # Optimal action
            action_optimal = env.get_lqr_action(state)

            error = np.linalg.norm(action_learned - action_optimal)
            errors.append(error)

        print(f"\nAction comparison on {num_samples} random states:")
        print(f"Mean absolute error: {np.mean(errors):.4f}")
        print(f"Max absolute error: {np.max(errors):.4f}")
        print(f"Std of errors: {np.std(errors):.4f}")

        return K_learned, K_optimal, errors


if __name__ == "__main__":
    # Example usage and simple test
    from LQR_env import LQR_Env

    # Create LQR environment
    A = np.array([[0.0, 1.0], [-1.0, -1.0]])
    B = np.array([[0.0], [1.0]])
    Q = np.eye(2)
    R = np.array([[1.0]])
    noise_std = 0.1

    env = LQR_Env(A, B, Q, R, noise_std)

    # Create neural controller
    value_layers = [64, 32]
    policy_layers = [64, 32]
    state_dim = 2
    action_dim = 1
    learning_rate = 0.01

    controller = NeuralControllerEst(value_layers, policy_layers, state_dim, action_dim, learning_rate)

    # Train for several episodes
    print("Training neural controller on LQR environment...")
    for episode in range(50):
        result = controller.train_episode(env, max_steps=100)

        if episode % 10 == 0:
            print(f"Episode {episode}: Reward={result['total_reward']:.2f}, "
                  f"Steps={result['steps']}, "
                  f"Value Loss={result['avg_value_loss']:.4f}, "
                  f"Policy Loss={result['avg_policy_loss']:.4f}")

    print("\nTraining completed!")

    # Test learned policy vs optimal LQR
    print("\nTesting learned policy vs optimal LQR:")
    state = env.reset().flatten()

    # Neural controller action
    nn_action = controller.get_action(state, training=False)
    print(f"Neural Controller Action: {nn_action.flatten()}")

    # Optimal LQR action
    lqr_action = env.get_lqr_action(state)
    print(f"Optimal LQR Action: {lqr_action}")

    # Compare values
    nn_value = controller.compute_value(state)[0, 0]
    true_value = env.get_true_value(state)
    print(f"Neural Controller Value: {nn_value:.4f}")
    print(f"True Optimal Value: {true_value:.4f}")