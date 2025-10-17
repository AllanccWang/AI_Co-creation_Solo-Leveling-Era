# Goal
The primary mission is to simulate a probability-based mechanical model where a key input is in a state of superposition, and to visualize the end-effector's resulting location not as a single trajectory, but as a density distribution map.

# Quests
**Side Quest 1: Probabilistic Linkage Modeling**

- **Objective:** Establish the mathematical framework for a **two-degree-of-freedom** linkage mechanism. Instead of defining a fixed input angle θ, you must model the first joint as having two possible states, θ_A and θ_B, with associated probabilities (e.g., P_A and P_B, where P_A+P_B=1).
- **Task Focus (Abstract Modeling):** Derive the kinematic equations
    
    (X, Y) = f(θ_A/B, L1, L2)
    
    for the end-effector and then apply the probability weighting to calculate the expected position **density** over a range of motion, translating the quantum superposition concept into a classical probability function.
    

**Side Quest 2: Heatmap Visualization**

- **Objective:** Create a dynamic visualization that expresses the probability density of the end-effector's location, rather than its deterministic path.
- **Task Focus (Dynamic Validation & Expression):** Utilize Matplotlib (or a similar library) to generate a **2D Heatmap** or **Contour Density Plot**. This plot must visually distinguish the regions where the end-effector is most likely to be (higher probability density/darker color) due to state θ_A versus state θ_B, effectively showing the 'spread' of the "superimposed" mechanism over time or input range.

# Result
| probabilities(Pa,Pb) | density distribution map |
| (0.1, 0.9) | density distribution map |
| (0.5, 0.5) | density distribution map |
| (0.9, 0.1) | density distribution map |