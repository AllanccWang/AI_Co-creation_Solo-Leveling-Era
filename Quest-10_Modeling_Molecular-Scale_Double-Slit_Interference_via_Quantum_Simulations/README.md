# 🎯 Goal

The **double-slit experiment** is one of the most iconic demonstrations in quantum mechanics, revealing the **wave–particle duality** of matter. When a single quantum particle — such as an electron — passes through a pair of slits, its **wavefunction interferes with itself**, producing a characteristic interference pattern on the detection screen.  

This interference pattern reflects the **coherent superposition of possible paths** and serves as a powerful probe for **decoherence** and **environmental noise**.

In this project, we use **quantum circuits** to simulate this phenomenon.  
- **Phase 1** focuses on a single qubit, mimicking a minimal quantum interference experiment.  
- **Phase 2** extends the system to multiple coupled qubits, capturing how **complexity and environmental coupling** can suppress interference.

---

# 🧭 Quests

## Phase 1 — Single-Qubit Interference and Noise

In this phase, we build and simulate a minimal quantum double-slit interferometer using a **single qubit**.

The circuit structure:
- **Hadamard gate (H)** — creates a superposition, analogous to a particle traversing both slits simultaneously.  
- **Phase shift gate (P(φ))** — introduces a controllable relative phase between the two paths.  
- **Second Hadamard gate (H)** — recombines the paths to produce interference.

By **sweeping the phase shift φ**, we obtain sinusoidal interference fringes in the measurement probabilities of |0⟩ and |1⟩.  

We then introduce different **noise channels**:
- Depolarizing noise — random bit and phase flips.  
- Phase damping — dephasing without energy loss.  
- Amplitude damping — energy relaxation.

The goal is to **quantify how each type of noise affects interference visibility**, i.e., the contrast between maximum and minimum fringe intensities.

---

## Phase 2 — Multi-Qubit Coupling and Interference Suppression

In Phase 2, we extend the model to **multiple coupled qubits**, representing larger and more complex quantum systems such as **molecules**.  

The **qubit coupling** acts as an **effective environment** or **internal degrees of freedom**, introducing **entanglement** that can lead to **decoherence** and **suppression of interference**.

We systematically vary:
- **Number of qubits** — to model increasing system size,  
- **Phase shift** — to explore how path differences scale with complexity,  
- **Noise strength** — to mimic environmental disturbances.

This allows us to study how **interference patterns degrade** as systems grow in size and complexity, providing insight into **quantum-to-classical transitions** and the role of **environmental coupling** in decoherence.
