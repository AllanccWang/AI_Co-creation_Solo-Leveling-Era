import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# === Initial Parameters ===
L1_init, L2_init, L3_init, L4_init = 50, 40, 70, 60
theta2_init = 45
O2 = np.array([0, 0])

# === Geometry Solver ===
def compute_positions(theta2_deg, L1, L2, L3, L4):
    O4 = np.array([L1, 0])
    theta2 = np.radians(theta2_deg)
    A = O2 + L2 * np.array([np.cos(theta2), np.sin(theta2)])

    def circle_intersection(c1, r1, c2, r2):
        d = np.linalg.norm(c2 - c1)
        if d > r1 + r2 or d < abs(r1 - r2):
            return None
        a = (r1**2 - r2**2 + d**2) / (2 * d)
        h = np.sqrt(r1**2 - a**2)
        p2 = c1 + a * (c2 - c1) / d
        offset = h * np.array([-(c2[1] - c1[1]) / d, (c2[0] - c1[0]) / d])
        return p2 + offset, p2 - offset

    result = circle_intersection(A, L3, O4, L4)
    if result is None:
        return None, None, None, None
    B1, B2 = result
    B = B1 if B1[1] > B2[1] else B2
    return O2, A, B, O4

# === Plot Setup ===
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.15, bottom=0.35)
ax.set_aspect('equal')
ax.set_xlim(-100, 200)
ax.set_ylim(-100, 100)
link_line, = ax.plot([], [], 'o-', lw=2)
trace_line, = ax.plot([], [], 'r--', lw=1)
trajectory = []

# === Slider Axes ===
ax_theta = plt.axes([0.25, 0.25, 0.65, 0.03])
ax_L1 = plt.axes([0.25, 0.20, 0.65, 0.03])
ax_L2 = plt.axes([0.25, 0.15, 0.65, 0.03])
ax_L3 = plt.axes([0.25, 0.10, 0.65, 0.03])
ax_L4 = plt.axes([0.25, 0.05, 0.65, 0.03])

# === Sliders ===
s_theta = Slider(ax_theta, 'θ₂ (deg)', 0, 360, valinit=theta2_init)
s_L1 = Slider(ax_L1, 'L1', 20, 100, valinit=L1_init)
s_L2 = Slider(ax_L2, 'L2', 20, 100, valinit=L2_init)
s_L3 = Slider(ax_L3, 'L3', 20, 100, valinit=L3_init)
s_L4 = Slider(ax_L4, 'L4', 20, 100, valinit=L4_init)

# === Update Function ===
def update(val):
    theta2 = s_theta.val
    L1 = s_L1.val
    L2 = s_L2.val
    L3 = s_L3.val
    L4 = s_L4.val
    O2, A, B, O4 = compute_positions(theta2, L1, L2, L3, L4)
    if A is None or B is None:
        link_line.set_data([], [])
        trace_line.set_data([], [])
        return
    xdata = [O2[0], A[0], B[0], O4[0]]
    ydata = [O2[1], A[1], B[1], O4[1]]
    link_line.set_data(xdata, ydata)
    trajectory.append(B)
    trace_line.set_data([p[0] for p in trajectory], [p[1] for p in trajectory])
    fig.canvas.draw_idle()

# === Connect Sliders ===
s_theta.on_changed(update)
s_L1.on_changed(update)
s_L2.on_changed(update)
s_L3.on_changed(update)
s_L4.on_changed(update)

# === Initial Draw ===
update(None)
fig.suptitle("Interactive Four-Bar Linkage Simulator", fontsize=14)
plt.show()
