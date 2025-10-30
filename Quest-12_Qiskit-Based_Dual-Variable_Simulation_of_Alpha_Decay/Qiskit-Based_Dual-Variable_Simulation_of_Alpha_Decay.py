import numpy as np
import matplotlib.pyplot as plt
from qiskit.circuit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import Sampler # Note: Sampler is deprecated but retained as per your working code
from qiskit.circuit.library import StatePreparation 

# --- 1. Define System Parameters ---
N_QUBITS = 4        
TOTAL_TIME = 1.0    
STEPS = 5           
IMAGINARY_FACTOR = -1j # Used for time evolution in e^(-iHt)

# --- 2. Step 01: Define Base Operators ---
# H = T + V (Kinetic + Potential) terms
# P1, P2 are Kinetic terms, P3, P4 are Potential terms
PAULI_TERMS = [
    # Operator, Base Coefficient (C), Involved Qubits (Qubits)
    ("XXII", 1.0, [0, 1]), # T1: X0 X1
    ("IIXX", 1.0, [2, 3]), # T2: X2 X3
    ("ZIIZ", 1.0, [0, 3]), # V1: Z0 Z3
    ("IZZI", 1.0, [1, 2]), # V2: Z1 Z2
]

# --- 3. Step 02: Construct Initial Wave Packet Circuit (Fixed) ---
def create_gaussian_wavepacket(n_qubits, center_index, sigma):
    """Creates a normalized Gaussian wave packet vector."""
    dim = 2**n_qubits
    positions = np.arange(dim)
    amplitudes = np.exp(-(positions - center_index)**2 / (2 * sigma**2))
    return amplitudes / np.linalg.norm(amplitudes)

initial_state_vector = create_gaussian_wavepacket(N_QUBITS, center_index=4, sigma=1.5)
initial_state_circuit = StatePreparation(initial_state_vector)


# ---------------------------------------------------
# --- 💥 Core Fix: Manual Implementation of Two-Qubit Pauli Evolution ---
# ---------------------------------------------------

def two_qubit_pauli_evolution(circuit, pauli_string, qubits, angle):
    """
    Implements the evolution e^(-i * angle * PauliString).
    This function handles 2-qubit Pauli operators (e.g., XX, ZZ).
    The standard implementation uses CNOTs to transform the Pauli string into a ZZ evolution.
    """
    p_a, p_b = pauli_string[0], pauli_string[1]
    q_a, q_b = qubits[0], qubits[1]
    
    # 1. Apply basis change gates to map X or Y to Z
    if p_a == 'X': circuit.h(q_a)
    if p_b == 'X': circuit.h(q_b)
    if p_a == 'Y': circuit.sdg(q_a); circuit.h(q_a)
    if p_b == 'Y': circuit.sdg(q_b); circuit.h(q_b)
    
    # 2. Map all terms to ZZ (since e^(-i theta ZZ) is the primitive evolution)
    circuit.cx(q_a, q_b)

    # 3. Apply Z rotation gate (angle is 2 * theta)
    circuit.rz(2 * angle, q_b)
    
    # 4. Uncompute CNOT
    circuit.cx(q_a, q_b)

    # 5. Undo basis change gates
    if p_a == 'X': circuit.h(q_a)
    if p_b == 'X': circuit.h(q_b)
    if p_a == 'Y': circuit.h(q_a); circuit.s(q_a)
    if p_b == 'Y': circuit.h(q_b); circuit.s(q_b)

def build_manual_trotter_circuit(T_coeff, V_coeff):
    """Constructs a complete Trotter evolution circuit using numerical coefficients."""
    
    # Calculate the angle for a single time step
    time_step = TOTAL_TIME / STEPS
    
    # Pauli coefficient list: [C_T, C_T, C_V, C_V]
    coeffs = [T_coeff, T_coeff, V_coeff, V_coeff]
    
    # Initialize circuit skeleton
    trotter_qc = QuantumCircuit(N_QUBITS)
    
    # Execute Trotter evolution steps
    for _ in range(STEPS):
        for i, (pauli_string_full, base_coeff, qubits) in enumerate(PAULI_TERMS):
            # Extract the relevant 2-qubit Pauli string (e.g., 'XX')
            pauli_string = "".join(pauli_string_full[q] for q in qubits)
            
            # Calculate the rotation angle (coefficient multiplied by time_step)
            # Evolution angle = coefficient * total_time / steps
            theta = coeffs[i] * time_step
            
            # Apply manual evolution
            two_qubit_pauli_evolution(
                trotter_qc,
                pauli_string,
                qubits,
                # Pass theta, as the implementation handles the 2*theta factor
                theta 
            )
            
    return trotter_qc

# ---------------------------------------------------
# --- 5. Step 04 & 05: Experiment 1 (Vary Barrier Height V0) ---
# ---------------------------------------------------
print("--- Running Experiment 1: Varying Barrier Height V0 (Fixed Kinetic T=0.5) ---")
TEST_VOLTAGES = [2.5, 3.5, 4.5] 
FIXED_T_COEFF = 0.5             
tunneling_results_V = {}
qc_list_v = []
sampler_v = Sampler() # Using the Sampler that works in your environment

