import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

# Read the CSV file
df = pd.read_csv('motor_data.csv')

# Sort the dataframe by "Time (s)" in ascending order
df = df.sort_values(by='Time (s)', ascending=True)

# Define the time range for Session 1
session_start_time = 62.78
session_end_time = 98.13

# Filter data for Session 1 only
session_df = df[(df['Time (s)'] >= session_start_time) & (df['Time (s)'] <= session_end_time)]

# Remove empty rows from Torque and Thrust data within this session
Torque_df = session_df.dropna(subset=['Torque (N·m)']).copy()
Thrust_df = session_df.dropna(subset=['Thrust (gf)']).copy()

# Now create a dataframe with rows that have BOTH torque and thrust data for the torque vs thrust analysis
torque_thrust_df = session_df.dropna(subset=['Torque (N·m)', 'Thrust (gf)']).copy()

# Convert thrust from gf to N in both dataframes
Thrust_df.loc[:, 'Thrust (N)'] = Thrust_df['Thrust (gf)'] * 0.00980665
torque_thrust_df.loc[:, 'Thrust (N)'] = torque_thrust_df['Thrust (gf)'] * 0.00980665

# Print information about the filtered data
print(f"Session 1 time range: {session_start_time} to {session_end_time} seconds")
print(f"Number of data points in session: {len(session_df)}")
print(f"Number of data points with Torque values: {len(Torque_df)}")
print(f"Number of data points with Thrust values: {len(Thrust_df)}")
print(f"Number of data points with both Torque and Thrust values: {len(torque_thrust_df)}")
print(f"ESC signal range: {session_df['ESC signal (µs)'].min()} to {session_df['ESC signal (µs)'].max()} µs")

# PART 1: TORQUE VS ESC SIGNAL
# For Torque, try both linear and polynomial fits
X_torque = Torque_df[['ESC signal (µs)']].values
y_torque = Torque_df['Torque (N·m)'].values

# Linear fit
torque_model_linear = LinearRegression()
torque_model_linear.fit(X_torque, y_torque)
torque_predictions_linear = torque_model_linear.predict(X_torque)
torque_r2_linear = torque_model_linear.score(X_torque, y_torque)

# Polynomial fit (degree 3)
torque_model_poly = make_pipeline(PolynomialFeatures(3), LinearRegression())
torque_model_poly.fit(X_torque, y_torque)
torque_predictions_poly = torque_model_poly.predict(X_torque)
torque_r2_poly = torque_model_poly.score(X_torque, y_torque)

# Get polynomial coefficients for torque vs ESC
poly_features_esc = torque_model_poly[0]
linear_reg_esc = torque_model_poly[1]
coefficients_esc = linear_reg_esc.coef_
intercept_esc = linear_reg_esc.intercept_

# PART 2: THRUST VS ESC SIGNAL
X_thrust = Thrust_df[['ESC signal (µs)']].values
y_thrust = Thrust_df['Thrust (N)'].values

thrust_model = LinearRegression()
thrust_model.fit(X_thrust, y_thrust)
thrust_predictions = thrust_model.predict(X_thrust)
thrust_r2 = thrust_model.score(X_thrust, y_thrust)

# PART 3: TORQUE VS THRUST
X_thrust_for_torque = torque_thrust_df[['Thrust (N)']].values  # Thrust is now the independent variable
y_torque_for_thrust = torque_thrust_df['Torque (N·m)'].values  # Torque is the dependent variable

# Linear fit for torque vs thrust
torque_thrust_model_linear = LinearRegression()
torque_thrust_model_linear.fit(X_thrust_for_torque, y_torque_for_thrust)
torque_thrust_predictions_linear = torque_thrust_model_linear.predict(X_thrust_for_torque)
torque_thrust_r2_linear = torque_thrust_model_linear.score(X_thrust_for_torque, y_torque_for_thrust)

# Polynomial fit (degree 2) for torque vs thrust
torque_thrust_model_poly = make_pipeline(PolynomialFeatures(2), LinearRegression())
torque_thrust_model_poly.fit(X_thrust_for_torque, y_torque_for_thrust)
torque_thrust_predictions_poly = torque_thrust_model_poly.predict(X_thrust_for_torque)
torque_thrust_r2_poly = torque_thrust_model_poly.score(X_thrust_for_torque, y_torque_for_thrust)

# Get polynomial coefficients for torque vs thrust
poly_features_thrust = torque_thrust_model_poly[0]
linear_reg_thrust = torque_thrust_model_poly[1]
coefficients_thrust = linear_reg_thrust.coef_
intercept_thrust = linear_reg_thrust.intercept_

