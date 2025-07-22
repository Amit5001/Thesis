''' 
This script will learn the distribution of the LQR controller generated in the Mass-Spring Generate data.py script.
It is not for imitation learning but rather for learning the distribution of the controller's actions.
It is important to note that this is an Offline learning test for approximating the distribution of the actions.


Lets say we have trajectories of the form: D = {x_t, u_t} where x_t is the state at time t and u_t is the action at time t.
We will use a neural network to learn the distribution of the actions given the states.
The neural network will output the parameters of a Gaussian distribution, which we will use to sample actions.
The loss function will be the negative log likelihood of the actions given the states. 
L = -log(P(u_t | x_t)) where P is the Gaussian distribution.


MDP definition:
- States: x_t = [position, velocity, integral_error]
- Actions: u_t = [force]
- Transition: For the mass-spring system is deterministic. But we want to learn something else.


What we try to learn here:
    Depends on the distributional assumption:
        * Gaussian: Learn μ(s), σ(s)
        * Mixture of Gaussians: Learn {μᵢ(s), σᵢ(s), πᵢ(s)}
        * Flow-based: Learn transformation parameters θ(s)
        * Non-parametric: Learn energy function E(s,a)

    1. Conditional VAE (CVAE)

    Learn p(a|s) by encoding actions into latent z
    Decoder outputs distribution parameters (μ, σ for Gaussian)
    Can capture multimodal distributions

    2. Normalizing Flows

    Learn exact likelihood p(a|s) through invertible transformations
    More flexible than simple Gaussian assumptions
    Can model complex, non-Gaussian distributions

    3. Energy-Based Models (EBMs)

    Learn unnormalized log-density of π(a|s)
    No restrictive distributional assumptions
    Can capture arbitrary distributions

    4. Mixture Density Networks (MDN)

    Output mixture of Gaussians: multiple (μᵢ, σᵢ, πᵢ) per state
    Good for multimodal policies
    Simpler than flows but more flexible than single Gaussian


    I will try to use the Mixture Density Networks (MDN) approach to learn the distribution of the actions.
    Archtecture:
    Input: State x_t
    Hidden layers: Fully connected layers with ReLU activation
    Output: Parameters of a mixture of Gaussians (μᵢ, σᵢ, πᵢ) 
            πᵢ is the mixing coefficient for the i-th Gaussian component in the mixture. 
            It represents the weight of the i-th component in the overall mixture distribution and must sum to 1 across all components.
            μᵢ and σᵢ are the mean and standard deviation of the i-th Gaussian component.

    Loss: Negative log likelihood of the actions given the states. 
            L = -log(P(u_t | x_t)) where P is the Gaussian distribution.
    Optimizer: Adam or SGD
    Evaluation: Check if the learned distribution matches the true distribution of the actions.

    Hyperparameters:
    num_components: Number of Gaussian components in the mixture
    hidden_size: Size of the hidden layers
    learning_rate: Learning rate for the optimizer
    num_epochs: Number of epochs for training
    batch_size: Size of the training batches
    input_size: Size of the input state vector (3 for [position, velocity, integral_error])
    output_size: Size of the output vector (3 * num_components for [μᵢ, σᵢ, πᵢ] for each component)


    MDN can be implemented like DQN, but instead of outputting Q-values, it outputs the parameters of a Gaussian distribution.
        Same as DQN:
        - Experience replay buffer
        - Network architecture (except final layer)
        - Training loop structure

        Different:
        - Output: {π₁, μ₁, σ₁, ..., πₖ, μₖ, σₖ} instead of Q-values
        - Loss: -log p(u|s) instead of TD error
        - No target network needed (supervised learning)        
'''

"""
Another approach is to use a Conditional Variational Autoencoder (CVAE) to learn the distribution of the actions.
The CVAE can capture the conditional dependencies between the states and actions, allowing for more accurate action generation.
The architecture is similar to the MDN, but with an additional encoder network to learn the latent representation of the actions.

Another approach which is more RL-like is Distributional offline RL, where we learn a distribution over actions given states.
"""