for V_test in TEST_VOLTAGES:
    # 1. Build the manual evolution circuit
    evolution_circuit = build_manual_trotter_circuit(T_coeff=FIXED_T_COEFF, V_coeff=V_test)
    
    qc_v = QuantumCircuit(N_QUBITS, N_QUBITS, name=f"V={V_test}")
    qc_v.compose(initial_state_circuit, inplace=True)
    qc_v.compose(evolution_circuit, inplace=True) 
    qc_v.measure(range(N_QUBITS), range(N_QUBITS))
    
    qc_list_v.append(qc_v) 

job_v = sampler_v.run(qc_list_v)
results_v = job_v.result().quasi_dists

# Analyze Experiment 1 results
for i, V_test in enumerate(TEST_VOLTAGES):
    counts = results_v[i]
    current_prob = 0
    for state_index, probability in counts.items():
        # Particle is considered "tunneled" if found in the final section (index >= 13, or '1101' to '1111')
        if state_index >= 13: 
            current_prob += probability
    tunneling_results_V[V_test] = current_prob
    print(f"  Barrier V0 = {V_test} : Tunneling Probability P_tunnel = {current_prob:.4f}")

# Plot Experiment 1
V_values = list(tunneling_results_V.keys())
P_values_v = list(tunneling_results_V.values())
plt.figure(figsize=(8, 5))
plt.bar([str(v) for v in V_values], P_values_v, color=['green', 'orange', 'red'])
plt.xlabel("Barrier Height $V_0$ (Energy Units)")
plt.ylabel("Final Tunneling Probability $P_{tunnel}$")
plt.title("Experiment 1: Tunneling Probability vs. Barrier Height (Fixed Kinetic Energy)")
plt.grid(axis='y', linestyle='--')
plt.show()

# ---------------------------------------------------
# --- 6. Step 04 & 05: Experiment 2 (Vary Kinetic Energy T) ---
# ---------------------------------------------------
print("\n--- Running Experiment 2: Varying Kinetic Energy T (Fixed Barrier V0=3.5) ---")
TEST_T_COEFFS = [0.5, 1.0, 1.5] 
FIXED_BARRIER_V0 = 3.5        
tunneling_results_T = {}
qc_list_t = []
sampler_t = Sampler() # Using the Sampler that works in your environment

for T_test in TEST_T_COEFFS:
    # 1. Build the manual evolution circuit
    evolution_circuit = build_manual_trotter_circuit(T_coeff=T_test, V_coeff=FIXED_BARRIER_V0)

    qc_t = QuantumCircuit(N_QUBITS, N_QUBITS, name=f"T={T_test}")
    qc_t.compose(initial_state_circuit, inplace=True)
    qc_t.compose(evolution_circuit, inplace=True) 
    qc_t.measure(range(N_QUBITS), range(N_QUBITS))
    
    qc_list_t.append(qc_t) 

job_t = sampler_t.run(qc_list_t)
results_t = job_t.result().quasi_dists

# Analyze Experiment 2 results
for i, T_test in enumerate(TEST_T_COEFFS):
    counts = results_t[i]
    current_prob = 0
    for state_index, probability in counts.items():
        if state_index >= 13: 
            current_prob += probability
    tunneling_results_T[T_test] = current_prob
    print(f"  Kinetic Coeff T = {T_test} : Tunneling Probability P_tunnel = {current_prob:.4f}")

# Plot Experiment 2
T_values = list(tunneling_results_T.keys())
P_values_t = list(tunneling_results_T.values())
plt.figure(figsize=(8, 5))
plt.bar([f'T={t}' for t in T_values], P_values_t, color=['skyblue', 'lightcoral', 'gold'])
plt.xlabel("Kinetic Coefficient $C_T$ (Effective Kinetic Energy)")
plt.ylabel("Final Tunneling Probability $P_{tunnel}$")
plt.title(f"Experiment 2: Tunneling Probability vs. Kinetic Energy (Fixed Barrier V0={FIXED_BARRIER_V0})")
plt.grid(axis='y', linestyle='--')
plt.show()

# --- 7. Final Physics Verification Summary ---
print("\n--- Final Physics Verification Summary ---")
P_values_v = list(tunneling_results_V.values())
# Prediction: Higher barrier should lead to lower tunneling probability.
if P_values_v[0] > P_values_v[1] > P_values_v[2]:
    print("✅ Experiment 1 Verified: Higher barrier leads to lower tunneling probability.")
else:
    print("❌ Experiment 1 Failed: Results contradict physics predictions.")

P_values_t = list(tunneling_results_T.values())
# Prediction: Higher kinetic energy should lead to higher tunneling probability.
if P_values_t[0] < P_values_t[1] < P_values_t[2]:
    print("✅ Experiment 2 Verified: Higher kinetic energy leads to higher tunneling probability.")
else:
    print("❌ Experiment 2 Failed: Results contradict physics predictions.")