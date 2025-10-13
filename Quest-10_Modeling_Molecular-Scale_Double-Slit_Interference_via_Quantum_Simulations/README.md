# Goal
The double-slit experiment is one of the most fundamental demonstrations of quantum interference, illustrating the wave–particle duality of matter. When a single quantum particle, such as an electron, passes through a pair of slits, its wavefunction interferes with itself, producing a characteristic interference pattern on the detection screen. This pattern reflects the coherent superposition of possible paths and serves as a sensitive probe for decoherence and environmental noise.

In this project, we use quantum circuits to simulate a double-slit interference experiment using a single qubit and then extend the system to multiple coupled qubits to mimic interference behavior of larger, more complex molecular systems.

Phase 1 — Single-Qubit Interference and Noise: 
In this phase, we simulate a basic quantum interference experiment using a single qubit.

Phase 2 — Multi-Qubit Coupling and Interference Suppression: 
In Phase 2, we extend the model to multiple coupled qubits, representing larger composite quantum systems such as molecules.
The coupling simulates internal degrees of freedom or environmental entanglement, which can lead to decoherence and loss of interference visibility.

# Quests
*Phase 1 — Single-Qubit Interference and Noise:*
In Phase 1, we simulate a basic quantum interference experiment using a single qubit.
The circuit consists of:

* A Hadamard gate to create a superposition (analogous to splitting through two slits).
* A phase shift gate to mimic relative path difference between the slits.
* A second Hadamard gate to recombine the paths and produce interference at the measurement stage.

By sweeping the phase shift, we obtain sinusoidal probability fringes for measurement outcomes |0> and |1>.
We then study the effect of different noise channels — depolarizing, phase damping, and amplitude damping — and observe their impact on interference visibility, i.e., the contrast between maximum and minimum fringe intensities.

*Phase 2 — Multi-Qubit Coupling and Interference Suppression:*
In Phase 2, we extend the model to multiple coupled qubits, representing larger composite quantum systems such as molecules.
The coupling simulates internal degrees of freedom or environmental entanglement, which can lead to decoherence and loss of interference visibility.

We systematically vary:
* Number of qubits (system size),
* Phase shift (path difference),
* Noise strength (environmental disturbance),

to study how increasing complexity affects interference fringes.
