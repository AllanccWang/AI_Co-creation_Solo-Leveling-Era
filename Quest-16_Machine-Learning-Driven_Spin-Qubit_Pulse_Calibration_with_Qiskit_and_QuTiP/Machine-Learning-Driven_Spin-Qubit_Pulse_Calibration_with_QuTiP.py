import numpy as np
import matplotlib.pyplot as plt
from qutip import *
from skopt import gp_minimize
from skopt.space import Real
from skopt.utils import use_named_args
from skopt.plots import plot_convergence, plot_objective
import warnings  # <-- Added this line to fix NameError

# ------------------------------------
# 1. Physical Model Setup
# ------------------------------------
def gaussian_pulse(tlist, sigma, amp, center):
    """
    Generate a Gaussian pulse
    tlist: time array
    sigma: pulse width
    amp:   pulse amplitude
    center: pulse center time
    """
    # Ensure we do not divide by zero
    sigma_safe = max(sigma, 1e-9) 
    return amp * np.exp(-(tlist - center)**2 / (2 * sigma_safe**2))

def simulate_pulse_dynamics(H_drift, H_control, psi0, sigma, amp, duration=10):
    """
    Simulate quantum dynamics
    """
    tlist = np.linspace(0, duration, 200)
    pulse = gaussian_pulse(tlist, sigma, amp, center=duration/2)
    
    # Define time-dependent Hamiltonian H(t) = H0 + f(t)*H1
    # Format: [static term, [operator, time-dependent coefficient (NumPy array)]]
    H = [H_drift, [H_control, pulse]] 
    
    # Perform evolution (Schrödinger Equation)
    # Use warnings.catch_warnings to suppress FutureWarning from older QuTiP versions
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        result = sesolve(H, psi0, tlist, options=Options(store_states=True, nsteps=5000))
        
    return result.states[-1]

# ------------------------------------
# 2. Bayesian Optimization Core
# ------------------------------------
def run_gp_optimization(gate_name, psi0, target_state, H_drift, H_control):
    print(f"\n--- Start optimization for {gate_name} Gate ---")
    
    # === A. Define Search Space ===
    space = [
        Real(0.1, 8.0, name='sigma'),
        Real(0.1, 10.0, name='amp')
    ]

    # === B. Define Objective Function ===
    @use_named_args(space)
    def objective(sigma, amp):
        psi_final = simulate_pulse_dynamics(H_drift, H_control, psi0, sigma, amp)
        fidelity = np.abs(psi_final.overlap(target_state))**2
        
        if np.isnan(fidelity):
             return 1.0  # Penalty value
        
        return -fidelity  # Minimize -Fidelity

    # === C. Run GP-BO ===
    res = gp_minimize(objective, space, n_calls=40, random_state=42, verbose=True, 
                      n_initial_points=10)

    # === D. Result Analysis ===
    best_fidelity = -res.fun
    best_sigma = res.x[0]
    best_amp = res.x[1]
    
    print(f"\n{gate_name} Gate best result:")
    print(f"  ✅ Max Fidelity: {best_fidelity:.6f}")
    print(f"  ✅ Best Sigma:   {best_sigma:.4f}")
    print(f"  ✅ Best Amp:     {best_amp:.4f}")

    # === E. Visualization (Optimized plots) ===
    
    # 1. Convergence Plot
    # Increase figure size to 8x5
    plt.figure(figsize=(8, 5)) 
    plot_convergence(res)
    plt.title(f"{gate_name} Gate - Optimization Convergence (GP-BO)")
    plt.tight_layout()  # <-- Added: auto adjust layout
    plt.savefig(f"{gate_name}_Convergence.png")
    
    # 2. Objective Landscape Plot
    # Increase figure size to 12x10 to ensure labels are not overlapping or cut off
    plt.figure(figsize=(12, 10)) 
    plot_objective(res, dimensions=['sigma', 'Amp'])
    plt.suptitle(f"{gate_name} Gate - Parameter Landscape")
    # Adjust tight_layout parameters to avoid suptitle being cut off
    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) 
    plt.savefig(f"{gate_name}_Landscape.png")
    
    # Close figures to free memory
    plt.close('all') 
    
    return res

# ------------------------------------
# 3. Main Program Execution
# ------------------------------------
if __name__ == "__main__":
    # Define Hamiltonians
    sx, sy, sz = sigmax(), sigmay(), sigmaz()
    H0 = 0.2 * sz     # Drift term
    
    # --- Calibrate X Gate ---
    psi0 = basis(2, 0)
    target_x = basis(2, 1)
    run_gp_optimization("X", psi0, target_x, H0, sx)

    # --- Calibrate Y Gate ---
    psi0 = basis(2, 0)
    target_y = -1j * basis(2, 1)  # Y gate transforms |0> to -i|1>
    run_gp_optimization("Y", psi0, target_y, H0, sy)
    
    # --- Calibrate Z Gate ---
    psi_plus = (basis(2,0) + basis(2,1)).unit()
    psi_minus = (basis(2,0) - basis(2,1)).unit()
    run_gp_optimization("Z", psi_plus, psi_minus, H0, sz)
