from pulse_and_qubit_dynamics_simulation import gaussian_pulse
from qiskit_dynamics.signals import Signal
import numpy as np

def run_ramsey_calibration(results, solver, A_pi, y0, delay_ns_list=None):
    import matplotlib.pyplot as plt
    from scipy.optimize import curve_fit

    if delay_ns_list is None:
        delay_ns_list = np.linspace(0, 300, 25)  # ns

    tau_pi2 = 50  # ns
    P1_values = []

    for delay_ns in delay_ns_list:
        delay_s = delay_ns * 1e-9
        tau_s = tau_pi2 * 1e-9

        #  π/2 pulse envelope
        signal = gaussian_pulse(A_pi, results, tau=tau_pi2)

        # signal_time
        signal_times = [
            [0.0, tau_s],                          # 1st π/2 pulse
            [tau_s + delay_s, 2*tau_s + delay_s]   # 2nd π/2 pulse
        ]

        total_time = 2*tau_s + delay_s
        solution = solver.solve(
            t_span=[0.0, total_time],
            y0=y0,
            signals=[signal],
            signal_times=signal_times
        )

        final_state = solution.y[-1]
        P1 = np.abs(final_state[1])**2
        P1_values.append(P1)

    # P1 vs delay
    def ramsey_fit(t, A, f, phi, C):
        return A * np.cos(2*np.pi*f*t + phi)**2 + C

    delay_s_list = delay_ns_list * 1e-9
    popt, _ = curve_fit(ramsey_fit, delay_s_list, P1_values, p0=[0.5, 1e6, 0, 0.5])
    A_fit, f_detune, phi_fit, C_fit = popt

    # Plot
    plt.figure(figsize=(8,5))
    plt.plot(delay_ns_list, P1_values, 'o-', label='Simulated')
    plt.plot(delay_ns_list, ramsey_fit(delay_s_list, *popt), '--', label=f'Fit Δf={f_detune/1e6:.2f} MHz')
    plt.xlabel("Delay (ns)")
    plt.ylabel("Population P1")
    plt.title("Ramsey Oscillation")
    plt.grid(True)
    plt.legend()
    plt.show()

    print(f"Estimated detuning Δf ≈ {f_detune:.2f} Hz")
    return f_detune

def run_T2_star_measurement(results, solver, A_pi, y0, delay_ns_list=None):
    import matplotlib.pyplot as plt
    from scipy.optimize import curve_fit
    import numpy as np

    if delay_ns_list is None:
        delay_ns_list = np.linspace(0, 3000, 30)  # ns

    tau_pi2 = 50  # ns, π/2 pulse duration
    A_pi2 = A_pi / 2.0  # π/2 pulse amplitude
    P1_values = []

    for delay_ns in delay_ns_list:
        delay_s = delay_ns * 1e-9
        tau_s = tau_pi2 * 1e-9

        # π/2 pulse envelope
        signal = gaussian_pulse(A_pi2, results, tau=tau_pi2)

        # signal_times: 1st π/2 pulse + 2nd π/2 pulse，delay in middle
        signal_times = [
            [0.0, tau_s],
            [tau_s + delay_s, 2*tau_s + delay_s]
        ]

        total_time = 2*tau_s + delay_s
        solution = solver.solve(
            t_span=[0.0, total_time],
            y0=y0,
            signals=[signal],
            signal_times=signal_times
        )

        final_state = solution.y[-1]
        P1 = np.abs(final_state[1])**2
        P1_values.append(P1)

    # fitting curve with cos × exp
    def ramsey_decay(t, A, f, phi, T2star, C):
        return A * np.cos(2*np.pi*f*t + phi)**2 * np.exp(-t/T2star) + C

    delay_s_list = delay_ns_list * 1e-9
    popt, _ = curve_fit(ramsey_decay, delay_s_list, P1_values,
                        p0=[0.5, 1e6, 0, 1e-6, 0.5])
    A_fit, f_detune, phi_fit, T2star_fit, C_fit = popt

    # Plot
    plt.figure(figsize=(8,5))
    plt.plot(delay_ns_list, P1_values, 'o-', label='Simulated')
    plt.plot(delay_ns_list, ramsey_decay(delay_s_list, *popt), '--',
             label=f'Fit T2*={T2star_fit*1e9:.1f} ns, Δf={f_detune/1e6:.2f} MHz')
    plt.xlabel("Delay (ns)")
    plt.ylabel("Population P1")
    plt.title("T2* Measurement (Ramsey)")
    plt.grid(True)
    plt.legend()
    plt.show()

    print(f"Estimated T2* ≈ {T2star_fit:.6e} s, Detuning Δf ≈ {f_detune:.2f} Hz")
    return T2star_fit, f_detune

from scipy.integrate import solve_ivp
from qiskit_dynamics.signals import Signal
from scipy.integrate import solve_ivp

