import qutip as qt
import numpy as np
from skopt import gp_minimize, space
import matplotlib.pyplot as plt

# --- 1. Define constants and Pauli matrices ---
OMEGA_FIXED = 2 * np.pi * 5.0  # Rx(pi/2) drive amplitude
DELTA_FIXED = 2 * np.pi * 1.0  # Rz frequency detuning
sx = qt.sigmax()
sz = qt.sigmaz()

# --- 2. Helper function ---
def calculate_gate_error(U_sim, U_target):
    """Calculate average gate error rate E_avg"""
    fidelity = qt.average_gate_fidelity(U_sim, U_target)
    return 1 - fidelity

# --- 3. Three independent black-box optimization objective functions ---

# A. R_x(pi/2) gate calibration: optimize pulse duration (t_pulse)
TARGET_Rx_HALF_PI = (-1j * np.pi/4 * sx).expm() 
def error_Rx_half_pi(t_pulse_list):
    t_pulse = t_pulse_list[0]
    H_drift = 0.5 * OMEGA_FIXED * sx
    U_sim = qt.propagator(H_drift, t_pulse)
    return calculate_gate_error(U_sim, TARGET_Rx_HALF_PI)

# B. R_x(pi) gate calibration: optimize pulse amplitude
TARGET_Rx_PI = (-1j * np.pi/2 * sx).expm() 
def error_Rx_pi(amplitude_list):
    amplitude = amplitude_list[0]
    t_fixed = 0.1 
    H_drift = 0.5 * amplitude * sx
    U_sim = qt.propagator(H_drift, t_fixed)
    return calculate_gate_error(U_sim, TARGET_Rx_PI)

# C. R_z(pi/4) gate calibration: optimize detuning time (t_detune)
TARGET_Rz_PHASE = (-1j * np.pi/8 * sz).expm()
def error_Rz_phase(t_detune_list):
    t_detune = t_detune_list[0]
    H_detune = 0.5 * DELTA_FIXED * sz
    U_sim = qt.propagator(H_detune, t_detune)
    return calculate_gate_error(U_sim, TARGET_Rz_PHASE)

# --- 4. Run optimization and comparison (manual plotting version) ---
def run_optimization_and_compare(error_func, search_space, name, n_calls=50, n_random_starts=10):
    print(f"\n--- Starting Calibration for: {name} ---")
    
    # 1. Run Bayesian Optimization (BO)
    res_bo = gp_minimize(
        func=error_func,
        dimensions=[search_space],
        n_calls=n_calls,
        n_initial_points=n_random_starts,
        random_state=42
    )

    # 2. Run Random Search (RS) - for comparison
    res_rs = gp_minimize(
        func=error_func,
        dimensions=[search_space],
        n_calls=n_calls,
        n_initial_points=n_calls, # all random
        base_estimator='dummy',
        random_state=42
    )

    # 3. Report results
    print(f"✅ {name} BO Result:")
    print(f"   Optimized Parameter: {res_bo.x[0]:.4f}")
    print(f"   Minimum Error (E_avg): {res_bo.fun:.2e}")
    print(f"   Random Search Min Error: {res_rs.fun:.2e}")

    # 4. Manually plot convergence curve (Manual Plotting for Full Control)
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Extract data: compute “minimum so far” (cummin)
    # This allows plotting a step-like convergence curve
    y_bo = np.minimum.accumulate(res_bo.func_vals)
    y_rs = np.minimum.accumulate(res_rs.func_vals)
    x = np.arange(1, len(y_bo) + 1)

    # Explicitly specify colors and line styles
    ax.plot(x, y_bo, color='blue', linestyle='-', linewidth=2, label='Bayesian Optimization (GP)')
    ax.plot(x, y_rs, color='red', linestyle='--', linewidth=2, label='Random Search (Baseline)')

    # Set chart labels
    ax.set_title(f'Convergence Comparison: {name}', fontsize=14)
    ax.set_xlabel('Number of Iterations', fontsize=12)
    ax.set_ylabel('Best Gate Error ($E_{avg}$) So Far', fontsize=12)
    ax.legend(fontsize=12) # show legend
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # Using logarithmic scale may make small error differences easier to see (optional)
    ax.set_yscale('log')

    # Save plot
    file_name = f'{name.replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")}_Convergence.png'
    plt.savefig(file_name)
    plt.close(fig)
    print(f"📊 Plot saved as: {file_name}")

    return res_bo

if __name__ == '__main__':
    N_CALLS = 50
    
    # Define and run optimization
    space_A = space.Real(0.01, 0.5, name='t_pulse')
    run_optimization_and_compare(error_Rx_half_pi, space_A, 'Rx(pi/2) Pulse Time')

    space_B = space.Real(1.0, 20.0, name='amplitude')
    run_optimization_and_compare(error_Rx_pi, space_B, 'Rx(pi) Amplitude')

    space_C = space.Real(0.01, 1.0, name='t_detune')
    run_optimization_and_compare(error_Rz_phase, space_C, 'Rz(pi/4) Detuning Time')
