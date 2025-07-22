# This script generates trajectories of a stabilizing policy for a mass-spring system.
# The designed controller is an LQR controller with integral action.


import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from control import lqr
import pandas as pd

# ==== System Parameters ====
m = 1.0  # mass
k = 1.0  # spring constant

# LQR cost
Q = np.diag([10, 1, 500])
R = np.array([[1]])


# Define step reference that switches every π/ω seconds
def x_ref(t_local):
    period = 2 * np.pi / omega
    half_period = period / 2
    n = int(t_local // half_period)
    return A if n % 2 == 0 else -A

# System dynamics for this block
def dynamics(t, state):
    x1, x2, x3 = state
    ref = x_ref(t)
    e = x1 - ref
    x_aug = np.array([x1, x2, x3])
    u = -K_lqr @ x_aug
    dx1 = x2
    dx2 = (-k * x1 + u) / m
    dx3 = e
    return [dx1, dx2, dx3]


# LQR system matrices
A_sys = np.array([[0, 1], [-k/m, 0]])
B_sys = np.array([[0], [1/m]])

A_aug = np.block([
    [A_sys,              np.zeros((2,1))],
    [np.array([[1, 0]]), np.zeros((1,1))]
])
B_aug = np.vstack([B_sys, [[0]]])
K_lqr, _, _ = lqr(A_aug, B_aug, Q, R)
K_lqr = np.asarray(K_lqr).flatten()

# ==== Simulation Control ====
block_duration = 20.0      # seconds
num_blocks = 50            # total steps
dt = 0.01
x0 = [0.0, 0.0, 0.0]       # initial state

# For dataset
all_t = []
all_x = []
all_u = []
all_ref = []
all_meta = []  # (A, omega) for each time

# ==== Run Multiple Blocks ====
for block in range(num_blocks):
    # Random amplitude and frequency for this block
    A = np.random.uniform(0.1, 0.8)
    omega = np.random.uniform(0.3, 1)


    # Simulate this block
    t_start = block * block_duration
    t_end = (block + 1) * block_duration
    t_eval = np.arange(t_start, t_end, dt)
    t_local_eval = np.arange(0, block_duration, dt)

    sol = solve_ivp(dynamics, (0, block_duration), x0, t_eval=t_local_eval, rtol=1e-6, atol=1e-8)
    x = sol.y
    t = sol.t + t_start

    # Compute reference and control
    ref_vals = np.array([x_ref(ti) for ti in sol.t])
    u_vals = -K_lqr[0]*x[0] - K_lqr[1]*x[1] - K_lqr[2]*x[2]

    # Save data
    all_t.append(t)
    all_x.append(x.T)
    all_u.append(u_vals)
    all_ref.append(ref_vals)
    all_meta.append(np.full_like(t, A).reshape(-1, 1))  # amplitude
    all_meta.append(np.full_like(t, omega).reshape(-1, 1))  # frequency

    # Set initial condition for next block
    x0 = x[:, -1]

# ==== Concatenate Data ====
T = np.concatenate(all_t)
X = np.concatenate(all_x)
U = np.concatenate(all_u)
REF = np.concatenate(all_ref)
A_vals = np.concatenate(all_meta[::2])
omega_vals = np.concatenate(all_meta[1::2])

# # ==== Example Plot ====
# plt.figure(figsize=(12, 5))
# plt.plot(T, X[:, 0], label='x(t)')
# plt.plot(T, REF, label='x_ref(t)', linestyle='--')
# plt.xlabel('Time [s]')
# plt.title('Tracking of Random Step Signals')
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.show()

# ==== Saving (Optional) ====
df = pd.DataFrame({
    'time': T,
    'x': X[:, 0],
    'x_dot': X[:, 1],
    'integral_error': X[:, 2],
    'u': U,
    'x_ref': REF,
    'amplitude': A_vals.flatten(),
    'omega': omega_vals.flatten()
})
# Check if the file already exists, if so, append to it
try:
    df.to_csv('mass_spring_lqr_dataset.csv', mode='x', index=False)
except FileExistsError:
    print("File already exists, appending to it.")
    df.to_csv('mass_spring_lqr_dataset.csv', mode='a', header=False, index=False)
else:
    print("✅ Dataset saved: mass_spring_lqr_dataset.csv")
    # If the file doesn't exist, it will be created
print("✅ Dataset saved: mass_spring_lqr_dataset.csv")
