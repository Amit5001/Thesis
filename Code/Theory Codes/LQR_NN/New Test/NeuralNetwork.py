import numpy as np


class ActivationFunctions:
    @staticmethod
    def relu(x):
        return np.maximum(0, x)

    @staticmethod
    def relu_derivative(x):
        return (x > 0).astype(float)

    @staticmethod
    def tanh(x):
        return np.tanh(x)

    @staticmethod
    def tanh_derivative(x):
        return 1 - np.tanh(x) ** 2

    @staticmethod
    def softmax(x):
        # Numerical stability: subtract max
        exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=-1, keepdims=True)

    @staticmethod
    def linear(x):
        return x

    @staticmethod
    def linear_derivative(x):
        return np.ones_like(x)


class Layer:
    def __init__(self, input_size, output_size, activation='relu'):
        # Xavier initialization
        self.weights = np.random.randn(input_size, output_size) * np.sqrt(2.0 / input_size)
        self.biases = np.zeros((1, output_size))

        # Set activation function
        if activation == 'relu':
            self.activation = ActivationFunctions.relu
            self.activation_derivative = ActivationFunctions.relu_derivative
        elif activation == 'tanh':
            self.activation = ActivationFunctions.tanh
            self.activation_derivative = ActivationFunctions.tanh_derivative
        elif activation == 'linear':
            self.activation = ActivationFunctions.linear
            self.activation_derivative = ActivationFunctions.linear_derivative

        # Store for backpropagation
        self.last_input = None
        self.last_z = None  # Before activation
        self.last_output = None  # After activation

    def forward(self, x):
        self.last_input = x
        self.last_z = np.dot(x, self.weights) + self.biases
        self.last_output = self.activation(self.last_z)
        return self.last_output

    def backward(self, gradient_output):
        # gradient_output: gradient flowing back from next layer

        # Gradient w.r.t. activation input
        gradient_z = gradient_output * self.activation_derivative(self.last_z)

        # Gradients w.r.t. parameters
        gradient_weights = np.dot(self.last_input.T, gradient_z)
        gradient_biases = np.sum(gradient_z, axis=0, keepdims=True)

        # Gradient w.r.t. input (for previous layer)
        gradient_input = np.dot(gradient_z, self.weights.T)

        return gradient_input, gradient_weights, gradient_biases


class NeuralNetwork:
    def __init__(self, layer_sizes, activations=None):
        """
        layer_sizes: list of layer sizes [input_size, hidden1, hidden2, ..., output_size]
        activations: list of activation functions for each layer (except input)
        """
        self.layers = []

        if activations is None:
            # Default: ReLU for hidden layers, linear for output
            activations = ['relu'] * (len(layer_sizes) - 2) + ['linear']

        for i in range(len(layer_sizes) - 1):
            layer = Layer(layer_sizes[i], layer_sizes[i + 1], activations[i])
            self.layers.append(layer)

    def forward(self, x):
        """Forward pass through network"""
        current_input = x
        for layer in self.layers:
            current_input = layer.forward(current_input)
        return current_input

    def backward(self, gradient_output):
        """Backward pass through network"""
        gradients = []
        current_gradient = gradient_output

        # Backpropagate through layers in reverse order
        for layer in reversed(self.layers):
            grad_input, grad_weights, grad_biases = layer.backward(current_gradient)
            gradients.append((grad_weights, grad_biases))
            current_gradient = grad_input

        # Reverse to match layer order
        gradients.reverse()
        return gradients


class SGDOptimizer:
    def __init__(self, learning_rate=0.01):
        self.learning_rate = learning_rate

    def update(self, network, gradients):
        """Update network parameters using gradients"""
        for layer, (grad_weights, grad_biases) in zip(network.layers, gradients):
            layer.weights -= self.learning_rate * grad_weights
            layer.biases -= self.learning_rate * grad_biases


class AdamOptimizer:
    def __init__(self, learning_rate=0.001, beta1=0.9, beta2=0.999, epsilon=1e-8):
        self.learning_rate = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.m_weights = []  # First moment
        self.v_weights = []  # Second moment
        self.m_biases = []
        self.v_biases = []
        self.t = 0  # Time step
        self.initialized = False

    def update(self, network, gradients):
        """Update network parameters using Adam optimization"""
        if not self.initialized:
            # Initialize moment estimates
            for layer in network.layers:
                self.m_weights.append(np.zeros_like(layer.weights))
                self.v_weights.append(np.zeros_like(layer.weights))
                self.m_biases.append(np.zeros_like(layer.biases))
                self.v_biases.append(np.zeros_like(layer.biases))
            self.initialized = True

        self.t += 1

        for i, (layer, (grad_weights, grad_biases)) in enumerate(zip(network.layers, gradients)):
            # Update biased first moment estimate
            self.m_weights[i] = self.beta1 * self.m_weights[i] + (1 - self.beta1) * grad_weights
            self.m_biases[i] = self.beta1 * self.m_biases[i] + (1 - self.beta1) * grad_biases

            # Update biased second moment estimate
            self.v_weights[i] = self.beta2 * self.v_weights[i] + (1 - self.beta2) * grad_weights ** 2
            self.v_biases[i] = self.beta2 * self.v_biases[i] + (1 - self.beta2) * grad_biases ** 2

            # Compute bias-corrected moment estimates
            m_w_corrected = self.m_weights[i] / (1 - self.beta1 ** self.t)
            m_b_corrected = self.m_biases[i] / (1 - self.beta1 ** self.t)
            v_w_corrected = self.v_weights[i] / (1 - self.beta2 ** self.t)
            v_b_corrected = self.v_biases[i] / (1 - self.beta2 ** self.t)

            # Update parameters
            layer.weights -= self.learning_rate * m_w_corrected / (np.sqrt(v_w_corrected) + self.epsilon)
            layer.biases -= self.learning_rate * m_b_corrected / (np.sqrt(v_b_corrected) + self.epsilon)


# Example usage and test
if __name__ == "__main__":
    # Test with simple data
    np.random.seed(42)

    # Create simple regression problem: y = x1 + 2*x2
    X = np.random.randn(100, 2)
    y = X[:, 0] + 2 * X[:, 1] + 0.1 * np.random.randn(100)
    y = y.reshape(-1, 1)

    # Create network: 2 inputs -> 10 hidden -> 1 output
    network = NeuralNetwork([2, 10, 1], ['relu', 'linear'])
    optimizer = SGDOptimizer(learning_rate=0.01)

    # Training loop
    for epoch in range(2000):
        # Forward pass
        predictions = network.forward(X)

        # Compute loss (MSE)
        loss = np.mean((predictions - y) ** 2)

        # Compute gradient of loss w.r.t. output
        gradient_output = 2 * (predictions - y) / len(X)

        # Backward pass
        gradients = network.backward(gradient_output)

        # Update parameters
        optimizer.update(network, gradients)

        if epoch % 100 == 0:
            print(f"Epoch {epoch}, Loss: {loss:.4f}")

    # Test predictions
    print("\nFinal predictions vs targets (first 5 samples):")
    final_predictions = network.forward(X)
    final_predictions = final_predictions.reshape(-1, 1)
    y_true = y = X[:, 0] + 2 * X[:, 1]
    y_true= y.reshape(-1, 1)

    # calculate the error:
    error = (final_predictions - y_true)
    print(max(error))