import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib


# ========= cold_atoms module path =========
cold_atoms_src_path = r'c:/Users/All/cold_atoms_module/src'
sys.path.insert(0, cold_atoms_src_path)


print("📁 Checking cold_atoms module:")
try:
    import cold_atoms
    print("✅ cold_atoms loaded successfully")
except ImportError:
    print("❌ cold_atoms not found, using mock simulation")
    # Simulated module content
    class cold_atoms:
        class AtomInterferometer:
            def __init__(self, params): self.params = params
            def simulate(self): return self._mock_data()
            def _mock_data(self):
                t = np.linspace(0, 0.01, 100)
                pos1 = 0.5*t**2 * 1e3  # Upper path [mm]
                pos2 = -0.5*t**2 * 1e3 # Lower path [mm]
                prob = 0.5 + 0.4*np.cos(2*np.pi*0.1/t[-1]*t) * np.exp(-(t-0.005)**2/0.001)
                return t, pos1, pos2, prob
        pass
    print("✅ Using simulated cold_atoms.AtomInterferometer")


# ========= Atom interferometer parameters (Rb-87, λ=780 nm) =========
params = {
    'wavelength': 780e-9,      # D2 line [m]
    'pulse_duration': 30e-6,   # π/2, π pulse duration [s]
    'T1': 4e-3,                # 1st arm time [s]
    'T2': 8e-3,                # 2nd arm time [s]
    'gravity': 9.8,            # Gravitational acceleration [m/s²]
    'k_eff': 2 * 2*np.pi/780e-9  # Raman effective wavevector [m^-1]
}


# ========= Run simulation =========
print("\n🚀 Running atom interferometer simulation...")
interferometer = cold_atoms.AtomInterferometer(params)
time, pos_upper, pos_lower, fringe_prob = interferometer.simulate()


# ========= Animation: path splitting + interference fringes =========
matplotlib.rcParams['font.family'] = 'Microsoft JhengHei'
matplotlib.rcParams['axes.unicode_minus'] = False


fig, (ax_path, ax_fringe) = plt.subplots(1, 2, figsize=(12, 5))


# Left plot: atomic wavefunction paths
ax_path.set_xlim(-2, 2)
ax_path.set_ylim(-1, 1)
ax_path.set_xlabel('Position (mm)')
ax_path.set_ylabel('Height (mm)')
ax_path.set_title('Mach-Zehnder Atom Interferometer\nInterference between two paths')
ax_path.grid(True, alpha=0.3)
ax_path.axhline(0, color='k', lw=1)


# Right plot: interference fringes
line_fringe, = ax_fringe.plot([], [], 'b-', lw=3)
ax_fringe.set_xlim(0, time[-1]*1e3)
ax_fringe.set_ylim(0, 1.1)
ax_fringe.set_xlabel('Time (ms)')
ax_fringe.set_ylabel('Interference phase probability')
ax_fringe.set_title('Interference fringes P = ½[1 + cos(φ)]')
ax_fringe.grid(True, alpha=0.3)


fig.tight_layout()


def init():
    line_fringe.set_data([], [])
    ax_path.clear()
    ax_path.set_xlim(-2, 2)
    ax_path.set_ylim(-1, 1)
    ax_path.set_xlabel('Position (mm)')
    ax_path.set_ylabel('Height (mm)')
    ax_path.set_title('Mach-Zehnder Atom Interferometer\nInterference between two paths')
    ax_path.grid(True, alpha=0.3)
    ax_path.axhline(0, color='k', lw=1)
    return line_fringe,


def update(i):
    t = time[:i+1]
    
    # Left plot: draw two parabolic paths
    ax_path.clear()
    ax_path.set_xlim(-2, 2)
    ax_path.set_ylim(-1, 1)
    ax_path.set_xlabel('Position (mm)')
    ax_path.set_ylabel('Height (mm)')
    ax_path.set_title(f'Atom Interferometer: t = {t[i]*1e3:.1f} ms')
    ax_path.grid(True, alpha=0.3)
    ax_path.axhline(0, color='k', lw=1)
    
    # Upper path (ℏk kick)
    x_upper = (params['k_eff'] * t**2 / 2) * 1e3
    y_upper = 0.5 * params['gravity'] * t**2 * 1e3
    ax_path.plot(x_upper[:i+1], y_upper[:i+1], 'b-', lw=3, label='Upper path')
    
    # Lower path (no kick)
    x_lower = np.zeros_like(t)
    y_lower = 0.5 * params['gravity'] * t**2 * 1e3
    ax_path.plot(x_lower[:i+1], y_lower[:i+1], 'r-', lw=3, label='Lower path')
    
    ax_path.legend(loc='upper right')
    
    # Right plot: interference phase
    fringe_t = t * 1e3
    fringe_p = 0.5 + 0.4 * np.cos(2*np.pi * 0.1 * t / time[-1]) * np.exp(-(t-0.005)**2 / 0.001)
    line_fringe.set_data(fringe_t[:i+1], fringe_p[:i+1])
    
    return line_fringe,


# Build animation
ani = FuncAnimation(fig, update, frames=len(time), init_func=init, 
                    interval=50, blit=False, repeat=True)


print("✅ Atom interferometer animation complete!")
print("Left plot: two parabolic paths overlap → interference")
print("Right plot: phase oscillates over time → sensing gravity/acceleration")


plt.show()
