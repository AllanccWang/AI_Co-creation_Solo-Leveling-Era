import scqubits as scq
import numpy as np


# 1-1: define Transmon qubit and get its property
def define_transmon(N_Levels):
    transmon = scq.Transmon(EJ=12.5, EC=0.25, ng=0.0, ncut=30, truncated_dim=10)

    energies = transmon.eigenvals(evals_count=N_Levels)
    omega_01 = energies[1] - energies[0]
    omega_12 = energies[2] - energies[1]
    omega_23 = energies[3] - energies[2]

    n_op = transmon.n_operator()
    cos_phi_op = transmon.cos_phi_operator()
    sin_phi_op = transmon.sin_phi_operator()

    evals, evecs = transmon.eigensys(N_Levels)
    n_eigenbasis = evecs.T.conj() @ n_op @ evecs

    n01 = n_eigenbasis[0, 1]
    n12 = n_eigenbasis[1, 2]
    n23 = n_eigenbasis[2, 3]

    return {
        "energies": energies,
        "omega_01": omega_01,
        "omega_12": omega_12,
        "n_op": n_op,
        "cos_phi_op": cos_phi_op,
        "sin_phi_op": sin_phi_op,
        "n_eigenbasis": n_eigenbasis,
        "n01": n01,
        "n12": n12,
        "n23": n23,
    }


# 1-2: Qiskit Dynamics Solver
from qiskit_dynamics import Solver
from qiskit_dynamics.signals import Signal
from qiskit_dynamics.models import LindbladModel

def qiskit_simulation_with_dissipation(results, T1_target=20e-6):
    energies = results["energies"]
    H_static = np.array(np.diag(energies), dtype=complex)

    # collapse operator |0><1|
    C10 = np.zeros_like(H_static)
    C10[0,1] = 1.0

    gamma = 1.0 / T1_target
    dissipator = np.sqrt(gamma) * C10

    # static_dissipators，and avoid signals
    lindblad_model = LindbladModel(
        static_hamiltonian=H_static,
        static_dissipators=[dissipator],
        vectorized=True   # for solve_ivp
    )
    return lindblad_model

def qiskit_simulation(results, drive_freq, dt):
    energies = results["energies"]
    n_eigenbasis = results["n_eigenbasis"]
    # StaTic Hamiltonian (complex type)
    H_static = np.array(np.diag(energies), dtype=complex)
    # driven term (from scqubits and transfer to type, complex)
    H_drive = np.array(n_eigenbasis, dtype=complex)
    # create Solver，assign dt and channel_carrier_freqs
    solver = Solver(
        static_hamiltonian=H_static,
        hamiltonian_operators=[H_drive],
        hamiltonian_channels=["d0"],
        channel_carrier_freqs={"d0": drive_freq},  # Hz
        dt=dt
    )
    return solver

def run_spectroscopy(results, solver, y0, freq_range=None):
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.optimize import curve_fit

    # Sweep around eigenvalue estimate if not provided
    if freq_range is None:
        f01_est = results["omega_01"]
        freq_range = np.linspace(f01_est - 20e6, f01_est + 20e6, 40)  # 粗掃

    P1_values = []

    # Use a long, low-amplitude drive tone
    tau = 80  # ns
    A = 0.2    # small amplitude

    for f in freq_range:
        drive_signal = Signal(lambda t: A * np.cos(2*np.pi*f*t))
        solution = solver.solve(t_span=[0.0, tau], y0=y0, signals=[drive_signal])
        final_state = solution.y[-1]
        P1 = np.abs(final_state[1])**2
        P1_values.append(P1)

    # Lorentzian fit
    def lorentzian(f, f0, gamma, A, C):
        return A * gamma**2 / ((f - f0)**2 + gamma**2) + C

    popt, _ = curve_fit(lorentzian, freq_range, P1_values,
                        p0=[results["omega_01"], 5e6, max(P1_values), min(P1_values)])
    f0_fit, gamma_fit, A_fit, C_fit = popt

    # Plot
    plt.figure(figsize=(8,5))
    plt.plot(freq_range/1e9, P1_values, 'o-', label='Simulated')
    plt.plot(freq_range/1e9, lorentzian(freq_range, *popt), '--',
             label=f'Fit f01={f0_fit/1e9:.6f} GHz')
    plt.xlabel("Drive frequency (GHz)")
    plt.ylabel("Excited state population P1")
    plt.title("Spectroscopy Scan")
    plt.grid(True)
    plt.legend()
    plt.show()

    print(f"Estimated f01 ≈ {f0_fit:.6e} Hz")
    return f0_fit

from qiskit_dynamics.models import LindbladModel
import numpy as np

def qiskit_simulation_with_dephasing(results, T1_target=20e-6, Tphi_target=5e-6):
    energies = results["energies"]
    H_static = np.array(np.diag(energies), dtype=complex)

    # Collapse operator for T1: |0><1|
    C10 = np.zeros_like(H_static)
    C10[0,1] = 1.0
    gamma1 = 1.0 / T1_target
    dissipator_T1 = np.sqrt(gamma1) * C10

    # Collapse operator for pure dephasing: σ_z
    sigma_z = np.diag([1, -1, 0, 0])  # restrict to first two levels
    gamma_phi = 1.0 / Tphi_target
    dissipator_dephasing = np.sqrt(gamma_phi) * sigma_z

    # Build Lindblad model with both dissipators
    lindblad_model = LindbladModel(
        static_hamiltonian=H_static,
        static_dissipators=[dissipator_T1, dissipator_dephasing],
        vectorized=True
    )
    return lindblad_model