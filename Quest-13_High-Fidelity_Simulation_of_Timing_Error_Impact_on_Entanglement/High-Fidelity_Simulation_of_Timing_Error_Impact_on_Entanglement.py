import numpy as np
import matplotlib.pyplot as plt
import scqubits as scq

# Qiskit Dynamics imports
from qiskit_dynamics.solvers import Solver
from qiskit.quantum_info import state_fidelity, DensityMatrix
from qiskit_dynamics.signals import Signal

# ---
# STEP 1: scqubits HARDWARE MODELING
# ---

print("Step 1: Building scqubits hardware model...")

g_strength = 0.02   # GHz
trunc_dim = 2       # 2-level truncation for speed (Hilbert space = 4)

# Define two Transmons
q0 = scq.Transmon(EJ=30.0, EC=1.2, ng=0.3, ncut=10)
q1 = scq.Transmon(EJ=25.0, EC=1.3, ng=0.3, ncut=10)

# Eigenvalues/vectors
evals0, evecs0 = q0.eigensys(evals_count=trunc_dim)
evals1, evecs1 = q1.eigensys(evals_count=trunc_dim)
wq0 = evals0[1] - evals0[0]
wq1 = evals1[1] - evals1[0]

# Bare Hamiltonians
H_q0 = np.diag(evals0 - evals0[0])
H_q1 = np.diag(evals1 - evals1[0])

# Number operators projected
n_op_q0 = evecs0.T @ q0.n_operator() @ evecs0
n_op_q1 = evecs1.T @ q1.n_operator() @ evecs1

# Pauli operators
sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)

# System Hamiltonians
I = np.eye(trunc_dim)
H_bare = np.kron(H_q0, I) + np.kron(I, H_q1)
H_int = g_strength * np.kron(n_op_q0, n_op_q1)

# Static Hamiltonian
H_static = 2 * np.pi * H_int
H_static = 0.5 * (H_static + H_static.conj().T)  # enforce Hermiticity

# Drive operators
drive_op_q0 = 2 * np.pi * np.kron(sigma_x, I)
drive_op_q1 = 2 * np.pi * np.kron(I, sigma_x)
drive_op_ZX = 2 * np.pi * np.kron(sigma_z, sigma_x)

drive_ops = [drive_op_q0, drive_op_q1, drive_op_ZX]

# Rotating frame
rot_frame = 2 * np.pi * H_bare

# Initial and target states
y0 = np.zeros(trunc_dim * trunc_dim, dtype=complex)
y0[0] = 1.0
psi_11 = np.zeros(trunc_dim * trunc_dim, dtype=complex)
psi_11[1 * trunc_dim + 1] = 1.0
ideal_bell = (y0 + psi_11) / np.sqrt(2)

print(f"  Q0 frequency: {wq0:.4f} GHz")
print(f"  System dimension: {H_static.shape[0]}")

# ---
# STEP 2: Qiskit Dynamics Solver
# ---

print("\nStep 2: Building Solver...")

solver = Solver(
    static_hamiltonian=H_static,
    hamiltonian_operators=drive_ops,
    rotating_frame=rot_frame,
)

print("  Solver ready.")

# ---
# STEP 3: Pulses
# ---

print("Step 3: Defining pulses...")

PI_HALF_AMP = 0.05
PI_HALF_SIGMA = 5
PI_HALF_DUR = 20

CR_AMP = 0.05
CR_SIGMA = 10
CR_DUR = 40

def gaussian_envelope(t, amp, sigma, t_peak):
    return amp * np.exp(-((t - t_peak) ** 2) / (2 * sigma**2))

