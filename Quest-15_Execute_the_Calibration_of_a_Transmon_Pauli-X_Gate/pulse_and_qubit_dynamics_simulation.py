import numpy as np
from qiskit_dynamics.signals import Signal
import matplotlib.pyplot as plt

def H_drive(t, H_static, O_hat, omega_d, A, t0, sigma):
    """
    time-dependence hamiltonian H(t) = H0 + Ω(t)cos(ω_d t) O_hat    
    Parms:
    - H_static: static hamiltonian (np.array)
    - O_hat: operator (np.array)
    - omega_d: driven frequency
    - A: pulse amplitude
    - t0: gaussian pulse center
    - sigma: width of gaussian pulse
    """
    # Gauss package
    Omega_t = A * np.exp(-(t - t0)**2 / (2 * sigma**2))    
    # driver term
    H_t = H_static + Omega_t * np.cos(omega_d * t) * O_hat
    return H_t

def gaussian_pulse(A, results, tau, sigma=None):
    if sigma is None:
        sigma = tau/5.0
    t0 = tau/2.0
    return Signal(lambda t: A * np.exp(-(t - t0)**2 / (2*sigma**2)) * np.cos(results["omega_01"]*t))
        
# Rabi oscillation - Rabi Curve: A vs P1
def Rabi_Curve_A_vs_P1(results, solver, t_span, tau, y0):
    # Step 3-1: sweep different amplitude
    A_values = np.linspace(0, 2.0, 20)
    P1_values = []
    final_states = []
    for A in A_values:
        # create Solver
        drive_signal = gaussian_pulse(A, results, tau)
        solution = solver.solve(t_span=t_span, y0=y0, signals=[drive_signal])
        final_state = solution.y[-1]
        # P1 = |ψ_1|^2
        P1 = np.abs(final_state[1])**2
        P1_values.append(P1)
        final_states.append(final_state)
    # find π-pulse (Maximum P1)
    A_pi = A_values[np.argmax(P1_values)]
    P1_pi = max(P1_values)
    final_state_pi = final_states[np.argmax(P1_values)]
    # # Plot Rabi Curve: A vs P1
    # plt.figure(figsize=(8,5))
    # plt.plot(A_values, P1_values, 'o-', color='blue')
    # plt.xlabel("Pulse Amplitude A")
    # plt.ylabel("Population P1")
    # plt.title("Rabi Curve: A vs P1")
    # plt.grid(True)
    # # mark π-pulse
    # plt.axvline(A_pi, color='red', linestyle='--', label=f"π-pulse ~ A={A_pi:.2f}")
    # plt.scatter([A_pi], [P1_pi], color='red')
    # plt.legend()
    # plt.show()
    return A_pi, P1_pi, final_state_pi

# Plot Rabi oscillation vs time
def Rabi_oscillation_vs_time(results, solver, A_pi, y0):
    times = np.linspace(0, 200, 50)   # sweeping time duration (ns)
    P1_values = []
    for tau in times:
        drive_signal = gaussian_pulse(A_pi, results, tau=tau)
        solution = solver.solve(t_span=[0.0, tau], y0=y0, signals=[drive_signal])
        final_state = solution.y[-1]
        P1 = np.abs(final_state[1])**2
        P1_values.append(P1)    
    plt.figure(figsize=(8,5))
    plt.plot(times, P1_values, 'o-', color='green')
    plt.xlabel("Pulse duration τ (ns)")
    plt.ylabel("Population P1")
    plt.title("Rabi Oscillation vs Time")
    plt.grid(True)
    plt.show()

def Bloch_sphere_visualization(results, solver, A_pi, tau, y0):
    from qiskit.visualization.bloch import Bloch
    # Simulate with calibrated pulse
    drive_signal = gaussian_pulse(A_pi, results, tau)  # σ defaults to τ/5
    sol = solver.solve(t_span=[0.0, tau], y0=y0, signals=[drive_signal])

    bloch = Bloch()
    points = []
    for psi in sol.y:
        alpha, beta = psi[0], psi[1]  # project to two-level subspace
        x = 2*np.real(np.conj(alpha)*beta)
        y = 2*np.imag(np.conj(alpha)*beta)
        z = np.abs(alpha)**2 - np.abs(beta)**2
        points.append([x, y, z])

    bloch.add_points(points)
    bloch.add_vectors([points[-1]])  # final state indicator
    bloch.render()
    plt.show()

    # Also print final populations for reference
    psi = sol.y[-1]
    P = np.abs(psi[:4])**2
    print(f"P0={P[0]:.4f}, P1={P[1]:.4f}, P2={P[2]:.6f}, P3={P[3]:.6f}")