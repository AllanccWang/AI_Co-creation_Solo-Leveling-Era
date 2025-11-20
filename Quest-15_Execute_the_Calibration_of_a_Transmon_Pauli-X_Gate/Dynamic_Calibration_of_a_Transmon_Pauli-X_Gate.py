from define_transmon_qubit import define_transmon, qiskit_simulation
import numpy as np

# Step 1-1: define Transmon
results = define_transmon(N_Levels=4)
# Step 1-2: create Solver
solver = qiskit_simulation(results, drive_freq=results["omega_01"], dt=0.1)
# initial state |0>
y0 = np.array([1, 0, 0, 0], dtype=complex)
tau = 50 # Gaussian pulse center P1 ~ 0.9
t_span = [0.0, tau]   # pulse duration τ = 50 ns
# ---
from pulse_and_qubit_dynamics_simulation import Rabi_Curve_A_vs_P1
# find π-pulse (Maximum P1)
A_pi, P1_pi, final_state = Rabi_Curve_A_vs_P1(results, solver, t_span, tau, y0)

# Plot Rabi oscillation vs time
# Rabi_oscillation_vs_time(results, solver, A_pi, y0)

# distribution of each states |0> to |3>
P0 = np.abs(final_state[0])**2
P1 = np.abs(final_state[1])**2
P2 = np.abs(final_state[2])**2
P3 = np.abs(final_state[3])**2
print(f"P0={P0:.4f}, P1={P1:.4f}, P2={P2:.6f}, P3={P3:.6f}")

# from pulse_and_qubit_dynamics_simulation import Bloch_sphere_visualization
# Project onto {|0>, |1>} and plot the trajectory. The final Bloch vector should be near the south pole when P1 ≈ 0.9.
# Bloch_sphere_visualization(results, solver, A_pi, tau, y0)

# ---
# Ramsey calibration
# Note: signal_times has no effect in this signal mode, but simulation still works correctly.
from calibration_session2 import run_ramsey_calibration
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
delta_f = run_ramsey_calibration(results, solver, A_pi, y0)
drive_freq_corrected = results["omega_01"] + delta_f
solver = qiskit_simulation(results, drive_freq=drive_freq_corrected, dt=0.1)
# ---
# T2* measurement : decoherence time for superposition state
from calibration_session2 import run_T2_star_measurement, run_T1_measurement, run_T1_measurement_lindbladModel
T2star, f_detune = run_T2_star_measurement(results, solver, A_pi, y0)
# ---
# T1* measurement : relaxation time from |1> to |0>
# disspation model
from define_transmon_qubit import qiskit_simulation_with_dissipation
lindblad_model = qiskit_simulation_with_dissipation(
    results,
    T1_target=20e-6   # target T1 = 20 μs
)
T1 = run_T1_measurement_lindbladModel(results, lindblad_model, delay_ns_list=None)
# Close system
# T1 = run_T1_measurement(results, solver, A_pi, y0)
# ---
# Echo (T₂) measurement
from calibration_session2 import run_echo_T2_measurement
# T₂ echo is abnormal because the model lacks pure dephasing noise
T2 = run_echo_T2_measurement(results, solver, A_pi, y0)
