import numpy as np
from NeuralNetwork import NeuralNetwork, AdamOptimizer


class ValueNetwork:
    """Neural network that estimates state values V(s)"""

    def __init__(self, state_size, hidden_sizes=[64]):
        """
        state_size: dimensionality of state space
        hidden_sizes: list of hidden layer sizes
        """
        self.state_size = state_size

        # Build network: state -> scalar value
        layer_sizes = [state_size] + hidden_sizes + [1]
        activations = ['relu'] * len(hidden_sizes) + ['linear']  # Linear output for value

        self.network = NeuralNetwork(layer_sizes, activations)

        # Store for gradient computation
        self.last_states = None
        self.last_values = None

    def forward(self, states):
        """
        Forward pass: states -> value estimates
        Returns scalar value estimates
        """
        # Ensure states is 2D (batch_size, state_size)
        if states.ndim == 1:
            states = states.reshape(1, -1)

        # Forward through network
        values = self.network.forward(states)

        # Store for backward pass
        self.last_states = states
        self.last_values = values

        return values.flatten()  # Return as 1D array

    def get_value(self, state):
        """Get value estimate for single state"""
        value = self.forward(state)
        return value[0]

    def compute_value_loss(self, states, targets):
        """
        Compute MSE loss: L = (target - V(s))^2

        states: batch of states
        targets: target values (returns G)

        Returns gradients and loss
        """
        # Forward pass
        predicted_values = self.forward(states)

        # MSE loss
        errors = targets - predicted_values
        loss = np.mean(errors ** 2)

        # Gradient of MSE w.r.t. predictions: -2(target - prediction) / batch_size
        grad_output = -2 * errors.reshape(-1, 1) / len(states)

        # Backpropagate through network
        gradients = self.network.backward(grad_output)

        return gradients, loss

    def compute_advantages(self, states, rewards, next_states, dones, gamma=0.99):
        """
        Compute advantages using TD error: A = r + γV(s') - V(s)

        states: current states
        rewards: immediate rewards
        next_states: next states
        dones: episode termination flags
        gamma: discount factor

        Returns advantages
        """
        current_values = self.forward(states)
        next_values = self.forward(next_states)

        # TD targets: r + γV(s') * (1 - done)
        td_targets = rewards + gamma * next_values * (1 - dones)

        # Advantages: TD error
        advantages = td_targets - current_values

        return advantages


# Test the value network
if __name__ == "__main__":
    # Test with CartPole state size
    # Setup
    state_size = 4
    value_net = ValueNetwork(state_size, hidden_sizes=[32])
    optimizer = AdamOptimizer(learning_rate=0.001)

    # Generate training data
    num_episodes = 50
    batch_size = 10

    print("Training Value Network...")
    for episode in range(num_episodes):
        # Generate random batch
        batch_states = np.random.randn(batch_size, state_size)
        # Simulate target returns (normally from actual episodes)
        target_returns = np.random.randn(batch_size) * 2

        # Compute loss and gradients
        gradients, loss = value_net.compute_value_loss(batch_states, target_returns)

        # Update network
        optimizer.update(value_net.network, gradients)

        if episode % 10 == 0:
            print(f"Episode {episode}, Loss: {loss:.4f}")

    # Test final performance
    test_state = np.random.randn(4)
    value = value_net.get_value(test_state)
    print(f"\nFinal state value: {value:.4f}")

    # Test advantages
    batch_states = np.random.randn(5, 4)
    rewards = np.array([1.0, 0.0, 1.0, 0.0, 1.0])
    next_states = np.random.randn(5, 4)
    dones = np.array([0, 0, 0, 0, 1])

    advantages = value_net.compute_advantages(batch_states, rewards, next_states, dones)
    print(f"Final advantages: {advantages}")