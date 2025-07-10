import numpy as np
from NeuralNetwork import NeuralNetwork, ActivationFunctions


class PolicyNetwork:
    """Neural network that outputs action probabilities"""

    def __init__(self, state_size, action_size, hidden_sizes=[64]):
        """
        state_size: dimensionality of state space
        action_size: number of discrete actions
        hidden_sizes: list of hidden layer sizes
        """
        self.state_size = state_size
        self.action_size = action_size

        # Build network architecture
        layer_sizes = [state_size] + hidden_sizes + [action_size]
        activations = ['relu'] * len(hidden_sizes) + ['linear']  # Linear output for softmax

        self.network = NeuralNetwork(layer_sizes, activations)

        # Store last outputs for gradient computation
        self.last_logits = None
        self.last_action_probs = None
        self.last_state = None

    def forward(self, state):
        """
        Forward pass: state -> action probabilities
        Returns action probabilities (softmax)
        """
        # Ensure state is 2D (batch_size, state_size)
        if state.ndim == 1:
            state = state.reshape(1, -1)

        # Forward through network to get logits
        logits = self.network.forward(state)

        # Apply softmax to get probabilities
        action_probs = ActivationFunctions.softmax(logits)

        # Store for backward pass
        self.last_logits = logits
        self.last_action_probs = action_probs
        self.last_state = state

        return action_probs

    def sample_action(self, state):
        """
        Sample action from policy distribution
        Returns: (action, log_prob)
        """
        action_probs = self.forward(state)

        # Sample action from categorical distribution
        action = np.random.choice(self.action_size, p=action_probs.flatten())

        # Calculate log probability
        log_prob = self.get_log_prob(action)

        return action, log_prob

    def get_action_probs(self, state):
        """Get action probabilities without sampling"""
        return self.forward(state)

    def get_log_prob(self, action):
        """Get log probability of specific action from last forward pass"""
        if self.last_action_probs is None:
            raise ValueError("Must call forward() before get_log_prob()")

        # Add small epsilon to prevent log(0)
        epsilon = 1e-8
        prob = self.last_action_probs[0, action] + epsilon
        return np.log(prob)

    def compute_policy_gradient(self, states, actions, advantages):
        """
        Compute policy gradient: ∇L = -log π(a|s) * A

        states: batch of states
        actions: batch of actions taken
        advantages: batch of advantage values

        Returns gradients for network parameters
        """
        batch_size = len(states)

        # Forward pass for entire batch
        action_probs = self.forward(states)

        # Compute log probabilities for taken actions
        epsilon = 1e-8
        log_probs = np.log(action_probs[range(batch_size), actions] + epsilon)

        # Policy gradient loss: -log π(a|s) * A
        policy_loss = -np.mean(log_probs * advantages)

        # Compute gradient of loss w.r.t. action probabilities
        grad_action_probs = np.zeros_like(action_probs)
        for i in range(batch_size):
            grad_action_probs[i, actions[i]] = -advantages[i] / (action_probs[i, actions[i]] + epsilon)
        grad_action_probs /= batch_size

        # Convert softmax gradient to logits gradient
        grad_logits = self._softmax_gradient(self.last_action_probs, grad_action_probs)

        # Backpropagate through network
        gradients = self.network.backward(grad_logits)

        return gradients, policy_loss

    def _softmax_gradient(self, softmax_output, grad_output):
        """
        Convert gradient w.r.t. softmax output to gradient w.r.t. logits
        For softmax: if i==j: ∂softmax_i/∂logit_j = softmax_i(1-softmax_i)
                     if i!=j: ∂softmax_i/∂logit_j = -softmax_i*softmax_j
        """
        batch_size, num_classes = softmax_output.shape
        grad_logits = np.zeros_like(softmax_output)

        for b in range(batch_size):
            s = softmax_output[b]  # Softmax output for this sample
            g = grad_output[b]  # Gradient for this sample

            # Jacobian of softmax
            jacobian = np.outer(s, s)  # s_i * s_j for all i,j
            jacobian[np.diag_indices_from(jacobian)] = s * (1 - s)  # Diagonal: s_i(1-s_i)
            jacobian = -jacobian  # Negative for off-diagonal
            jacobian[np.diag_indices_from(jacobian)] = s * (1 - s)  # Fix diagonal

            grad_logits[b] = jacobian @ g

        return grad_logits


class ContinuousPolicyNetwork(PolicyNetwork):
    def __init__(self, state_size, hidden_sizes=[64]):
        super().__init__(state_size, action_size=1, hidden_sizes=hidden_sizes)
        # Network outputs mean and log_std for Gaussian distribution
        layer_sizes = [state_size] + hidden_sizes + [2]  # [mean, log_std]
        self.network = NeuralNetwork(layer_sizes, ['relu'] * len(hidden_sizes) + ['linear'])

    def sample_action(self, state):
        output = self.network.forward(state)
        mean, log_std = output[0, 0], output[0, 1]
        std = np.exp(log_std)

        # Sample from Gaussian
        action = np.random.normal(mean, std)
        # Scale to [1000, 2000]
        action = 1000 + (action + 3) * 166.67  # Assuming action ∈ [-3,3]
        action = np.clip(action, 1000, 2000)

        return action, log_prob

# Test the policy network
if __name__ == "__main__":
    # Test with simple environment
    state_size = 4  # e.g., CartPole
    action_size = 2  # left/right

    policy = PolicyNetwork(state_size, action_size, hidden_sizes=[32])

    # Test forward pass
    test_state = np.random.randn(4)
    action_probs = policy.get_action_probs(test_state)
    print(f"Action probabilities: {action_probs}")
    print(f"Sum of probabilities: {np.sum(action_probs):.6f}")

    # Test action sampling
    action, log_prob = policy.sample_action(test_state)
    print(f"Sampled action: {action}, Log prob: {log_prob:.4f}")

    # Test batch gradient computation
    batch_states = np.random.randn(5, 4)
    batch_actions = np.array([0, 1, 0, 1, 0])
    batch_advantages = np.array([1.0, -0.5, 0.2, -1.0, 0.8])

    gradients, loss = policy.compute_policy_gradient(batch_states, batch_actions, batch_advantages)
    print(f"Policy loss: {loss:.4f}")
    print(f"Number of gradient sets: {len(gradients)}")