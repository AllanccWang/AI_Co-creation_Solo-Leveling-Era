"""
phase1_double_slit.py
Single-qubit "double-slit" quantum circuit simulation.

- 1 qubit circuit: H -> P(phi) -> H -> measure
- Optionally apply a simple noise model
- Sweep phi from 0 to 2π and plot P(|0>) and P(|1>)
- Compute and show simple visibility (contrast) if desired
"""

import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, amplitude_damping_error, phase_damping_error

# ----- parameters -----
shots = 4096
phi_vals = np.linspace(0, 2*np.pi, 101)
p_noise_list = [0.0, 0.02, 0.05, 0.1]
noise_types = ["depolarizing", "phase", "amplitude"]
simulator = AerSimulator()
# ----- helper: run single-qubit double-slit -----
def run_double_slit(phi_vals, p_noise, noise_type):
    if p_noise > 0:
        nm = NoiseModel()
        if noise_type == "depolarizing":
            err = depolarizing_error(p_noise, 1)
        elif noise_type == "phase":
            err = phase_damping_error(p_noise)
        elif noise_type == "amplitude":
            err = amplitude_damping_error(p_noise)
        else:
            raise ValueError("Unknown noise type")
        nm.add_all_qubit_quantum_error(err, ['u1', 'u2', 'u3', 'id'])
        noise_model = nm
    else:
        noise_model = None

    p0_sim, p1_sim = [], []
    for phi in phi_vals:
        qc = QuantumCircuit(1, 1)
        qc.h(0)
        qc.p(phi, 0)
        qc.h(0)
        qc.measure(0, 0)

        circ_t = transpile(qc, simulator)
        job = simulator.run(circ_t, noise_model=noise_model, shots=shots)
        counts = job.result().get_counts()
        p0 = counts.get('0', 0) / shots
        p1 = counts.get('1', 0) / shots
        p0_sim.append(p0)
        p1_sim.append(p1)
    return np.array(p0_sim), np.array(p1_sim)

# ----- analytic ideal curves -----
p0_analytic = np.cos(phi_vals / 2.0)**2
p1_analytic = np.sin(phi_vals / 2.0)**2

# ----- main: plot for each noise type -----
for noise_type in noise_types:
    plt.figure(figsize=(10, 5))
    for p_noise in p_noise_list:
        p0_sim, p1_sim = run_double_slit(phi_vals, p_noise, noise_type)
        plt.plot(phi_vals, p0_sim, label=f"P0 ({noise_type}, p={p_noise})")
        plt.plot(phi_vals, p1_sim, '--', label=f"P1 ({noise_type}, p={p_noise})")

    # add ideal analytic lines
    plt.plot(phi_vals, p0_analytic, 'k-', lw=2, label='P0 ideal = cos²(φ/2)')
    plt.plot(phi_vals, p1_analytic, 'k--', lw=2, label='P1 ideal = sin²(φ/2)')

    plt.xlabel('Phase φ (rad)')
    plt.ylabel('Probability')
    plt.title(f'Phase-1 double-slit: {noise_type} noise comparison')
    plt.legend(fontsize=8)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
