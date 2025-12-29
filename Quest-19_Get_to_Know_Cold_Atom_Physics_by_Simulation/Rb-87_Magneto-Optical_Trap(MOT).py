import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib


# ========= Path and module check (optional, can be removed) =========
cold_atoms_src_path = r'c:/Users/All/cold_atoms_module/src'
sys.path.insert(0, cold_atoms_src_path)


# ========= Rb-87 MOT simplified model (1D statistics + 2D cloud shape) =========
print("\n🚀 Running Rb-87 MOT simulation (with 2D atomic cloud animation)...")

# Time axis 0–0.2 s
time = np.linspace(0, 0.2, 200)          # [s]

# Density: exponential loading to 8.2×10^7 /cm^3
density = 1e6 * (1 - np.exp(-time/0.08)) * 8.2   # [1/cm^3]

# Temperature: cooling from 1.2 mK to 115 μK
temp = 1200 * np.exp(-time/0.06) + 115           # [μK]

# Cloud size: assume sqrt proportional to temperature, shrink from 1.0 mm to 0.35 mm
sigma0 = 1.0e-3      # Initial radius [m]
sigma_min = 0.35e-3  # Final radius [m]
sigma = sigma_min + (sigma0 - sigma_min) * np.exp(-time/0.08)  # [m]


# ========= Font settings (Chinese) =========
matplotlib.rcParams['font.family'] = 'Microsoft JhengHei'
matplotlib.rcParams['axes.unicode_minus'] = False


# ========= Create 2D Gaussian cloud grid =========
# Spatial range ±2 mm
L = 2.0e-3
Nx = Ny = 100
x = np.linspace(-L, L, Nx)
y = np.linspace(-L, L, Ny)
X, Y = np.meshgrid(x, y)


def gaussian_cloud(s):
    """2D Gaussian cloud, s is standard deviation (m)"""
    return np.exp(-(X**2 + Y**2) / (2*s**2))


# ========= Create animation figure: left 2D cloud, right density/temperature curves =========
fig, (ax_cloud, ax_curve) = plt.subplots(1, 2, figsize=(12, 5))


# Left plot: 2D atomic cloud
s0 = sigma[0]
Z0 = gaussian_cloud(s0)
im = ax_cloud.imshow(
    Z0,
    extent=[-L*1e3, L*1e3, -L*1e3, L*1e3],
    origin='lower',
    cmap='inferno',
    vmin=0,
    vmax=1
)
ax_cloud.set_xlabel('x (mm)')
ax_cloud.set_ylabel('y (mm)')
ax_cloud.set_title('MOT Atomic Cloud 2D Gaussian Distribution')
cbar = plt.colorbar(im, ax=ax_cloud)
cbar.set_label('Relative Density')


# Right plot: density and temperature curves (drawn up to current time)
line_n, = ax_curve.plot([], [], 'b-', linewidth=2, label='Density')
ax_curve2 = ax_curve.twinx()
line_T, = ax_curve2.plot([], [], 'r-', linewidth=2, label='Temperature')

ax_curve.set_xlabel('Time (ms)')
ax_curve.set_ylabel('Density (10⁶/cm³)', color='b')
ax_curve2.set_ylabel('Temperature (μK)', color='r')
ax_curve.set_xlim(0, time[-1]*1e3)
ax_curve.set_ylim(0, 8.5)
ax_curve2.set_ylim(0, 1300)
ax_curve.set_title("MOT Loading and Cooling Curves")

# Combined legend
lines = [line_n, line_T]
labels = ['Density', 'Temperature']
ax_curve.legend(lines, labels, loc='upper right', fontsize=10)


fig.tight_layout()


# ========= Animation functions =========
def init():
    # Initial: empty curves
    line_n.set_data([], [])
    line_T.set_data([], [])
    # Initial cloud
    im.set_data(gaussian_cloud(sigma[0]))
    return im, line_n, line_T


def update(i):
    # 2D cloud contraction
    s = sigma[i]
    Z = gaussian_cloud(s)
    im.set_data(Z)
    ax_cloud.set_title(
        f"MOT Atomic Cloud 2D Gaussian Distribution\nTime={time[i]*1e3:5.1f} ms, σ={s*1e3:4.2f} mm"
    )

    # Right curves up to current time
    t_ms = time[:i+1] * 1e3
    n_val = density[:i+1] / 1e6
    T_val = temp[:i+1]
    line_n.set_data(t_ms, n_val)
    line_T.set_data(t_ms, T_val)

    return im, line_n, line_T


ani = FuncAnimation(
    fig,
    update,
    frames=len(time),
    init_func=init,
    blit=False,       # imshow + dual y-axis, blit=False is more stable
    interval=50
)


# To save as mp4, install ffmpeg first, then uncomment below
# ani.save('mot_cloud_evolution.mp4', fps=30, dpi=150)


print("✅ Animation created successfully, displaying 2D atomic cloud contraction + curve evolution")
plt.show()