# Ramsey
def run_ramsey(delta_t=0.0):
    t_peak = PI_HALF_DUR / 2
    pulse1 = lambda t: gaussian_envelope(t, PI_HALF_AMP, PI_HALF_SIGMA, t_peak)
    sigs1 = [Signal(pulse1, 0.0), Signal(lambda t: 0.0, 0.0), Signal(lambda t: 0.0, 0.0)]
    y1 = solver.solve(t_span=[0.0, PI_HALF_DUR], y0=y0, signals=sigs1).y[-1]

    wait = 20.0
    sigs_wait = [Signal(lambda t: 0.0, 0.0)] * 3
    y2 = solver.solve(t_span=[0.0, wait], y0=y1, signals=sigs_wait).y[-1]

    dur2 = PI_HALF_DUR + delta_t
    t_peak2 = dur2 / 2
    pulse2 = lambda t: gaussian_envelope(t, PI_HALF_AMP, PI_HALF_SIGMA, t_peak2)
    sigs2 = [Signal(pulse2, 0.0), Signal(lambda t: 0.0, 0.0), Signal(lambda t: 0.0, 0.0)]
    y3 = solver.solve(t_span=[0.0, dur2], y0=y2, signals=sigs2).y[-1]
    return y3

# Bell
def run_bell(delta_t=0.0):
    t_peak = PI_HALF_DUR / 2
    pulse1 = lambda t: gaussian_envelope(t, PI_HALF_AMP, PI_HALF_SIGMA, t_peak)
    sigs1 = [Signal(pulse1, 0.0), Signal(lambda t: 0.0, 0.0), Signal(lambda t: 0.0, 0.0)]
    y1 = solver.solve(t_span=[0.0, PI_HALF_DUR], y0=y0, signals=sigs1).y[-1]

    dur = CR_DUR + delta_t
    t_peak2 = dur / 2
    pulse2 = lambda t: gaussian_envelope(t, CR_AMP, CR_SIGMA, t_peak2)
    sigs2 = [Signal(lambda t: 0.0, 0.0), Signal(lambda t: 0.0, 0.0), Signal(pulse2, 0.0)]
    y2 = solver.solve(t_span=[0.0, dur], y0=y1, signals=sigs2).y[-1]
    return y2

# ---
# STEP 4: Execution
# ---

print("\nStep 4: Running timing error sweep...")

delta_t_range = np.linspace(-10, 10, 5)  # fewer points for speed
phase_errors = []
fidelities = []

state_ref = run_ramsey(0.0)
idx_00, idx_10 = 0, 2
ideal_phase = np.angle(state_ref[idx_10] / state_ref[idx_00])

for dt in delta_t_range:
    st = run_ramsey(dt)
    cur_phase = np.angle(st[idx_10] / st[idx_00])
    dphi = (cur_phase - ideal_phase + np.pi) % (2 * np.pi) - np.pi
    phase_errors.append(dphi * 180 / np.pi)

for dt in delta_t_range:
    st = run_bell(dt)
    # Flatten and normalize before wrapping in DensityMatrix
    ideal_vec = np.asarray(ideal_bell).flatten()
    ideal_vec = ideal_vec / np.linalg.norm(ideal_vec)
    st_vec = np.asarray(st).flatten()
    st_vec = st_vec / np.linalg.norm(st_vec)
    fid = state_fidelity(DensityMatrix(ideal_vec), DensityMatrix(st_vec))
    fidelities.append(fid)

print("Simulation complete.")

# ---
# STEP 5: Plot
# ---

plt.style.use("seaborn-v0_8-darkgrid")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
fig.suptitle("Timing Error Impact on Quantum States", fontsize=16)

ax1.plot(delta_t_range, phase_errors, "o-", color="blue")
ax1.set_title("Ramsey Phase Error")
ax1.set_xlabel("δt (ns)")
ax1.set_ylabel("Δφ (deg)")

ax2.plot(delta_t_range, fidelities, "s-", color="red")
ax2.set_title("Bell State Fidelity")
ax2.set_xlabel("δt (ns)")
ax2.set_ylabel("Fidelity")
ax2.set_ylim(0, 1.05)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()

print("\n--- Done ---")