def run_T1_measurement_lindbladModel(results, lindblad_model, delay_ns_list=None):
    import matplotlib.pyplot as plt
    from scipy.optimize import curve_fit
    import numpy as np

    if delay_ns_list is None:
        delay_ns_list = np.linspace(0, 50000, 30)  # ns (0–50 μs)

    P1_values = []

    # 初始密度矩陣 (|1⟩)
    rho0 = np.zeros((4,4), dtype=complex)
    rho0[1,1] = 1.0
    rho0 = rho0.flatten()

    def lindblad_rhs(t, rho_vec):
        return lindblad_model.evaluate_rhs(t, rho_vec)

    for delay_ns in delay_ns_list:
        delay_s = delay_ns * 1e-9
        total_time = 50e-9 + delay_s

        sol = solve_ivp(lindblad_rhs, [0, total_time], rho0, t_eval=[total_time])
        rho_final = sol.y[:,-1].reshape((4,4))

        P1 = np.real(rho_final[1,1])
        P1_values.append(P1)

    # 擬合指數衰減
    def exp_decay(t, A, T1, C):
        return A * np.exp(-t/T1) + C

    delay_s_list = delay_ns_list * 1e-9
    popt, _ = curve_fit(exp_decay, delay_s_list, P1_values, p0=[1.0, 20e-6, 0.0])
    A_fit, T1_fit, C_fit = popt

    plt.figure(figsize=(8,5))
    plt.plot(delay_ns_list, P1_values, 'o-', label='Simulated')
    plt.plot(delay_ns_list, exp_decay(delay_s_list, *popt), '--',
             label=f'Fit T1={T1_fit*1e6:.1f} μs')
    plt.xlabel("Delay (ns)")
    plt.ylabel("Population P1")
    plt.title("T1 Measurement (Energy Relaxation)")
    plt.grid(True)
    plt.legend()
    plt.show()

    print(f"Estimated T1 ≈ {T1_fit:.6e} s")
    return T1_fit

def run_T1_measurement(results, solver, A_pi, y0, delay_ns_list= None):
    import matplotlib.pyplot as plt
    from scipy.optimize import curve_fit
    import numpy as np

    if delay_ns_list is None:
        delay_ns_list = np.linspace(0, 50000, 30)  # ns (0–50 μs)

    P1_values = []

    for delay_ns in delay_ns_list:
        delay_s = delay_ns * 1e-9

        # π pulse
        signal = gaussian_pulse(A_pi, results, tau=50)  # τ=50 ns, π pulse

        # signal_times: π pulse + delay time
        signal_times = [[0.0, 50e-9]]  # π pulse duration
        total_time = 50e-9 + delay_s

        # 用 Solver 演化
        solution = solver.solve(
            t_span=[0.0, total_time],
            y0=y0,
            signals=[signal],
            signal_times=signal_times
        )

        final_state = solution.y[-1]
        P1 = np.abs(final_state[1])**2
        P1_values.append(P1)

    # 擬合指數衰減
    def exp_decay(t, A, T1, C):
        return A * np.exp(-t/T1) + C

    delay_s_list = delay_ns_list * 1e-9
    popt, _ = curve_fit(exp_decay, delay_s_list, P1_values, p0=[1.0, 20e-6, 0.0])
    A_fit, T1_fit, C_fit = popt

    # Plot
    plt.figure(figsize=(8,5))
    plt.plot(delay_ns_list, P1_values, 'o-', label='Simulated')
    plt.plot(delay_ns_list, exp_decay(delay_s_list, *popt), '--',
             label=f'Fit T1={T1_fit*1e6:.1f} μs')
    plt.xlabel("Delay (ns)")
    plt.ylabel("Population P1")
    plt.title("T1 Measurement (Energy Relaxation)")
    plt.grid(True)
    plt.legend()
    plt.show()

    print(f"Estimated T1 ≈ {T1_fit:.6e} s")
    return T1_fit
def run_echo_T2_measurement(results, solver, A_pi, y0, delay_ns_list=None):
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.optimize import curve_fit
    from pulse_and_qubit_dynamics_simulation import gaussian_pulse

    if delay_ns_list is None:
        delay_ns_list = np.linspace(0, 5000, 25)  # ns (0–5 μs)

    tau_pi2 = 50   # ns, π/2 pulse duration
    tau_pi  = 50   # ns, π pulse duration
    A_pi2   = A_pi / 2.0  # π/2 pulse amplitude

    P1_values = []

    for delay_ns in delay_ns_list:
        delay_s = delay_ns * 1e-9
        tau_s_pi2 = tau_pi2 * 1e-9
        tau_s_pi  = tau_pi * 1e-9

        # Only one signal is needed, since Solver has one operator
        signal = gaussian_pulse(A_pi, results, tau=tau_pi)

        # Define the pulse sequence: π/2 → delay → π → delay → π/2
        signal_times = [
            [0.0, tau_s_pi2],                                # first π/2 pulse
            [tau_s_pi2 + delay_s, tau_s_pi2 + delay_s + tau_s_pi],  # π pulse
            [tau_s_pi2 + delay_s + tau_s_pi + delay_s,
             tau_s_pi2 + delay_s + tau_s_pi + delay_s + tau_s_pi2]  # final π/2 pulse
        ]

        total_time = tau_s_pi2 + 2*delay_s + tau_s_pi + tau_s_pi2

        solution = solver.solve(
            t_span=[0.0, total_time],
            y0=y0,
            signals=[signal],          # one signal
            signal_times=signal_times  # control pulse timing
        )

        final_state = solution.y[-1]
        P1 = np.abs(final_state[1])**2
        P1_values.append(P1)

    # Fit exponential decay
    def echo_decay(t, A, T2, C):
        return A * np.exp(-t/T2) + C

    delay_s_list = delay_ns_list * 1e-9
    popt, _ = curve_fit(echo_decay, 2*delay_s_list, P1_values, p0=[0.5, 2e-6, 0.5])
    A_fit, T2_fit, C_fit = popt

    # Plot results
    plt.figure(figsize=(8,5))
    plt.plot(2*delay_ns_list, P1_values, 'o-', label='Simulated')
    plt.plot(2*delay_ns_list, echo_decay(2*delay_s_list, *popt), '--',
             label=f'Fit T2={T2_fit*1e6:.1f} μs')
    plt.xlabel("Total delay 2τ (ns)")
    plt.ylabel("Population P1")
    plt.title("Echo (T2) Measurement")
    plt.grid(True)
    plt.legend()
    plt.show()

    print(f"Estimated T2 ≈ {T2_fit:.6e} s")
    return T2_fit
