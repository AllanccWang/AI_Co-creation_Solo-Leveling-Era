import numpy as np
import matplotlib.pyplot as plt
import qutip as qt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, thermal_relaxation_error

# =========================
# Global parameters
# =========================
D = 2.87          # Zero-field splitting (GHz)
gamma = 28.0      # Gyromagnetic ratio (GHz/T)
Omega = 0.05      # Rabi frequency (GHz)

# =========================
# STEP 1–2: Rabi oscillations (qubit model)
# =========================
# Use a qubit Hamiltonian H = 0.5*omega0*σz + 0.5*Omega*σx to get a clear Rabi curve.
omega0 = 1.0      # Splitting in arbitrary units for visualization
tlist = np.linspace(0, 10, 400)  # time (arb. units)

psi0 = qt.basis(2, 0)  # |0>
H_rabi = 0.5*omega0*qt.sigmaz() + 0.5*Omega*qt.sigmax()
result_rabi = qt.sesolve(H_rabi, psi0, tlist)        # store full states
P1 = qt.expect(qt.num(2), result_rabi.states)        # P(|1>) expectation

# =========================
# STEP 3–4: ODMR spectrum & calibration (NV model, qubit approximation)
# =========================
def odmr_spectrum(B_z, freqs):
    """
    Compute ODMR P(|0>) vs microwave frequency for given B_z (Tesla).
    Uses effective two-level model in rotating frame.
    """
    psi0 = qt.basis(2, 0)
    t_pi = np.pi / Omega
    p0 = np.zeros_like(freqs)

    resonance = D + gamma * B_z  # transition frequency (GHz)
    for i, f in enumerate(freqs):
        detuning = f - resonance
        H_eff = 0.5*detuning*qt.sigmaz() + 0.5*Omega*qt.sigmax()
        res = qt.sesolve(H_eff, psi0, [0, t_pi], e_ops=[qt.num(2)])
        p0[i] = res.expect[0][-1].real
    return p0

freqs = np.linspace(2.8, 2.95, 60)          # microwave scan (GHz)
B_fields = np.linspace(0, 0.1, 6)           # 0–0.1 T
peak_shifts = []

for B in B_fields:
    p0_B = odmr_spectrum(B, freqs)
    peak_freq = freqs[np.argmin(p0_B)]
    peak_shifts.append(peak_freq - D)

peak_shifts = np.array(peak_shifts)
gamma_fit = np.polyfit(B_fields*1000, peak_shifts*1000, 1)[0]  # MHz/mT

# =========================
# STEP 5: T2 decoherence via Ramsey (Qiskit)
# =========================
def ramsey_snr(delay_us, t1=1000.0, t2=10.0):
    """
    Single Ramsey fringe contrast (SNR) for a given free-evolution delay (microseconds).
    """
    qc = QuantumCircuit(1, 1)
    qc.rx(np.pi/2, 0)                       # π/2
    qc.delay(int(delay_us*1000), unit='dt') # delay in 'dt' (1 ns units)
    qc.rx(np.pi/2, 0)                       # π/2
    qc.measure(0, 0)

    noise_model = NoiseModel()
    # Convert all times to ns for thermal_relaxation_error
    error_gate = thermal_relaxation_error(t1*1000, t2*1000, delay_us*1000)
    noise_model.add_all_qubit_quantum_error(error_gate, ['rx', 'delay'])

    sim = AerSimulator(method='density_matrix', noise_model=noise_model)
    compiled = transpile(qc, sim)
    job = sim.run(compiled, shots=1024)
    counts = job.result().get_counts()
    p0 = counts.get('0', 0) / 1024
    return abs(p0 - 0.5)

delays = np.array([1, 2, 5, 10, 20])  # μs
snrs = np.array([ramsey_snr(d) for d in delays])

# =========================
# PLOTS: Rabi, ODMR, calibration, T2
# =========================
plt.figure(figsize=(12, 8))

# Rabi oscillations
plt.subplot(2, 2, 1)
plt.plot(tlist, P1, 'b-', lw=2)
plt.xlabel('Time (arb. u.)')
plt.ylabel('P(|1⟩)')
plt.title('Rabi Oscillations')
plt.grid(True)

# ODMR spectra
plt.subplot(2, 2, 2)
p0_B0 = odmr_spectrum(0.0, freqs)
p0_B50 = odmr_spectrum(0.05, freqs)
plt.plot(freqs, p0_B0, 'b-', lw=2, label='B = 0 mT')
plt.plot(freqs, p0_B50, 'r--', lw=2, label='B = 50 mT')
plt.xlabel('Microwave Frequency (GHz)')
plt.ylabel('P(|0⟩)')
plt.title('ODMR Spectra')
plt.legend()
plt.grid(True)

# Calibration Δf vs B
plt.subplot(2, 2, 3)
plt.plot(B_fields*1000, peak_shifts*1000, 'ro-', lw=2, ms=6)
plt.xlabel('B_z (mT)')
plt.ylabel('Peak Shift Δf (MHz)')
plt.title(f'Calibration γ ≈ {gamma_fit:.1f} MHz/mT')
plt.grid(True)

# T2 decoherence
plt.subplot(2, 2, 4)
plt.plot(delays, snrs, 'go-', lw=2, ms=6)
plt.xlabel('Delay (μs)')
plt.ylabel('Ramsey SNR')
plt.title('T2 Decoherence (T2 = 10 μs)')
plt.grid(True)

plt.tight_layout()
plt.show()

# =========================
# STEP 6: Bloch sphere trajectory for Rabi
# =========================
from qutip import Bloch

b = Bloch()
b.add_states(result_rabi.states)  # full trajectory
b.point_marker = ['o']
b.point_color = ['r']
b.show()

print(f"γ_fit ≈ {gamma_fit:.1f} MHz/mT  (ideal ≈ 28 MHz/mT)")
# --- keep figures open when running as .py ---
input("Press <Enter> to close plots and exit...")