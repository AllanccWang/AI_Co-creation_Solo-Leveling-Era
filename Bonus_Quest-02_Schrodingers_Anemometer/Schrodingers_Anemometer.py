import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

# --- Side Quest 1 Implementation ---

# 1. Parameter Settings
L1, L2 = 1.0, 1.0  # Link lengths
N_POINTS = 20000   # Monte Carlo sampling points

# 2. Superposition States
# State A: 45 degrees (pi/4 radians)
theta1_A = np.deg2rad(45)
P_A = 0.1
# State B: 135 degrees (3pi/4 radians)
theta1_B = np.deg2rad(135)
P_B = 0.9

# 3. Generate Random Data Points
X_coords = []
Y_coords = []

# Second joint (theta2) sweeps the full range (random uniform distribution)
theta2_range = np.random.uniform(0, 2 * np.pi, N_POINTS)

for theta2 in theta2_range:
    # Decide whether to use State A or State B (based on probabilities P_A and P_B)
    if np.random.rand() < P_A:
        # Use State A
        theta1 = theta1_A
    else:
        # Use State B
        theta1 = theta1_B

    # Calculate End-Effector coordinates (X, Y)
    x = L1 * np.cos(theta1) + L2 * np.cos(theta2)
    y = L1 * np.sin(theta1) + L2 * np.sin(theta2)

    X_coords.append(x)
    Y_coords.append(y)

# Convert lists to NumPy arrays
X_coords = np.array(X_coords)
Y_coords = np.array(Y_coords)

# --- Side Quest 2 Implementation ---

# 4. Data Binning (Heatmap Data Preparation)
# Set number of bins (determines heatmap resolution)
N_BINS = 100

# Use numpy.histogram2d to calculate 2D density distribution
# H: Density matrix, xedges/yedges: Axis boundaries
H, xedges, yedges = np.histogram2d(X_coords, Y_coords, bins=N_BINS)

# Transpose density H for proper plotting orientation
H = H.T

# 5. Plot Heatmap (Visualization)
plt.figure(figsize=(8, 7))

# Plot heatmap using 'viridis' color map.
# Use plt.Normalize to set the color scale range, making the contrast clear.
plt.imshow(H, interpolation='nearest', origin='lower',
           extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
           cmap='viridis',
           norm=plt.Normalize(vmin=0, vmax=np.max(H)*0.5)
          )

# Add Color Bar
cbar = plt.colorbar(label='Probability Density (Number of Samples)')

# Set title and axis labels
plt.title(f'Bonus Quest: Schrödinger\'s Anemometer Density Map\n(Superposition $\\theta_1 = 45^\circ$ vs $135^\circ$, $P_A:P_B = {P_A}:{P_B}$)')
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.axis('equal') # Ensure equal aspect ratio to prevent shape distortion
plt.grid(alpha=0.2)
plt.show()

print(f"\n✅ End-effector data generation complete: {N_POINTS} points.")
print("✅ Heatmap visualization complete.")