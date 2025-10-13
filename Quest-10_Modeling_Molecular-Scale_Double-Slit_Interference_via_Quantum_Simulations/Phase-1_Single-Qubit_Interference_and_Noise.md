# Phase 1 — Single-Qubit Double-Slit Interference and Noise

## 🎯 Goal
This phase aims to reproduce a **quantum double-slit interference pattern** using a **single qubit** as an analog to a single-particle interferometer.

The quantum circuit consists of:
- **Hadamard gate (H)** — creates a superposition, analogous to splitting the wavefunction through two slits.  
- **Phase shift gate (P(φ))** — introduces a relative phase difference between the two paths.  
- **Second Hadamard gate (H)** — recombines the paths, producing interference at the measurement stage.

<img align="justify" src="./Phase-1_Single-Qubit_Interference_and_Noise/Single-qubit_double-slit_quantum_circuit.PNG" alt="Single-qubit_double-slit_quantum_circuit_IMG" style="width:60%">

By **sweeping the phase** φ from \( 0 \) to \( 2\pi \), we obtain sinusoidal interference fringes for the probabilities of measuring \(|0\rangle\) and \(|1\rangle\).  

To study the effect of decoherence, we introduce different **noise channels**:
- **Depolarizing noise** — random bit and phase flips.  
- **Phase damping** — loss of phase coherence (dephasing).  
- **Amplitude damping** — energy relaxation (spontaneous emission).

We then **quantify the impact on interference visibility**, i.e., the contrast between the maximum and minimum intensities of the fringes.

📜 The simulation code is available [**here**](https://github.com/AllanccWang/AI_Co-creation_Solo-Leveling-Era/blob/645309973ad9af674d884936b3f9fcd60981cf0e/Quest-10_Modeling_Molecular-Scale_Double-Slit_Interference_via_Quantum_Simulations/Phase-1_Single-Qubit_Interference_and_Noise/Single-Qubit_Double-Slit.py).

---

## 🧪 Results

### 1. Depolarizing Noise
`depolarizing_error(p)` introduces **random bit and phase errors**, reducing coherence and **lowering interference visibility** as \( p \) increases.

<img align="justify" src="./Phase-1_Single-Qubit_Interference_and_Noise/Single-Qubit_Double-Slit_depolarizing_error.png" alt="Single-Qubit_Double-Slit_depolarizing_error_IMG" style="width:60%">

---

### 2. Phase Damping
`phase_damping_error(p)` models **pure dephasing**, i.e., loss of phase coherence without energy loss.

<img align="justify" src="./Phase-1_Single-Qubit_Interference_and_Noise/Single-Qubit_Double-Slit_phase_damping_error.png" alt="Single-Qubit_Double-Slit_phase_damping_error_IMG" style="width:60%">

📌 **Observation:**  
Phase damping has almost **no visible impact** in this circuit.  
This is because:
- The superposition state exists for only a **very short circuit depth** before being converted to population by the final Hadamard gate.
- Phase damping occurs between gates, but there is insufficient “idle time” for dephasing to accumulate.
- As a result, the **interference pattern remains nearly unchanged** for typical noise strengths in this setup.

---

### 3. Amplitude Damping
`amplitude_damping_error(p)` represents **energy relaxation**, where excited states \(|1\rangle\) decay to \(|0\rangle\).

<img align="justify" src="./Phase-1_Single-Qubit_Interference_and_Noise/Single-Qubit_Double-Slit_amplitude_damping_error.png" alt="Single-Qubit_Double-Slit_amplitude_damping_error_IMG" style="width:60%">

Amplitude damping **distorts the fringe pattern** by biasing outcomes toward \(|0\rangle\), especially as \( p \) increases.

---

## 📊 Summary of Findings
| Noise Type              | Effect on Interference Pattern                        | Visibility |
|--------------------------|----------------------------------------------------------|------------|
| **Depolarizing**         | Reduces overall coherence, lowers fringe contrast        | ↓ Moderate |
| **Phase damping**        | Minimal effect for short circuits                        | ≈ Constant |
| **Amplitude damping**    | Biases results toward \(|0\rangle\), distorts fringes    | ↓ Strong   |

> 📝 *Key Insight*:  
> Phase damping becomes significant only when the superposition is **maintained over a longer circuit depth** (e.g., idle times or multiple operations).  
> For a minimal double-slit circuit, **depolarizing and amplitude damping** dominate the interference degradation.

---

## 🧭 Next Steps
- Introduce **delays or additional gates** to study **time-dependent dephasing**.  
- Extend to **Phase 2** with multi-qubit coupling to simulate molecular-scale systems and environment-induced decoherence.
- Analyze **interference visibility quantitatively** as a function of noise strength.

---

This version:
✅ Improves structure (clear sections: goal, results, summary, next steps)  
✅ Adds scientific language but keeps it readable  
✅ Explains **why phase damping seems invisible** clearly  
✅ Gives a **table comparison** at the end for clarity

Would you like me to make a **shorter “presentation slide version”** of this too (e.g., bullet points only, no paragraphs)?
