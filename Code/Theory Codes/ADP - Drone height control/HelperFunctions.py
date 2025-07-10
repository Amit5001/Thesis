import numpy as np
import scipy as sp

def create_N_matrix(n):
    N = np.zeros((n ** 2, (n ** 2 + n) // 2))
    count = 0
    for j in range(n):
        for p in range(j, n):
            N[j * n + p, count] = 1
            if j != p:
                N[p * n + j, count] = 1
            count += 1
    return N


def svec(matrix):
    """
    Vectorize the upper triangular part of a symmetric matrix, including the diagonal elements.

    Parameters:
    matrix (np.ndarray): The input symmetric matrix to be vectorized.

    Returns:
    np.ndarray: The vectorized form of the upper triangular part of the input matrix.
    """
    n = matrix.shape[0]
    svec_result = []
    for i in range(n):
        for j in range(i, n):
            svec_result.append(matrix[i, j])
    return np.array(svec_result)


def vec(matrix):
    """
    Vectorize a matrix column-wise.

    Parameters:
    matrix (np.ndarray): The input matrix to be vectorized.

    Returns:
    np.ndarray: The vectorized form of the input matrix.
    """
    return matrix.flatten('F')


def vec2matrix(vector):
    """
    Convert a vectorized matrix back to its original matrix form.

    Parameters:
    vector (np.ndarray): The input vectorized matrix.

    Returns:
    np.ndarray: The original matrix form of the input vector.
    """
    n_ = int(np.sqrt(len(vector)))
    matrix = np.zeros((n_, n_))
    count = 0
    for k in range(n_):
        for j in range(n_):
            matrix[k, j] = vector[count]
            count += 1
    return matrix


def svec2matrix(vector):
    """
    Convert a vectorized symmetric matrix back to its original matrix form.

    Parameters:
    vector (np.ndarray): The input vectorized symmetric matrix.

    Returns:
    np.ndarray: The original symmetric matrix form of the input vector.
    """

    n_ = int(np.sqrt(2 * len(vector)))
    matrix = np.zeros((n_, n_))
    count = 0
    for i in range(n_):
        for j in range(i, n_):
            matrix[i, j] = vector[count]
            matrix[j, i] = vector[count]
            count += 1
    return matrix


def create_input_signal(t, min_val=1000, max_val=2000, low_val=1400, high_val=1800,
                        initial_ramp_time=20, cycle_time=20, noise_std=100, noise_freq=100):
    """
    Create an input signal with frequency-controlled noise

    Parameters:
    -----------
    t : array-like
        Time vector
    min_val, max_val : float
        Min and max values of the signal
    low_val, high_val : float
        Lower and higher values in the cycling pattern
    initial_ramp_time : float
        Time to ramp from min_val to max_val
    cycle_time : float
        Time for one complete cycle
    noise_std : float
        Standard deviation of the noise (amplitude)
    noise_freq : float
        Frequency of the noise in Hz
    """
    dt = t[1] - t[0]

    # Create base signal
    u = np.zeros_like(t)

    # Initial ramp up
    initial_ramp_idx = int(initial_ramp_time / dt)
    u[:initial_ramp_idx] = np.linspace(min_val, max_val, initial_ramp_idx)

    # Cycling pattern
    half_cycle = int(cycle_time / 2 / dt)
    cycle = np.concatenate([
        np.linspace(max_val, low_val, half_cycle),
        np.linspace(low_val, high_val, half_cycle)
    ])

    # Fill remaining time with cycles
    remaining_points = len(t) - initial_ramp_idx
    num_complete_cycles = remaining_points // len(cycle)
    remaining_samples = remaining_points % len(cycle)

    for i in range(num_complete_cycles):
        start_idx = initial_ramp_idx + i * len(cycle)
        end_idx = start_idx + len(cycle)
        u[start_idx:end_idx] = cycle

    if remaining_samples > 0:
        start_idx = initial_ramp_idx + num_complete_cycles * len(cycle)
        u[start_idx:] = cycle[:remaining_samples]

    # Generate frequency-controlled noise
    # Basic white noise
    noise = np.random.normal(0, noise_std, size=len(t))
    # Add frequency component
    noise = noise * np.sin(2 * np.pi * noise_freq * t)

    # Add noise to signal
    u = u + noise

    return u

# Example usage:
# t = np.linspace(0, 100, 10000)  # 100 seconds with 10000 points
# Low frequency noise:
# u = create_input_signal(t, noise_std=50, noise_freq=1)  # 1 Hz noise
# High frequency noise:
# u = create_input_signal(t, noise_std=50, noise_freq=50)  # 50 Hz noise


def apply_highpass_filter(data, cutoff_freq, fs, order=2):
    nyquist = fs / 2
    normal_cutoff = cutoff_freq / nyquist
    b, a = sp.signal.butter(order, normal_cutoff, btype='high')
    filtered_data = sp.signal.lfilter(b, a, data)
    return filtered_data


def apply_butter_filter(data, cutoff, fs, order=2, btype='low'):
    nyquist = 0.5 * fs
    if isinstance(cutoff, (list, tuple)):  # for bandpass/bandstop
        normal_cutoff = [c / nyquist for c in cutoff]
    else:
        normal_cutoff = cutoff / nyquist

    b, a = sp.signal.butter(order, normal_cutoff, btype=btype, analog=False)
    return sp.signal.filtfilt(b, a, data)


# Basic FFT
def apply_fft(data, sampling_rate):
    # Compute FFT
    fft_values = np.fft.fft(data)

    # Compute frequency bins
    freqs = np.fft.fftfreq(len(data), 1 / sampling_rate)

    # Get magnitude spectrum (absolute values)
    magnitude = np.abs(fft_values)

    # Get phase spectrum
    phase = np.angle(fft_values)

    return freqs, magnitude, phase