# Print all equations and R² values
print("\n--- TORQUE VS ESC SIGNAL ---")
print(f"Linear Torque equation: Torque (N·m) = {torque_model_linear.coef_[0]:.6f} × ESC signal (µs) + {torque_model_linear.intercept_:.6f}")
print(f"Linear Torque equation R² = {torque_r2_linear:.4f}")
print(f"Polynomial Torque equation R² = {torque_r2_poly:.4f}")

print("\n--- THRUST VS ESC SIGNAL ---")
print(f"Thrust equation: Thrust (N) = {thrust_model.coef_[0]:.6f} × ESC signal (µs) + {thrust_model.intercept_:.6f}")
print(f"Thrust equation R² = {thrust_r2:.4f}")

print("\n--- TORQUE VS THRUST ---")
print(f"Linear equation: Torque (N·m) = {torque_thrust_model_linear.coef_[0]:.6f} × Thrust (N) + {torque_thrust_model_linear.intercept_:.6f}")
print(f"Linear equation R² = {torque_thrust_r2_linear:.4f}")
print(f"Polynomial equation R² = {torque_thrust_r2_poly:.4f}")
print(f"Polynomial equation: Torque (N·m) = {intercept_thrust:.6f} + {coefficients_thrust[1]:.6f} × Thrust (N) + {coefficients_thrust[2]:.6f} × Thrust(N)²")

# Create smooth sequences for polynomial curves
X_smooth_esc = np.linspace(X_torque.min(), X_torque.max(), 500).reshape(-1, 1)
y_smooth_poly_esc = torque_model_poly.predict(X_smooth_esc)

# Sort the X values for torque vs thrust for better visualization
sorted_indices = np.argsort(X_thrust_for_torque.flatten())
X_thrust_sorted = X_thrust_for_torque[sorted_indices]
y_torque_sorted = y_torque_for_thrust[sorted_indices]

X_smooth_thrust = np.linspace(X_thrust_for_torque.min(), X_thrust_for_torque.max(), 500).reshape(-1, 1)
y_smooth_poly_thrust = torque_thrust_model_poly.predict(X_smooth_thrust)

# PLOT 1: Torque vs ESC signal with both linear and polynomial fits
plt.figure(figsize=(8, 6))
plt.scatter(X_torque, y_torque, color='blue', label='Actual data')
plt.plot(X_torque, torque_predictions_linear, color='red', linestyle='--', label=f'Linear fit (R² = {torque_r2_linear:.4f})')
plt.plot(X_smooth_esc, y_smooth_poly_esc, color='green', label=f'Polynomial fit (R² = {torque_r2_poly:.4f})')
plt.xlabel('ESC signal (µs)')
plt.ylabel('Torque (N·m)')
plt.title('Torque vs ESC signal (Session 1)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig('torque_vs_esc.png')
plt.close()

# PLOT 2: Thrust vs ESC signal
plt.figure(figsize=(8, 6))
plt.scatter(X_thrust, y_thrust, color='green', label='Actual data')
plt.plot(X_thrust, thrust_predictions, color='red', label=f'Linear fit (R² = {thrust_r2:.4f})')
plt.xlabel('ESC signal (µs)')
plt.ylabel('Thrust (N)')
plt.title('Thrust vs ESC signal (Session 1)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig('thrust_vs_esc.png')
plt.close()

# PLOT 3: Torque vs Thrust with both linear and polynomial fits
plt.figure(figsize=(8, 6))
plt.scatter(X_thrust_for_torque, y_torque_for_thrust, color='purple', label='Actual data')
plt.plot(X_thrust_sorted, torque_thrust_predictions_linear[sorted_indices], color='red', linestyle='--',
         label=f'Linear fit (R² = {torque_thrust_r2_linear:.4f})')
plt.plot(X_smooth_thrust, y_smooth_poly_thrust, color='green',
         label=f'Polynomial fit (R² = {torque_thrust_r2_poly:.4f})')
plt.xlabel('Thrust (N)')
plt.ylabel('Torque (N·m)')
plt.title('Torque vs Thrust (Session 1)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig('torque_vs_thrust.png')
plt.close()

print("\nAll plots have been saved:")
print("1. 'torque_vs_esc.png' - Torque vs ESC signal")
print("2. 'thrust_vs_esc.png' - Thrust vs ESC signal")
print("3. 'torque_vs_thrust.png' - Torque vs Thrust")