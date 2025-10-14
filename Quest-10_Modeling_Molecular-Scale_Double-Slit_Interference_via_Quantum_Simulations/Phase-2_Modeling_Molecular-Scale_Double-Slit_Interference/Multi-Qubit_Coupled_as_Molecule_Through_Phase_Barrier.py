"""
Phase 2: Multi-qubit "molecular" interference simulation.
Now with path qubit marginalization and multiple noise levels.
"""

import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, phase_damping_error
from qiskit.circuit.library import QFT

# ------------------------------
# Helper functions
# ------------------------------
def build_molecule_interference(path_qubits, internal_qubits, phi, marking_strength=1.0, use_qft=True):
    total = path_qubits + internal_qubits
    qc = QuantumCircuit(total, total)

    path_reg = list(range(path_qubits))
    int_reg  = list(range(path_qubits, total))

    # 1) Prepare path superposition
    qc.h(path_reg)

    # 2) Apply path phase shift
    qc.p(phi, path_reg[0])

    # 3) Which-path marking: entangle path with internal qubits
    theta = marking_strength * np.pi/4
    for q in int_reg:
        qc.cry(+theta, path_reg[0], q)
        qc.x(path_reg[0])
        qc.cry(-theta, path_reg[0], q)
        qc.x(path_reg[0])

    # 4) Path readout: QFT or Hadamard
    if use_qft:
        qc.append(QFT(path_qubits, do_swaps=True), path_reg)
    else:
        qc.h(path_reg)

    # 5) Measurement
    qc.measure(range(total), range(total))
    return qc

def create_noise_model(p):
    """Create a simple phase-damping noise model."""
    if p is None or p <= 0.0:
        return None
    nm = NoiseModel()
    err = phase_damping_error(p)
    nm.add_all_qubit_quantum_error(err, ['u1', 'u2', 'u3', 'id'])
    return nm

def simulate_circuit(qc, noise_model=None, shots=20000):
    """Simulate the given circuit with optional noise model."""
    simulator = AerSimulator()
    tqc = transpile(qc, simulator)
    if noise_model is None:
        job = simulator.run(tqc, shots=shots)
    else:
        job = simulator.run(tqc, shots=shots, noise_model=noise_model)
    result = job.result()
    return result.get_counts()

def marginalize_path_distribution(counts, path_qubits, internal_qubits, shots):
    """
    Marginalize over internal qubits and return probability distribution
    for the path register only.
    """
    path_size = 2**path_qubits
    probs = np.zeros(path_size)
    for bitstr, c in counts.items():
        path_bits = bitstr[-(path_qubits+internal_qubits):][-(path_qubits):]
        idx = int(path_bits, 2)
        probs[idx] += c
    return probs / shots

# ------------------------------
# Parameters
# ------------------------------
num_qubits_list = [1, 2, 4, 8]   # internal qubits
phi_values = np.linspace(0, 2*np.pi, 60)
noise_strength_list = [0.0, 0.02, 0.05, 1.0]
shots = 20000

# ------------------------------
# Simulation and plotting
# ------------------------------
fig, axes = plt.subplots(2, 2, figsize=(14,10))
axes = axes.flatten()

for i, noise_strength in enumerate(noise_strength_list):
    noise_model = create_noise_model(noise_strength)
    path_distributions = {}

    for n in num_qubits_list:
        dist_list = []
        for phi in phi_values:
            qc = build_molecule_interference(path_qubits=1, internal_qubits=n, phi=phi)
            counts = simulate_circuit(qc, noise_model=noise_model, shots=shots)
            dist = marginalize_path_distribution(counts, path_qubits=1, internal_qubits=n, shots=shots)
            dist_list.append(dist)
        path_distributions[n] = np.array(dist_list)

    # Plot both cos²-like (path=0) and sin²-like (path=1)
    ax = axes[i]
    for n in num_qubits_list:
        ax.plot(phi_values, path_distributions[n][:,0], label=f"{n}-qubit (P(path=0))")
        ax.plot(phi_values, path_distributions[n][:,1], '--', label=f"{n}-qubit (P(path=1))")
    ax.set_title(f"Noise strength p={noise_strength}")
    ax.set_xlabel("Phase φ (rad)")
    ax.set_ylabel("Probability")
    ax.grid(True)
    if i == 0:  # show legend only once
        ax.legend(fontsize=8)

plt.tight_layout()
plt.show()
