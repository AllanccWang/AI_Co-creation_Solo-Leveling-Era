# Phase 2 — Modeling Molecular-Scale Double-Slit Interference

🎯 **Goal**  
Extend the single-qubit double-slit model (Phase 1) into a **multi-qubit “molecular” interference model**, capturing how internal degrees of freedom degrade interference visibility.

---

## 🧩 Conceptual Model

- **Path qubit(s):** represent which slit the particle/molecule goes through.  
- **Internal qubits:** represent internal states of a larger molecule (vibrations, rotations, etc.).  
- **Entanglement:** controlled-RY gates couple the path qubit to internal qubits, simulating which-path marking.  
- **Measurement:** only the path qubit is analyzed; internal qubits are marginalized out, acting like an “environment.”  

**Analogy to real experiments:**

- Increasing **mass/size** → shorter de Broglie wavelength + more internal degrees of freedom.  
- Larger molecules → weaker interference fringes.  
- Circuit toy model: **more internal qubits ≈ larger molecule**.

---

## ⚙️ Quantum Circuit

1. **Hadamard (H)** on path qubit → creates superposition of “left slit” and “right slit.”  
2. **Phase gate P(φ)** → introduces relative phase between the two paths.  
3. **Controlled-RY rotations** from path qubit to each internal qubit:  
   - If path = |0⟩ → apply RY(+θ).  
   - If path = |1⟩ → apply RY(−θ).  
4. **Hadamard (or QFT)** on path qubit → maps phase information into measurement basis.  
5. **Measurement:** all qubits measured, but analysis keeps only the path qubit distribution.

---

## 🔍 Key Observations

### Probability vs Phase
- **Phase 1 (single qubit):**  
  - Clean sinusoidal fringes:  
    - $$P(\text{path}=0) = \cos^2\left(\tfrac{\phi}{2}\right)$$  
    - $$P(\text{path}=1) = \sin^2\left(\tfrac{\phi}{2}\right)$$  
- **Phase 2 (multi-qubit):**  
  - Adding internal qubits reshapes curves:  
    - Peaks sharpen, valleys lift, contrast decreases.  
  - More internal qubits → more washed-out interference.

### Effect of Noise
- **Small phase damping (p = 0.02, 0.05):** minor effect compared to entanglement.  
- **Dominant factor:** number of internal qubits, not small external noise.  
- **High noise (p = 1):** interference collapses completely.

---

## ❓ Questions & Answers

**Q: Why did Phase 1 curves look almost the same for different noise strengths?**  
A: With only one qubit, phase damping just attenuates coherence uniformly. The fringe shape remains the same, only slightly flattened.

**Q: Why does Phase 2 change dramatically with qubit number, but not with small noise?**  
A: Internal qubits act like an environment. Entanglement leaks which-path information, dominating decoherence. Small noise is secondary.

**Q: What’s the physical analogy?**  
- Phase 1 = single atom double slit → clean fringes.  
- Phase 2 = large molecule double slit → internal states carry away path info, fringes blur.  
- Noise = “fog in the lab,” but main decoherence comes from molecular complexity.

---

## ✅ Summary

- **Microscopic particles (electrons, atoms):** long de Broglie wavelength, clean fringes.  
- **Mesoscopic/large molecules (C₆₀, proteins):** shorter wavelength + internal decoherence → blurred fringes.  
- **Macroscopic objects:** wave nature exists in principle, but decoherence dominates, making interference unobservable.  

**Key Insight:**  
Phase 2 shows that **entanglement with internal degrees of freedom** (molecular size) is the primary cause of interference degradation, not small external noise. This mirrors real molecular interference experiments.

---

📌 *This Phase 2 model builds directly on [Phase 1 — Single-Qubit Double-Slit Interference and Noise](Phase-1_Single-Qubit_Double-Slit_Interference_and_Noise.md), extending the analogy from single-particle to molecular-scale interference.*
