#%%

import numpy as np
import pandas as pd
import scipy as sp
from scipy.signal import butter, lfilter
from scipy.integrate import cumulative_trapezoid

import os
from HelperFunctions import *

import matplotlib.pyplot as plt
%matplotlib inline


#%%
base_path = os.getcwd()
data_path = os.path.join(base_path, 'Data')
data_files = os.listdir(data_path)

#%%
df = pd.read_csv(os.path.join(data_path, data_files[0]))

#%%
# Checking how many zeros we have in the lidar distance
num_zeros = (df['_current_lidar_distance_distance'] == 0).sum()
print("Precentage of zeros in lidar distance: {:.2f}%".format((num_zeros / len(df)) * 100))

#%%
# Removing all the rows where the lidar distance is zero. putting it on a new df
df_non_zero = df[df['_current_lidar_distance_distance'] != 0]

# Removing last 25 rows -- The battery was dead.
# Reseting the index of the dataframe
df_non_zero = df_non_zero[df_non_zero['time_sec'] < 380]
df_non_zero.reset_index(drop=True, inplace=True)

# %%
x_cols = ['_current_lidar_distance_distance','_drone_header_current']
u_cols = ['_rc_channel_data_data[2]'] # This is the Thrust PWM value
dt = df_non_zero['time_sec'].reset_index(drop=True)

x = df_non_zero[x_cols]
u = df_non_zero[u_cols]

# Renaming the columns for clarity
x.columns = ['distance', 'current']
u.columns = ['thrust_pwm']  # This is the Thrust PWM value


# %%
# Reset index to ensure proper alignment
x = x.reset_index(drop=True)
dt = dt.reset_index(drop=True)

# Calculate derivative using central difference
def calculate_derivative(signal, time):
    """Calculate derivative using central difference for interior points"""
    deriv = np.zeros_like(signal)
    
    # Central difference for interior points
    deriv[1:-1] = (signal.iloc[2:].values - signal.iloc[:-2].values) / (time.iloc[2:].values - time.iloc[:-2].values)
    
    # Forward difference for first point
    deriv[0] = (signal.iloc[1] - signal.iloc[0]) / (time.iloc[1] - time.iloc[0])
    
    # Backward difference for last point
    deriv[-1] = (signal.iloc[-1] - signal.iloc[-2]) / (time.iloc[-1] - time.iloc[-2])
    
    return deriv

# Calculate derivative
x['distance_dot'] = calculate_derivative(x['distance'], dt)

# Calculate integral using trapezoidal rule (handles variable dt correctly)
x['distance_int'] = np.concatenate([[0], cumulative_trapezoid(x['distance'], dt)])

# %%
#plotting the lidar data vs time. Doint it as 3 subplots
plt.figure(figsize=(12, 8))
plt.subplot(3, 1, 1)
plt.plot(dt, x['distance'], label='Lidar Distance', color='blue')
plt.xlabel('Time (s)')
plt.ylabel('Distance (m)')
plt.title('Lidar Distance Over Time')
plt.legend()
plt.grid()
plt.figure(figsize=(12, 8))
plt.subplot(3, 1, 2)
plt.plot(dt, x['distance_dot'], label='Distance Derivative', color='orange')
plt.xlabel('Time (s)')
plt.ylabel('Distance Derivative (m/s)')
plt.title('Distance Derivative Over Time')
plt.legend()
plt.grid()
plt.figure(figsize=(12, 8))
plt.subplot(3, 1, 3)
plt.plot(dt, x['distance_int'], label='Distance Integral', color='green')
plt.xlabel('Time (s)')
plt.ylabel('Distance Integral (m·s)')
plt.title('Distance Integral Over Time')
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

# %%
# Plotting the thrust pwm vs time
plt.figure(figsize=(12, 4))
plt.plot(dt, u['thrust_pwm'], label='Thrust PWM', color='red')
plt.xlabel('Time (s)')
plt.ylabel('Thrust PWM')
plt.title('Thrust PWM Over Time')
plt.legend()
plt.grid()
plt.show()
# %%
print(f"Final time: {dt.iloc[-1]:.2f}s")
print(f"Data points: {len(dt)}")
# %%
